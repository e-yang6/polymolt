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


# ─── Shock event evidence ─────────────────────────────────────────────────────
# Injected temporarily by POST /market/{id}/shock — picked up by CategoryRetriever.
# Each shock lasts a configurable number of rounds, then expires automatically.

_SHOCK_NEGATIVE: dict[str, list[EvidenceItem]] = {
    "climate_and_emissions": [{
        "id": "shock_neg_clim", "category": "climate_and_emissions",
        "title": "Extreme climate event triggers emergency declaration",
        "summary": "Unprecedented flooding and heatwave reverses years of emissions progress. Emergency measures declared across the region.",
        "sentiment": "negative", "strength": 0.93,
    }],
    "energy_and_resource_systems": [{
        "id": "shock_neg_energy", "category": "energy_and_resource_systems",
        "title": "Energy grid failure exposes critical infrastructure risk",
        "summary": "Regional power outages lasting days reveal systemic fragility. Fossil fuel dependency exposed as renewables fail to cover demand.",
        "sentiment": "negative", "strength": 0.89,
    }],
    "water_and_ecosystems": [{
        "id": "shock_neg_water", "category": "water_and_ecosystems",
        "title": "Water contamination emergency declared",
        "summary": "Severe pollution event renders major water sources unsafe. Ecosystem collapse reported in key watersheds.",
        "sentiment": "negative", "strength": 0.91,
    }],
    "infrastructure_and_built_environment": [{
        "id": "shock_neg_infra", "category": "infrastructure_and_built_environment",
        "title": "Infrastructure failure following extreme weather",
        "summary": "Roads, bridges, and energy infrastructure damaged beyond immediate repair. Recovery costs projected at multi-year timescale.",
        "sentiment": "negative", "strength": 0.87,
    }],
    "economy_and_social_resilience": [{
        "id": "shock_neg_social", "category": "economy_and_social_resilience",
        "title": "Economic crisis triggers social unrest",
        "summary": "Rapid unemployment rise and food insecurity spark protests. Social safety nets under severe strain.",
        "sentiment": "negative", "strength": 0.85,
    }],
    "governance_and_policy": [{
        "id": "shock_neg_gov", "category": "governance_and_policy",
        "title": "Governance breakdown: environmental agencies suspended",
        "summary": "Key regulatory bodies defunded amid political crisis. Environmental enforcement collapses, reporting halted.",
        "sentiment": "negative", "strength": 0.90,
    }],
}

_SHOCK_POSITIVE: dict[str, list[EvidenceItem]] = {
    "climate_and_emissions": [{
        "id": "shock_pos_clim", "category": "climate_and_emissions",
        "title": "Emergency climate summit delivers binding recovery commitments",
        "summary": "International agreement accelerates net-zero targets. Carbon pricing extended and emissions monitoring fully restored.",
        "sentiment": "positive", "strength": 0.91,
    }],
    "energy_and_resource_systems": [{
        "id": "shock_pos_energy", "category": "energy_and_resource_systems",
        "title": "Massive renewable energy deployment fast-tracked",
        "summary": "Emergency investment drives rapid renewable expansion. Grid resilience significantly improved within months.",
        "sentiment": "positive", "strength": 0.88,
    }],
    "water_and_ecosystems": [{
        "id": "shock_pos_water", "category": "water_and_ecosystems",
        "title": "Water infrastructure restoration complete, ecosystems recovering",
        "summary": "International aid and domestic investment fully restore clean water access. Key watersheds show measurable recovery.",
        "sentiment": "positive", "strength": 0.90,
    }],
    "infrastructure_and_built_environment": [{
        "id": "shock_pos_infra", "category": "infrastructure_and_built_environment",
        "title": "Resilient infrastructure rebuild program launched",
        "summary": "New climate-resilient standards adopted. International funding secured for green infrastructure overhaul.",
        "sentiment": "positive", "strength": 0.86,
    }],
    "economy_and_social_resilience": [{
        "id": "shock_pos_social", "category": "economy_and_social_resilience",
        "title": "Recovery package boosts employment and social stability",
        "summary": "Green jobs initiative reduces unemployment. Social resilience metrics improve sharply with emergency support programs.",
        "sentiment": "positive", "strength": 0.84,
    }],
    "governance_and_policy": [{
        "id": "shock_pos_gov", "category": "governance_and_policy",
        "title": "Governance reforms strengthen environmental oversight",
        "summary": "Independent environmental agencies reinstated with expanded powers. Transparency and enforcement markedly improved.",
        "sentiment": "positive", "strength": 0.89,
    }],
}


@dataclass
class AgentState:
    """Dynamic state for one agent — changes each round."""
    config: AgentConfig
    current_belief: float = 0.5
    current_position: float = 0.0       # net position (positive=long, negative=short)
    effective_confidence: float = 0.0   # initialized in __post_init__
    rounds_since_trade: int = 0         # rounds elapsed without firing a trade
    last_reasoning: str = ""
    evidence_used: list[EvidenceItem] = field(default_factory=list)
    trade_history: list[dict] = field(default_factory=list)
    belief_history: list[float] = field(default_factory=list)

    def __post_init__(self):
        self.effective_confidence = self.config.confidence

    def apply_confidence_decay(self):
        """
        Decay effective_confidence each round the agent doesn't trade.
        Floors at 30% of baseline confidence.
        """
        self.rounds_since_trade += 1
        floor = self.config.confidence * 0.30
        self.effective_confidence = max(
            floor,
            self.effective_confidence - self.config.confidence_decay_rate
        )

    def refresh_confidence(self):
        """Called after a trade fires — partially restores confidence."""
        self.rounds_since_trade = 0
        # Restore toward baseline (not all the way — prevents instant reset)
        self.effective_confidence = min(
            self.config.confidence,
            self.effective_confidence + self.config.confidence_decay_rate * 3
        )

    def to_dict(self) -> dict:
        return {
            "id": self.config.id,
            "name": self.config.name,
            "agentType": self.config.agent_type,
            "categories": self.config.categories,
            "bettingPower": self.config.betting_power,
            "confidence": self.config.confidence,
            "effectiveConfidence": round(self.effective_confidence, 3),
            "riskTolerance": self.config.risk_tolerance,
            "stubbornness": self.config.stubbornness,
            "herdSensitivity": self.config.herd_sensitivity,
            "updateFrequency": self.config.update_frequency,
            "contrarian": self.config.contrarian,
            "maxPosition": self.config.max_position,
            "currentBelief": round(self.current_belief, 4),
            "currentPosition": round(self.current_position, 2),
            "lastReasoning": self.last_reasoning,
            "evidenceUsed": list(self.evidence_used),
            "tradeHistory": self.trade_history[-10:],
            "beliefHistory": [round(b, 4) for b in self.belief_history[-50:]],
        }


class AppState:
    """Singleton application state."""

    def __init__(self):
        self.market: MarketState | None = None
        self.agents: dict[str, AgentState] = {}
        self.connections: set[WebSocket] = set()
        self._shock_evidence: dict[str, list[EvidenceItem]] = {}
        self._shock_expiry_round: int = -1
        self._init_agents()

    def _init_agents(self):
        for config in AGENT_CONFIGS:
            self.agents[config.id] = AgentState(config=config)

    def reset_for_region(self, region_id: str, b: float = 50.0):
        """Reset market and agent states for a new region."""
        self._shock_evidence = {}
        self._shock_expiry_round = -1
        self.market = MarketState(
            region_id=region_id,
            b=b,
            q_yes=b,
            q_no=b,
        )
        for agent_state in self.agents.values():
            agent_state.current_belief = 0.5
            agent_state.current_position = 0.0
            agent_state.effective_confidence = agent_state.config.confidence
            agent_state.rounds_since_trade = 0
            agent_state.last_reasoning = ""
            agent_state.evidence_used = []
            agent_state.trade_history = []
            agent_state.belief_history = []

    def inject_shock(self, shock_type: str = "negative", rounds: int = 20):
        """Inject temporary strong evidence that agents will pick up for the next N rounds."""
        if shock_type == "negative":
            self._shock_evidence = _SHOCK_NEGATIVE
        else:
            self._shock_evidence = _SHOCK_POSITIVE
        current_round = self.market.round_number if self.market else 0
        self._shock_expiry_round = current_round + rounds

    def clear_shock(self):
        """Remove all active shock evidence."""
        self._shock_evidence = {}
        self._shock_expiry_round = -1

    def get_shock_evidence(self, category: str) -> list[EvidenceItem]:
        """Return active shock items for a category, or [] if expired/inactive."""
        if not self._shock_evidence:
            return []
        current_round = self.market.round_number if self.market else 0
        if current_round >= self._shock_expiry_round:
            self._shock_evidence = {}  # auto-expire
            return []
        return self._shock_evidence.get(category, [])

    @property
    def shock_active(self) -> bool:
        """True if a shock event is currently active."""
        if not self._shock_evidence:
            return False
        current_round = self.market.round_number if self.market else 0
        return current_round < self._shock_expiry_round

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

        # Refresh confidence after firing a trade
        agent_state.refresh_confidence()

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
