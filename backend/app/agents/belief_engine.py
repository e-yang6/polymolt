"""
Belief formation logic for agents.
Each agent reads its accessible evidence and forms a private probability estimate.

Evidence is fetched via CategoryRetriever (app.rag.retrieval), which is the
single RAG integration seam. Swap to real vector retrieval by setting
RAG_ENABLED=true in config and implementing CategoryRetriever._vector_retrieve().
"""

import random
from app.agents.agent_config import AgentConfig
from app.data.evidence import EvidenceItem
from app.rag.access import get_retrievers_for_agent


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
    momentum: float = 0.0,
) -> tuple[float, list[EvidenceItem]]:
    """
    Agent forms a new private belief based on:
    1. Evidence from accessible categories (raw evidence belief)
    2. Prior belief (stubbornness blend)
    3. Market price + momentum (herd sensitivity nudge)

    momentum: recent price trend (-0.05 to 0.05). Positive = rising market.
    High herd_sensitivity agents amplify momentum in their herd nudge.

    Evidence access goes through get_retrievers_for_agent() → CategoryRetriever.retrieve().
    This is the primary RAG integration point.

    Returns (new_belief, evidence_used).

    Evidence is retrieved via CategoryRetriever — the RAG integration point.
    To swap in real retrieval: set RAG_ENABLED=true and implement the vector
    store path in app.rag.retrieval.CategoryRetriever.retrieve().
    """
    all_evidence: list[EvidenceItem] = []
    retrievers = get_retrievers_for_agent(agent)   # access-controlled retriever list
    for retriever in retrievers:
        items = retriever.retrieve(region_id)      # TODO: RAG seam — see retrieval.py
        all_evidence.extend(items)

    if not all_evidence:
        return prior_belief, []

    # Add small noise to simulate real-world uncertainty
    noise = random.gauss(0, 0.025)
    raw_belief, _ = compute_evidence_belief(all_evidence)
    raw_belief = max(0.05, min(0.95, raw_belief + noise))

    # Stubbornness: blend raw belief with prior (belief persistence)
    blended = raw_belief * (1 - agent.stubbornness) + prior_belief * agent.stubbornness

    # Momentum-adjusted herd target:
    # High herd_sensitivity agents follow both level AND direction of market.
    # momentum is scaled and clipped to prevent runaway effects.
    momentum_nudge = momentum * agent.herd_sensitivity * 8.0  # amplify momentum signal
    momentum_nudge = max(-0.08, min(0.08, momentum_nudge))

    if agent.contrarian:
        herd_target = 1.0 - market_price - momentum_nudge
    else:
        herd_target = market_price + momentum_nudge

    herd_target = max(0.05, min(0.95, herd_target))

    final_belief = blended * (1 - agent.herd_sensitivity) + herd_target * agent.herd_sensitivity
    final_belief = max(0.05, min(0.95, final_belief))

    return final_belief, all_evidence
