"""
Template-based reasoning generation for agents.
Phase 2: Stronger templates that cite specific evidence with strength values,
compare exact belief vs market price, and vary by agent type and domain.

TODO: Langflow — replace template_reason() with LangflowClient.run_workflow("agent_reasoning", ...)
"""

import random
from app.agents.agent_config import AgentConfig
from app.data.evidence import EvidenceItem


def template_reason(
    agent: AgentConfig,
    evidence_used: list[EvidenceItem],
    private_belief: float,
    market_price: float,
    direction: str,
    trade_size: float,
) -> str:
    """
    Generates a specific, readable explanation for an agent's trade.
    Cites top evidence by title and strength. Compares belief to market price.

    TODO: Langflow — replace with:
        return langflow_client.run_workflow("agent_reasoning", {
            "agent_id": agent.id, "evidence": evidence_used,
            "market_price": market_price, "direction": direction,
            "belief": private_belief
        })["reasoning"]
    """
    if not evidence_used:
        return (
            f"No evidence available in my domain. "
            f"Market at {market_price:.0%}; holding position."
        )

    # Sort by strength descending, pick top 2
    top = sorted(evidence_used, key=lambda e: e["strength"], reverse=True)[:2]

    belief_pct = f"{private_belief:.1%}"
    market_pct = f"{market_price:.1%}"
    gap = abs(private_belief - market_price)
    dominant = _dominant_sentiment(evidence_used)
    action = "buying" if direction == "BUY" else "selling"

    # Evidence citation
    evidence_str = _cite_evidence(top)

    # Domain voice — phrasing varies by agent type
    domain_voice = _domain_opener(agent, dominant, direction)

    # Gap assessment
    gap_str = _gap_assessment(gap, agent.confidence, direction, belief_pct, market_pct)

    # Conviction qualifier
    conviction = _conviction(gap, agent.confidence, agent.stubbornness)

    return f"{domain_voice} {evidence_str} {gap_str} {conviction} {action.capitalize()} {trade_size:.1f} units."


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _cite_evidence(items: list[EvidenceItem]) -> str:
    """Format top evidence as a citation string with strength."""
    parts = []
    for item in items:
        strength_label = "strong" if item["strength"] >= 0.80 else "moderate" if item["strength"] >= 0.60 else "weak"
        sentiment_adj = {"positive": "supports", "negative": "challenges", "mixed": "complicates"}[item["sentiment"]]
        parts.append(f'"{item["title"]}" ({strength_label}, {item["strength"]:.0%}) {sentiment_adj} sustainability')
    return "Evidence: " + "; ".join(parts) + "."


def _dominant_sentiment(evidence: list[EvidenceItem]) -> str:
    counts: dict[str, float] = {"positive": 0.0, "negative": 0.0, "mixed": 0.0}
    for e in evidence:
        counts[e["sentiment"]] += e["strength"]
    return max(counts, key=lambda k: counts[k])


def _domain_opener(agent: AgentConfig, dominant: str, direction: str) -> str:
    """Opening sentence that reflects agent domain and evidence tone."""
    openers_by_type = {
        "specialist": {
            "BUY": {
                "positive": [
                    f"Within my domain, the evidence is clear:",
                    f"My specialized data points strongly positive:",
                    f"Domain indicators are favorable:",
                ],
                "negative": [
                    f"Despite negative signals in my domain, the net assessment is above market:",
                    f"Weighing the negatives carefully, I still see underpricing:",
                ],
                "mixed": [
                    f"Mixed domain signals, but the balance tips above market price:",
                    f"My evidence is split, but net sustainability exceeds what the market implies:",
                ],
            },
            "SELL": {
                "negative": [
                    f"My domain reveals critical deficiencies:",
                    f"The data in my coverage area is unambiguous:",
                    f"Specialist insight shows significant underperformance:",
                ],
                "positive": [
                    f"Despite superficially positive signals, structural risks are underpriced:",
                    f"The optimism in my domain is not warranted by fundamentals:",
                ],
                "mixed": [
                    f"The mixed evidence in my domain tilts toward risk:",
                    f"Market is too optimistic given the uncertainty I see:",
                ],
            },
        },
        "hybrid": {
            "BUY": {
                "positive": ["Across my three domains, the picture is net positive:"],
                "negative": ["My cross-domain view shows the market is underweighting positives:"],
                "mixed": ["Synthesizing my domains, sustainability is undervalued here:"],
            },
            "SELL": {
                "negative": ["Across my domains, the sustainability case is weak:"],
                "positive": ["Despite some positives, my cross-domain read is bearish:"],
                "mixed": ["The cross-domain synthesis points to overvaluation:"],
            },
        },
        "master": {
            "BUY": {
                "positive": ["Full-spectrum analysis supports higher probability:"],
                "negative": ["Even with negative signals across domains, aggregate view is bullish:"],
                "mixed": ["Integrating all six categories, market is underpriced:"],
            },
            "SELL": {
                "negative": ["Full-spectrum view reveals systematic sustainability gaps:"],
                "positive": ["Despite pockets of strength, aggregate evidence doesn't support current price:"],
                "mixed": ["Holistic assessment: the region is overpriced on sustainability:"],
            },
        },
    }
    pool = openers_by_type.get(agent.agent_type, openers_by_type["specialist"])
    direction_pool = pool.get(direction, {})
    candidates = direction_pool.get(dominant, direction_pool.get("mixed", ["Assessing available data:"]))
    return random.choice(candidates)


def _gap_assessment(gap: float, confidence: float, direction: str, belief_pct: str, market_pct: str) -> str:
    verb = "above" if direction == "BUY" else "below"
    if gap > 0.20:
        return (
            f"I estimate sustainability at {belief_pct} — {verb} the market's {market_pct}. "
            f"This {gap:.0%} gap is substantial and demands action."
        )
    elif gap > 0.10:
        return (
            f"My estimate is {belief_pct}; market says {market_pct}. "
            f"A {gap:.0%} divergence justifies a trade."
        )
    else:
        return (
            f"I'm at {belief_pct} vs market's {market_pct}. "
            f"Small gap of {gap:.0%}, but within my conviction threshold."
        )


def _conviction(gap: float, confidence: float, stubbornness: float) -> str:
    if gap > 0.20 and confidence >= 0.75:
        return "High conviction."
    elif gap > 0.10 or (stubbornness > 0.55 and gap > 0.05):
        return "Moderate conviction."
    else:
        return "Low conviction — monitoring closely."
