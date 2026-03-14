"""
LMSR (Logarithmic Market Scoring Rule) market maker.
Provides bounded, continuous probability updates without a counterparty.

Reference: Hanson (2003) "Combinatorial Information Market Design"
"""

import math


def lmsr_price(q_yes: float, q_no: float, b: float) -> float:
    """
    Compute current market probability from LMSR quantities.

    P(yes) = e^(q_yes/b) / (e^(q_yes/b) + e^(q_no/b))

    This is equivalent to softmax([q_yes/b, q_no/b])[0].
    """
    # Use stable softmax to prevent overflow
    a = q_yes / b
    c = q_no / b
    max_val = max(a, c)
    exp_yes = math.exp(a - max_val)
    exp_no = math.exp(c - max_val)
    return exp_yes / (exp_yes + exp_no)


def apply_trade(
    q_yes: float,
    q_no: float,
    b: float,
    direction: str,
    size: float,
) -> tuple[float, float, float, float]:
    """
    Apply a trade and return updated state + probability.

    Returns: (new_q_yes, new_q_no, price_before, price_after)

    BUY  → increase q_yes (bullish on sustainability)
    SELL → increase q_no (bearish on sustainability)
    """
    price_before = lmsr_price(q_yes, q_no, b)

    if direction == "BUY":
        q_yes = q_yes + size
    elif direction == "SELL":
        q_no = q_no + size
    else:
        raise ValueError(f"Unknown direction: {direction}")

    price_after = lmsr_price(q_yes, q_no, b)
    return q_yes, q_no, price_before, price_after


def reset_market(b: float) -> tuple[float, float]:
    """Reset to 50/50. Returns (q_yes, q_no)."""
    return b, b
