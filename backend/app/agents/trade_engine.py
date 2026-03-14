"""
Trade decision logic for agents.
Computes direction, size, and whether to trade at all.
"""

import random
from app.agents.agent_config import AgentConfig
from app.data.evidence import EvidenceItem

# Minimum belief-price gap to bother trading
MIN_GAP_TO_TRADE = 0.025

# Base trade unit — scales with betting power, confidence, etc.
BASE_TRADE_UNIT = 10.0


def compute_trade(
    agent: AgentConfig,
    private_belief: float,
    market_price: float,
    evidence_used: list[EvidenceItem],
) -> tuple[str | None, float]:
    """
    Returns (direction, size) or (None, 0) if agent skips this round.

    Direction: "BUY" means agent thinks market should be higher (bullish).
               "SELL" means agent thinks market should be lower (bearish).

    Size is in LMSR quantity units.
    """
    # Check update frequency: agents don't trade every round
    if random.random() > agent.update_frequency:
        return None, 0.0

    belief_gap = private_belief - market_price

    # Skip if gap is too small
    if abs(belief_gap) < MIN_GAP_TO_TRADE:
        return None, 0.0

    direction = "BUY" if belief_gap > 0 else "SELL"

    # Evidence factor: how strong is the underlying evidence?
    if evidence_used:
        evidence_factor = sum(e["strength"] for e in evidence_used) / len(evidence_used)
    else:
        evidence_factor = 0.5

    # Trade size formula
    # betting_power × confidence × risk_tolerance × |gap| × evidence_factor × BASE_UNIT
    raw_size = (
        agent.betting_power
        * agent.confidence
        * agent.risk_tolerance
        * abs(belief_gap)
        * evidence_factor
        * BASE_TRADE_UNIT
    )

    # Add small noise to prevent perfectly deterministic sizes
    noise_factor = random.uniform(0.85, 1.15)
    size = max(0.5, raw_size * noise_factor)

    return direction, round(size, 2)
