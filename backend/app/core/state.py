"""
Global application state for Polymolt.
Holds current market, agent dynamic state, and WebSocket connections.
"""

import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from fastapi import WebSocket

from app.agents.agent_config import AgentConfig, AGENT_CONFIGS
from app.market.trade_models import MarketState, TradeEntry
from app.data.evidence import EvidenceItem


@dataclass
class AgentState:
    """Dynamic state for one agent — changes each round."""
    config: AgentConfig
    current_belief: float = 0.5
    current_position: float = 0.0   # net position (positive=long, negative=short)
    last_reasoning: str = ""
    evidence_used: list[EvidenceItem] = field(default_factory=list)
    trade_history: list[dict] = field(default_factory=list)
    belief_history: list[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.config.id,
            "name": self.config.name,
            "agentType": self.config.agent_type,
            "categories": self.config.categories,
            "bettingPower": self.config.betting_power,
            "confidence": self.config.confidence,
            "riskTolerance": self.config.risk_tolerance,
            "stubbornness": self.config.stubbornness,
            "herdSensitivity": self.config.herd_sensitivity,
            "updateFrequency": self.config.update_frequency,
            "contrarian": self.config.contrarian,
            "currentBelief": round(self.current_belief, 4),
            "currentPosition": round(self.current_position, 2),
            "lastReasoning": self.last_reasoning,
            "evidenceUsed": list(self.evidence_used),
            "tradeHistory": self.trade_history[-10:],  # last 10 trades
            "beliefHistory": [round(b, 4) for b in self.belief_history[-50:]],
        }


class AppState:
    """Singleton application state."""

    def __init__(self):
        self.market: MarketState | None = None
        self.agents: dict[str, AgentState] = {}
        self.connections: set[WebSocket] = set()
        self._init_agents()

    def _init_agents(self):
        for config in AGENT_CONFIGS:
            self.agents[config.id] = AgentState(config=config)

    def reset_for_region(self, region_id: str, b: float = 50.0):
        """Reset market and agent states for a new region."""
        self.market = MarketState(
            region_id=region_id,
            b=b,
            q_yes=b,
            q_no=b,
        )
        for agent_state in self.agents.values():
            agent_state.current_belief = 0.5
            agent_state.current_position = 0.0
            agent_state.last_reasoning = ""
            agent_state.evidence_used = []
            agent_state.trade_history = []
            agent_state.belief_history = []

    def record_trade(
        self,
        agent_state: AgentState,
        direction: str,
        size: float,
        price_before: float,
        price_after: float,
        reasoning: str,
        evidence_used: list[EvidenceItem],
    ) -> TradeEntry:
        """Record a completed trade in market state and agent history."""
        trade_id = str(uuid.uuid4())[:8]
        from datetime import datetime, timezone
        timestamp = datetime.now(timezone.utc).isoformat()

        evidence_titles = [e["title"] for e in evidence_used[:3]]

        trade = TradeEntry(
            id=trade_id,
            timestamp=timestamp,
            agent_id=agent_state.config.id,
            agent_name=agent_state.config.name,
            agent_type=agent_state.config.agent_type,
            direction=direction,
            size=size,
            price_before=price_before,
            price_after=price_after,
            reasoning=reasoning,
            evidence_titles=evidence_titles,
        )

        self.market.trade_log.append(trade)
        self.market.price_history.append(price_after)
        self.market.round_number += 1

        # Update position
        if direction == "BUY":
            agent_state.current_position += size
        else:
            agent_state.current_position -= size

        # Update trade history
        agent_state.trade_history.append(trade.to_dict())
        agent_state.belief_history.append(agent_state.current_belief)

        return trade

    def add_connection(self, ws: WebSocket):
        self.connections.add(ws)

    def remove_connection(self, ws: WebSocket):
        self.connections.discard(ws)


# Global singleton
app_state = AppState()
