"""
Template-based reasoning generation for agents.
Produces natural-language explanations for trade decisions.

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
    Generates a short, readable explanation for an agent's trade.
    Uses the top evidence items to construct a narrative.

    TODO: Langflow — replace with LLM-generated reasoning:
        return langflow_client.run_workflow("agent_reasoning", {
            "agent_id": agent.id, "evidence": evidence_used,
            "market_price": market_price, "direction": direction
        })["reasoning"]
    """
    if not evidence_used:
        return f"No evidence available. Defaulting to market price of {market_price:.0%}."

    # Sort by strength, pick top 2
    top_evidence = sorted(evidence_used, key=lambda e: e["strength"], reverse=True)[:2]

    belief_pct = f"{private_belief:.0%}"
    market_pct = f"{market_price:.0%}"
    gap = abs(private_belief - market_price)

    # Build reasoning string
    evidence_refs = " and ".join([f'"{e["title"]}"' for e in top_evidence])
    sentiment_dominant = _dominant_sentiment(evidence_used)

    if direction == "BUY":
        gap_phrase = f"I estimate sustainability at {belief_pct}, above the market's {market_pct}."
        action_phrase = _buy_phrase(sentiment_dominant, agent.agent_type)
    else:
        gap_phrase = f"I estimate sustainability at {belief_pct}, below the market's {market_pct}."
        action_phrase = _sell_phrase(sentiment_dominant, agent.agent_type)

    conviction = _conviction_phrase(gap, agent.confidence)

    return f"{action_phrase} Key evidence: {evidence_refs}. {gap_phrase} {conviction}"


def _dominant_sentiment(evidence: list[EvidenceItem]) -> str:
    counts = {"positive": 0, "negative": 0, "mixed": 0}
    for e in evidence:
        counts[e["sentiment"]] += 1
    return max(counts, key=lambda k: counts[k])


def _buy_phrase(sentiment: str, agent_type: str) -> str:
    phrases = {
        "positive": [
            "Evidence strongly supports regional sustainability.",
            "The data shows positive sustainability signals.",
            "Indicators are trending favorable.",
        ],
        "negative": [
            "Despite some negative signals, my assessment is net positive.",
            "Weighing the evidence, sustainability prospects are above market expectations.",
        ],
        "mixed": [
            "Mixed evidence, but sustainability outweighs concerns.",
            "On balance, this region is more sustainable than the market suggests.",
        ],
    }
    return random.choice(phrases.get(sentiment, phrases["mixed"]))


def _sell_phrase(sentiment: str, agent_type: str) -> str:
    phrases = {
        "negative": [
            "Evidence points to significant sustainability risks.",
            "The data reveals critical sustainability deficits.",
            "Indicators suggest this region is overvalued.",
        ],
        "positive": [
            "Despite optimistic signals, structural risks are underpriced.",
            "The market is overestimating this region's sustainability.",
        ],
        "mixed": [
            "Mixed evidence tilts negative; the market is too optimistic.",
            "Sustainability risks are not fully priced in.",
        ],
    }
    return random.choice(phrases.get(sentiment, phrases["mixed"]))


def _conviction_phrase(gap: float, confidence: float) -> str:
    if gap > 0.20 and confidence > 0.75:
        return "High conviction trade — significant gap between my assessment and market price."
    elif gap > 0.10:
        return "Moderate conviction — clear divergence from market consensus."
    else:
        return "Marginal trade — small belief-price gap but worth acting on."
