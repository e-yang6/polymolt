"""
Web scraper — pure Python, no AI.

Scrapes multiple sources for hospital wait-time data and patient-experience
signals that are not typically disclosed in news coverage:
  1. DuckDuckGo Lite  — general search snippets for any query
  2. RateMDs          — Canadian hospital/doctor review pages
  3. Reddit           — community posts (r/toronto, r/askTO, r/ontario)
  4. Ontario ER       — Ontario government public ER wait-time tables
  5. Google News RSS  — targeted feed queries (consistent with notebook)
  6. Site-targeted    — DuckDuckGo searches scoped to Yelp / Healthgrades

Public API
----------
  scrape_web(query)              → ScrapeResult   (used by orchestrator)
  scrape_hospital_reviews(name)  → ScrapeResult   (hospital-focused)
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-CA,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

_TIMEOUT = 12
_MAX_PER_SOURCE = 6
_SNIPPET_MAX_LEN = 500

# Patterns that indicate a snippet is relevant to wait times / patient experience
_WAIT_PATTERN = re.compile(
    r"\b("
    r"wait(?:ed|ing|[\s\-]+time)?|"
    r"\d+[\s\-]+(?:hour|hr|minute|min)s?|"
    r"(?:ER|emergency|triage|intake|discharge|bed[\s\-]+block)|"
    r"over[\s\-]?crowd|"
    r"staff(?:ing)?[\s\-]+(?:shortage|issue|ratio)|"
    r"patient[\s\-]+(?:experience|satisfaction|complaint|ratio)|"
    r"ambulance[\s\-]+offload"
    r")\b",
    re.IGNORECASE,
)

TORONTO_HOSPITALS = [
    "Toronto General Hospital",
    "Toronto Western Hospital",
    "St. Michael's Hospital",
    "Mount Sinai Hospital",
    "Sunnybrook Hospital",
    "SickKids",
    "Humber River Hospital",
    "North York General Hospital",
    "Michael Garron Hospital",
    "Princess Margaret Cancer Centre",
    "Scarborough Health Network",
    "Trillium Health Partners",
]

_HOSPITAL_RE = re.compile(
    r"\b(hospital|ER|emergency\s+room|healthcare|wait\s+time|patient|clinic)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class ScrapeResult:
    snippets: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)

    def add(self, text: str, source: str) -> None:
        text = text.strip()
        if not text or text in self.snippets:
            return
        self.snippets.append(text[:_SNIPPET_MAX_LEN])
        self.sources.append(source)

    def extend(self, other: "ScrapeResult") -> None:
        for snippet, source in zip(other.snippets, other.sources):
            self.add(snippet, source)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get(url: str, **kwargs) -> requests.Response | None:
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT, **kwargs)
        resp.raise_for_status()
        return resp
    except Exception as exc:
        logger.warning("GET %s failed: %s", url, exc)
        return None


def _soup(resp: requests.Response) -> BeautifulSoup:
    return BeautifulSoup(resp.text, "html.parser")


# ---------------------------------------------------------------------------
# Source 1: DuckDuckGo Lite
# ---------------------------------------------------------------------------

def _ddg(query: str, max_results: int = _MAX_PER_SOURCE) -> list[str]:
    """
    Scrape DuckDuckGo Lite for organic result snippets.
    Optionally prefix the query with 'site:foo.com' to target a specific domain.
    """
    url = f"https://lite.duckduckgo.com/lite/?q={quote_plus(query)}"
    resp = _get(url)
    if resp is None:
        return []
    soup = _soup(resp)
    results: list[str] = []
    for td in soup.select("td.result-snippet")[:max_results]:
        text = td.get_text(" ", strip=True)
        if text:
            results.append(text)
    return results


# ---------------------------------------------------------------------------
# Source 2: RateMDs
# ---------------------------------------------------------------------------

def _ratemds_review_page(url: str) -> list[str]:
    resp = _get(url)
    if resp is None:
        return []
    soup = _soup(resp)
    snippets: list[str] = []
    # RateMDs review comments live in several possible containers
    selectors = [
        ".rating-comment",
        "div[class*='comment']",
        "p[class*='comment']",
        ".review-text",
        "div[class*='review']",
    ]
    for sel in selectors:
        for el in soup.select(sel)[:10]:
            text = el.get_text(" ", strip=True)
            if len(text) > 30:
                snippets.append(f"[RateMDs] {text}")
        if snippets:
            break
    return snippets[:_MAX_PER_SOURCE]


def _scrape_ratemds(hospital_name: str, city: str = "Toronto") -> list[str]:
    query = f"{hospital_name} {city}"
    search_url = f"https://www.ratemds.com/hospital/?search={quote_plus(query)}"
    resp = _get(search_url)
    if resp is None:
        # Fallback: use DuckDuckGo scoped to ratemds.com
        return _ddg(f'site:ratemds.com "{hospital_name}" reviews wait', max_results=4)
    soup = _soup(resp)
    snippets: list[str] = []
    # Collect links to individual hospital pages
    links = [
        a["href"]
        for a in soup.select("a[href*='/hospital/']")[:3]
        if a.get("href")
    ]
    for path in links:
        url = urljoin("https://www.ratemds.com", path)
        snippets.extend(_ratemds_review_page(url))
        time.sleep(0.6)
    # Also pull any visible review snippets from the search page itself
    for el in soup.select("span[class*='rating'], div[class*='listing']")[:5]:
        text = el.get_text(" ", strip=True)
        if len(text) > 30:
            snippets.append(f"[RateMDs search] {text}")
    if not snippets:
        snippets = _ddg(f'site:ratemds.com "{hospital_name}" wait time', max_results=4)
    return snippets[:_MAX_PER_SOURCE]


# ---------------------------------------------------------------------------
# Source 3: Reddit (old.reddit.com — static HTML, no JS required)
# ---------------------------------------------------------------------------

def _scrape_reddit(query: str, subreddits: list[str] | None = None) -> list[str]:
    if subreddits is None:
        subreddits = ["toronto", "askTO", "ontario", "canada"]
    snippets: list[str] = []
    for sub in subreddits[:4]:
        url = (
            f"https://old.reddit.com/r/{sub}/search"
            f"?q={quote_plus(query)}&restrict_sr=1&sort=relevance&t=year"
        )
        resp = _get(url)
        if resp is None:
            continue
        soup = _soup(resp)

        # Post titles from search results
        for a in soup.select("a.search-title, .entry a.title")[:4]:
            title = a.get_text(strip=True)
            if title:
                snippets.append(f"[Reddit r/{sub}] {title}")

        # Post self-text snippets on the search page
        for div in soup.select("div.search-result-body")[:3]:
            text = div.get_text(" ", strip=True)
            if len(text) > 40:
                snippets.append(f"[Reddit r/{sub}] {text}")

        time.sleep(0.5)
    return snippets[:_MAX_PER_SOURCE]


# ---------------------------------------------------------------------------
# Source 4: Ontario ER Wait Times (government page)
# ---------------------------------------------------------------------------

def _scrape_ontario_er() -> list[str]:
    url = "https://www.ontario.ca/page/emergency-department-wait-times"
    resp = _get(url)
    if resp is None:
        return _ddg("ontario emergency department wait times site:ontario.ca", max_results=3)
    soup = _soup(resp)
    snippets: list[str] = []
    for table in soup.select("table")[:3]:
        rows = table.select("tr")
        for row in rows[:20]:
            cells = [td.get_text(strip=True) for td in row.select("td, th")]
            if any(cells):
                line = " | ".join(c for c in cells if c)
                if line:
                    snippets.append(f"[ON Gov ER Waits] {line}")
    # Fallback to any paragraph mentioning waits
    if not snippets:
        for p in soup.select("p, li")[:15]:
            text = p.get_text(" ", strip=True)
            if _WAIT_PATTERN.search(text):
                snippets.append(f"[ON Gov ER Waits] {text}")
    return snippets[:_MAX_PER_SOURCE]


# ---------------------------------------------------------------------------
# Source 5: Google News RSS (consistent with hospital_data.ipynb approach)
# ---------------------------------------------------------------------------

def _scrape_google_news_rss(hospital_name: str, extra: str = "wait time") -> list[str]:
    try:
        import feedparser  # type: ignore
    except ImportError:
        logger.warning("feedparser not installed; skipping Google News RSS")
        return []
    query = f'"{hospital_name}" {extra}'
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-CA&gl=CA&ceid=CA:en"
    try:
        feed = feedparser.parse(url)
        snippets = []
        for entry in feed.entries[:_MAX_PER_SOURCE]:
            summary = entry.get("summary", "") or entry.get("title", "")
            text = BeautifulSoup(summary, "html.parser").get_text(" ", strip=True)
            if text:
                snippets.append(f"[Google News] {text}")
        return snippets
    except Exception as exc:
        logger.warning("Google News RSS failed for %s: %s", hospital_name, exc)
        return []


# ---------------------------------------------------------------------------
# Source 6: Site-targeted DuckDuckGo (Yelp, Healthgrades, WalkInClinics)
# ---------------------------------------------------------------------------

def _scrape_yelp_via_ddg(hospital_name: str, city: str = "Toronto") -> list[str]:
    query = f'site:yelp.ca "{hospital_name}" {city} reviews'
    return [f"[Yelp] {s}" for s in _ddg(query, max_results=4)]


def _scrape_healthgrades_via_ddg(hospital_name: str) -> list[str]:
    query = f'site:healthgrades.com "{hospital_name}" wait time patient reviews'
    return [f"[Healthgrades] {s}" for s in _ddg(query, max_results=4)]


def _scrape_walkin_via_ddg(hospital_name: str, city: str = "Toronto") -> list[str]:
    query = f'"{hospital_name}" {city} wait time patient experience -news'
    return [f"[Web] {s}" for s in _ddg(query, max_results=4)]


# ---------------------------------------------------------------------------
# Hospital-specific aggregator
# ---------------------------------------------------------------------------

def scrape_hospital_reviews(
    hospital_name: str | None = None,
    city: str = "Toronto",
) -> ScrapeResult:
    """
    Aggregate hospital wait-time and patient-experience data from review
    sites, Reddit, and official government sources.

    Parameters
    ----------
    hospital_name:
        Name of the hospital (e.g. "Toronto General Hospital").
        If None, uses a generic query for all ER departments.
    city:
        City used to narrow searches.

    Returns
    -------
    ScrapeResult with .snippets and .sources populated.
    """
    result = ScrapeResult()
    name = hospital_name or "emergency department"

    logger.info("Scraping hospital reviews for: %s, %s", name, city)

    # 1. RateMDs
    for s in _scrape_ratemds(name, city):
        result.add(s, "ratemds")

    # 2. Yelp (via DuckDuckGo)
    for s in _scrape_yelp_via_ddg(name, city):
        result.add(s, "yelp")

    # 3. Healthgrades (via DuckDuckGo)
    for s in _scrape_healthgrades_via_ddg(name):
        result.add(s, "healthgrades")

    # 4. General web (wait-time focused, news excluded)
    for s in _scrape_walkin_via_ddg(name, city):
        result.add(s, "web")

    # 5. Reddit community posts
    for s in _scrape_reddit(f"{name} wait time emergency"):
        result.add(s, "reddit")

    # 6. Ontario government ER wait times
    for s in _scrape_ontario_er():
        result.add(s, "ontario_gov")

    # 7. Google News RSS (recent coverage)
    for s in _scrape_google_news_rss(name, extra="wait time OR patient experience"):
        result.add(s, "google_news")

    logger.info("Collected %d snippets for %s", len(result.snippets), name)
    return result


def scrape_all_hospitals(city: str = "Toronto") -> dict[str, ScrapeResult]:
    """
    Scrape review data for every known Toronto hospital.
    Returns a mapping of hospital name → ScrapeResult.
    Useful for bulk data collection in the notebook.
    """
    results: dict[str, ScrapeResult] = {}
    for hospital in TORONTO_HOSPITALS:
        logger.info("Scraping: %s", hospital)
        results[hospital] = scrape_hospital_reviews(hospital, city)
        time.sleep(1.0)  # polite crawl delay between hospitals
    return results


# ---------------------------------------------------------------------------
# General entry point — called by orchestrator
# ---------------------------------------------------------------------------

def _extract_hospital_name(query: str) -> str | None:
    """Return the first matching hospital name found in a free-text query."""
    q_lower = query.lower()
    for name in TORONTO_HOSPITALS:
        if name.lower() in q_lower:
            return name
    return None


def scrape_web(query: str) -> ScrapeResult:
    """
    General-purpose web scrape for any query string.

    Always runs a DuckDuckGo search. If the query mentions hospital/
    healthcare keywords, also runs the full hospital review pipeline.

    This function is called by the orchestrator (orchestrator.py).
    """
    result = ScrapeResult()

    # General DuckDuckGo search
    for s in _ddg(query, max_results=8):
        result.add(s, "duckduckgo")

    # Hospital-specific enrichment when relevant
    if _HOSPITAL_RE.search(query):
        hospital_name = _extract_hospital_name(query)
        hospital_result = scrape_hospital_reviews(hospital_name)
        result.extend(hospital_result)

    return result
