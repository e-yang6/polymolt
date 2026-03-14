"""
LMSR prediction-market engine and region configuration.

Uses the Logarithmic Market Scoring Rule (Hanson 2003):
    price_yes = e^(q_yes / b) / (e^(q_yes / b) + e^(q_no / b))

Each region has its own question, liquidity param *b*, and starting price.
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Region definitions
# ---------------------------------------------------------------------------

@dataclass
class Region:
    id: str
    name: str
    description: str
    question: str
    profile: str            # "sustainable" | "weak" | "contested"
    lmsr_b: float = 100.0
    starting_price: float = 0.50

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "profile": self.profile,
            "lmsr_b": self.lmsr_b,
        }


REGIONS: dict[str, Region] = {
    "scandinavia": Region(
        id="scandinavia",
        name="Scandinavia",
        description="Nordic region with strong renewable energy commitments",
        question="Will Scandinavia meet its 2030 net-zero electricity target?",
        profile="sustainable",
        lmsr_b=100.0,
        starting_price=0.72,
    ),
    "southeast_asia": Region(
        id="southeast_asia",
        name="Southeast Asia",
        description="Rapidly developing region with mixed energy policies",
        question="Will Southeast Asia reduce coal dependency by 30% by 2035?",
        profile="contested",
        lmsr_b=80.0,
        starting_price=0.35,
    ),
    "sub_saharan_africa": Region(
        id="sub_saharan_africa",
        name="Sub-Saharan Africa",
        description="Region facing climate adaptation challenges",
        question="Will Sub-Saharan Africa achieve universal energy access by 2040?",
        profile="weak",
        lmsr_b=60.0,
        starting_price=0.20,
    ),
}


# ---------------------------------------------------------------------------
# LMSR Engine
# ---------------------------------------------------------------------------

@dataclass
class MarketEngine:
    """Tracks LMSR quantities and computes prices."""

    region: Region
    q_yes: float = 0.0
    q_no: float = 0.0
    price_history: list[float] = field(default_factory=list)
    round_number: int = 0
    trade_count: int = 0
    is_running: bool = True

    def __post_init__(self) -> None:
        # Reverse-engineer starting quantities from the desired price
        # price = e^(q_yes/b) / (e^(q_yes/b) + e^(q_no/b))
        # With q_no = 0: price = e^(q_yes/b) / (e^(q_yes/b) + 1)
        # => q_yes = b * ln(price / (1 - price))
        p = max(0.01, min(0.99, self.region.starting_price))
        self.q_yes = self.region.lmsr_b * math.log(p / (1 - p))
        self.q_no = 0.0
        self.price_history = [self.current_price]

    @property
    def current_price(self) -> float:
        b = self.region.lmsr_b
        exp_y = math.exp(self.q_yes / b)
        exp_n = math.exp(self.q_no / b)
        return exp_y / (exp_y + exp_n)

    def execute_trade(self, direction: str, size: float) -> tuple[float, float]:
        """
        Execute a trade.  Returns (price_before, price_after).

        direction: "BUY" or "SELL"  (BUY = buy YES shares, SELL = buy NO shares)
        """
        price_before = self.current_price
        if direction == "BUY":
            self.q_yes += size
        else:
            self.q_no += size
        price_after = self.current_price
        self.price_history.append(price_after)
        self.trade_count += 1
        self.round_number += 1
        return price_before, price_after

    def reset(self) -> None:
        self.__post_init__()
        self.round_number = 0
        self.trade_count = 0
        self.is_running = True

    def snapshot(self) -> dict[str, Any]:
        """Return the MarketState dict the frontend expects."""
        return {
            "regionId": self.region.id,
            "question": self.region.question,
            "currentPrice": round(self.current_price, 6),
            "priceHistory": [round(p, 6) for p in self.price_history[-200:]],
            "roundNumber": self.round_number,
            "isRunning": self.is_running,
            "tradeCount": self.trade_count,
        }

    @staticmethod
    def make_trade_id() -> str:
        return str(uuid.uuid4())[:8]
