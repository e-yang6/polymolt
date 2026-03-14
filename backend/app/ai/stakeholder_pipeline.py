from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from app.models import generate
from app.ai.rag import retrieve
from app.ai.langflow_client import run_websearch_flow


logger = logging.getLogger(__name__)


@dataclass
class Stakeholder:
    name: str
    type: str
    description: str


@dataclass
class StakeholderAnalysis:
    stakeholder: Stakeholder
    search_query: str
    search_snippet: str
    reasoning: str


_STAKEHOLDER_SYSTEM = (
    "You are a climate and sustainability analyst. "
    "Given the user's question, identify the key stakeholders affected by the issue. "
    "Stakeholders can be people, communities, companies, NGOs, governments, or ecosystems. "
    "Return ONLY a strict JSON array of objects with fields: "
    '"name", "type", and "description". Do not include any prose before or after the JSON.'
)


def identify_stakeholders(
    message: str,
    context: Optional[str] = None,
    model: Optional[str] = None,
) -> List[Stakeholder]:
    parts = [message]
    if context:
        parts.append(f"\n\nAdditional context:\n{context}")
    user_content = "".join(parts)

    raw = generate(user_content, system_prompt=_STAKEHOLDER_SYSTEM, model=model, max_tokens=800)
    try:
        data = json.loads(raw)
    except Exception:
        logger.warning("Failed to parse stakeholders JSON; raw response: %s", raw)
        return []

    stakeholders: List[Stakeholder] = []
    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip()
            stype = str(item.get("type", "")).strip()
            desc = str(item.get("description", "")).strip()
            if name:
                stakeholders.append(Stakeholder(name=name, type=stype, description=desc))
    return stakeholders


def run_stakeholder_search(
    stakeholders: List[Stakeholder],
    message: str,
) -> List[StakeholderAnalysis]:
    analyses: List[StakeholderAnalysis] = []
    for s in stakeholders:
        search_query = f"{message} – impacts on {s.name} ({s.type})"
        snippet = run_websearch_flow(search_query, stakeholder_name=s.name)
        reasoning = (
            "Summary of websearch results relevant to this stakeholder based on Langflow output."
        )
        analyses.append(
            StakeholderAnalysis(
                stakeholder=s,
                search_query=search_query,
                search_snippet=snippet,
                reasoning=reasoning,
            )
        )
    return analyses


_SUMMARIZE_SYSTEM = (
    "You are a climate and sustainability analyst summarizing stakeholder-specific websearch results. "
    "Write a concise overview of the situation, highlighting key risks, opportunities, and trade-offs "
    "across stakeholders. Make the reasoning clear but keep the answer focused."
)


def summarize_analyses(
    message: str,
    analyses: List[StakeholderAnalysis],
    model: Optional[str] = None,
) -> str:
    if not analyses:
        return "No stakeholder-specific analyses were generated."

    lines: List[str] = [message, "\n\nStakeholder findings:\n"]
    for a in analyses:
        lines.append(
            f"- Stakeholder: {a.stakeholder.name} ({a.stakeholder.type})\n"
            f"  Search query: {a.search_query}\n"
            f"  Websearch snippet: {a.search_snippet}\n"
        )
    user_content = "".join(lines)
    return generate(user_content, system_prompt=_SUMMARIZE_SYSTEM, model=model, max_tokens=800)


def run_stakeholder_websearch_pipeline(
    message: str,
    use_rag: bool = True,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    context = retrieve(message, top_k=4) if use_rag else ""
    stakeholders = identify_stakeholders(message=message, context=context or None, model=model)

    if not stakeholders:
        return {
            "message": message,
            "stakeholders": [],
            "combined_summary": (
                "No stakeholders could be reliably identified for this question. "
                "Try rephrasing the problem with more detail about who is affected."
            ),
            "details": [],
        }

    analyses = run_stakeholder_search(stakeholders=stakeholders, message=message)
    combined_summary = summarize_analyses(message=message, analyses=analyses, model=model)

    # Convert dataclasses into dicts shaped for WebsearchResponse
    result_stakeholders = [asdict(s) for s in stakeholders]
    result_details: List[Dict[str, Any]] = []
    for a in analyses:
        result_details.append(
            {
                "stakeholder": asdict(a.stakeholder),
                "search_query": a.search_query,
                "search_snippet": a.search_snippet,
                "reasoning": a.reasoning,
            }
        )

    return {
        "message": message,
        "stakeholders": result_stakeholders,
        "combined_summary": combined_summary,
        "details": result_details,
    }

