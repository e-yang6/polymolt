"""
Belief formation logic for agents.
Each agent reads its accessible evidence and forms a private probability estimate.

TODO: RAG — replace get_evidence() calls with CategoryRetriever.retrieve()
"""

import random
from app.agents.agent_config import AgentConfig
from app.data.evidence import EvidenceItem, get_evidence


def compute_evidence_belief(evidence_items: list[EvidenceItem]) -> tuple[float, float]:
    """
    Compute a raw belief score from evidence items.
    Returns (belief: 0–1, mean_strength: 0–1).

    Positive evidence pushes toward 1.0, negative toward 0.0, mixed is neutral.
    Weighted by strength.
    """
    if not evidence_items:
        return 0.5, 0.5

    total_weight = 0.0
    weighted_sum = 0.0

    for item in evidence_items:
        w = item["strength"]
        if item["sentiment"] == "positive":
            score = 0.5 + (item["strength"] * 0.5)   # maps to 0.5–1.0
        elif item["sentiment"] == "negative":
            score = 0.5 - (item["strength"] * 0.5)   # maps to 0.0–0.5
        else:  # mixed
            score = 0.5
        weighted_sum += score * w
        total_weight += w

    raw_belief = weighted_sum / total_weight if total_weight > 0 else 0.5
    mean_strength = total_weight / len(evidence_items)
    return raw_belief, mean_strength


def form_belief(
    agent: AgentConfig,
    region_id: str,
    prior_belief: float,
    market_price: float,
) -> tuple[float, list[EvidenceItem]]:
    """
    Agent forms a new private belief based on:
    1. Evidence from accessible categories (raw evidence belief)
    2. Prior belief (stubbornness blend)
    3. Market price (herd sensitivity nudge)

    Returns (new_belief, evidence_used).

    TODO: RAG — replace get_evidence(region_id, cat) with CategoryRetriever(cat).retrieve(region_id)
    """
    all_evidence: list[EvidenceItem] = []
    for category in agent.categories:
        items = get_evidence(region_id, category)  # TODO: RAG
        all_evidence.extend(items)

    if not all_evidence:
        return prior_belief, []

    # Add small noise to simulate real-world uncertainty
    noise = random.gauss(0, 0.03)
    raw_belief, _ = compute_evidence_belief(all_evidence)
    raw_belief = max(0.05, min(0.95, raw_belief + noise))

    # Stubbornness: blend raw belief with prior
    blended = raw_belief * (1 - agent.stubbornness) + prior_belief * agent.stubbornness

    # Herd sensitivity: nudge toward (or away from) market price
    if agent.contrarian:
        # Contrarian agents push away from market price
        herd_target = 1.0 - market_price
    else:
        herd_target = market_price

    final_belief = blended * (1 - agent.herd_sensitivity) + herd_target * agent.herd_sensitivity
    final_belief = max(0.05, min(0.95, final_belief))

    return final_belief, all_evidence
