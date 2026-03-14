"""
Trade and market data models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class TradeEntry:
    id: str
    timestamp: str
    agent_id: str
    agent_name: str
    agent_type: str
    direction: Literal["BUY", "SELL"]
    size: float
    price_before: float
    price_after: float
    reasoning: str
    evidence_titles: list[str]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "agentId": self.agent_id,
            "agentName": self.agent_name,
            "agentType": self.agent_type,
            "direction": self.direction,
            "size": round(self.size, 2),
            "priceBefore": round(self.price_before, 4),
            "priceAfter": round(self.price_after, 4),
            "reasoning": self.reasoning,
            "evidenceTitles": self.evidence_titles,
        }


@dataclass
class MarketState:
    region_id: str
    question: str = "Is this region sustainable?"
    b: float = 50.0
    q_yes: float = 50.0
    q_no: float = 50.0
    price_history: list[float] = field(default_factory=list)
    trade_log: list[TradeEntry] = field(default_factory=list)
    round_number: int = 0
    is_running: bool = False

    @property
    def current_price(self) -> float:
        from app.market.lmsr import lmsr_price
        return lmsr_price(self.q_yes, self.q_no, self.b)

    @property
    def price_momentum(self) -> float:
        """
        Recent price trend as a signed float.
        Positive = rising, negative = falling. Range roughly -0.05 to 0.05.
        Computed from the last 6 price points (5 deltas).
        """
        if len(self.price_history) < 3:
            return 0.0
        window = self.price_history[-6:]
        deltas = [window[i + 1] - window[i] for i in range(len(window) - 1)]
        return sum(deltas) / len(deltas)

    def to_dict(self) -> dict:
        return {
            "regionId": self.region_id,
            "question": self.question,
            "currentPrice": round(self.current_price, 4),
            "priceHistory": [round(p, 4) for p in self.price_history],
            "priceMomentum": round(self.price_momentum, 5),
            "roundNumber": self.round_number,
            "isRunning": self.is_running,
            "tradeCount": len(self.trade_log),
        }
