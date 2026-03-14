"""
Trade decision logic for agents.
Computes direction, size, and whether to trade at all.
Phase 2: uses effective_confidence and enforces position limits.
"""

import random
from app.agents.agent_config import AgentConfig
from app.data.evidence import EvidenceItem

# Minimum belief-price gap to bother trading
MIN_GAP_TO_TRADE = 0.025

# Base trade unit — scales with betting power, confidence, etc.
BASE_TRADE_UNIT = 10.0

# How close to max_position (as fraction) before trade is scaled down
POSITION_DAMPEN_THRESHOLD = 0.75


def compute_trade(
    agent: AgentConfig,
    private_belief: float,
    market_price: float,
    evidence_used: list[EvidenceItem],
    effective_confidence: float,
    current_position: float,
) -> tuple[str | None, float]:
    """
    Returns (direction, size) or (None, 0) if agent skips this round.

    Direction: "BUY" means agent thinks market should be higher (bullish).
               "SELL" means agent thinks market should be lower (bearish).

    Uses effective_confidence (decayed from baseline) for size.
    Enforces max_position to prevent monopolization.
    """
    # Check update frequency
    if random.random() > agent.update_frequency:
        return None, 0.0

    belief_gap = private_belief - market_price
    if abs(belief_gap) < MIN_GAP_TO_TRADE:
        return None, 0.0

    direction = "BUY" if belief_gap > 0 else "SELL"

    # Position limit check — block trade if at or beyond cap in trade direction
    if direction == "BUY" and current_position >= agent.max_position:
        return None, 0.0
    if direction == "SELL" and current_position <= -agent.max_position:
        return None, 0.0

    # Evidence factor
    if evidence_used:
        evidence_factor = sum(e["strength"] for e in evidence_used) / len(evidence_used)
    else:
        evidence_factor = 0.5

    # Trade size — uses effective_confidence (decayed), not baseline confidence
    raw_size = (
        agent.betting_power
        * effective_confidence           # Phase 2: decayed confidence
        * agent.risk_tolerance
        * abs(belief_gap)
        * evidence_factor
        * BASE_TRADE_UNIT
    )

    # Scale down as position approaches the cap (position dampening)
    position_ratio = abs(current_position) / agent.max_position
    if position_ratio > POSITION_DAMPEN_THRESHOLD:
        # Linearly reduce trade size as we approach the limit
        dampen = 1.0 - (position_ratio - POSITION_DAMPEN_THRESHOLD) / (1.0 - POSITION_DAMPEN_THRESHOLD)
        raw_size *= max(0.1, dampen)

    noise_factor = random.uniform(0.85, 1.15)
    size = max(0.5, raw_size * noise_factor)

    return direction, round(size, 2)
