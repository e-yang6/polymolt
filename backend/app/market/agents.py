"""
Simulated trading agents for the prediction market.

Each agent has a private belief, risk tolerance, and trading strategy.
Agents evaluate the gap between their belief and the market price,
then trade if the divergence exceeds their threshold.
"""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvidenceItem:
    id: str
    category: str
    title: str
    summary: str
    sentiment: str       # "positive" | "negative" | "mixed"
    strength: float      # 0–1

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "title": self.title,
            "summary": self.summary,
            "sentiment": self.sentiment,
            "strength": round(self.strength, 3),
        }


@dataclass
class SimAgent:
    """One simulated market agent, matching the frontend Agent interface."""

    id: str
    name: str
    agent_type: str            # "specialist" | "hybrid" | "master"
    categories: list[str]
    betting_power: float
    confidence: float
    effective_confidence: float
    risk_tolerance: float
    max_position: float
    stubbornness: float        # how slowly the agent revises beliefs
    herd_sensitivity: float    # how much the market price pulls the belief
    update_frequency: float    # probability of acting each round
    contrarian: bool

    current_belief: float = 0.5
    current_position: float = 0.0
    last_reasoning: str = ""
    evidence_used: list[EvidenceItem] = field(default_factory=list)
    trade_history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "agentType": self.agent_type,
            "categories": self.categories,
            "bettingPower": self.betting_power,
            "confidence": round(self.confidence, 3),
            "effectiveConfidence": round(self.effective_confidence, 3),
            "riskTolerance": round(self.risk_tolerance, 3),
            "maxPosition": self.max_position,
            "stubbornness": round(self.stubbornness, 3),
            "herdSensitivity": round(self.herd_sensitivity, 3),
            "updateFrequency": round(self.update_frequency, 3),
            "contrarian": self.contrarian,
            "currentBelief": round(self.current_belief, 4),
            "currentPosition": round(self.current_position, 3),
            "lastReasoning": self.last_reasoning,
            "evidenceUsed": [e.to_dict() for e in self.evidence_used],
            "tradeHistory": self.trade_history[-20:],
            "beliefHistory": [],  # computed client-side
        }

    def update_belief(self, market_price: float) -> None:
        """Drift belief toward or away from market, with noise."""
        noise = random.gauss(0, 0.02 * (1 - self.stubbornness))

        # Herd component pulls toward market price
        herd_pull = self.herd_sensitivity * (market_price - self.current_belief)

        # Contrarians resist the herd
        if self.contrarian:
            herd_pull *= -0.5

        self.current_belief += herd_pull + noise
        self.current_belief = max(0.01, min(0.99, self.current_belief))
        self.effective_confidence = self.confidence * (
            0.8 + 0.2 * abs(self.current_belief - 0.5) * 2
        )

    def decide_trade(self, market_price: float) -> tuple[str, float] | None:
        """
        Return (direction, size) or None if the agent sits out.

        direction: "BUY" (buy YES) or "SELL" (buy NO).
        """
        if random.random() > self.update_frequency:
            return None

        gap = self.current_belief - market_price

        # Threshold scales inversely with risk tolerance
        threshold = 0.03 / max(self.risk_tolerance, 0.1)

        if abs(gap) < threshold:
            return None

        direction = "BUY" if gap > 0 else "SELL"
        size = min(
            abs(gap) * self.betting_power * self.effective_confidence * 10,
            self.max_position - abs(self.current_position),
        )

        if size <= 0:
            return None

        return direction, round(size, 3)

    def record_trade(self, trade_entry: dict[str, Any]) -> None:
        self.trade_history.append(trade_entry)
        if trade_entry["direction"] in ("BUY", "YES"):
            self.current_position += trade_entry["size"]
        else:
            self.current_position -= trade_entry["size"]


# ---------------------------------------------------------------------------
# Evidence pools (randomised per round)
# ---------------------------------------------------------------------------

_EVIDENCE_POOL: list[EvidenceItem] = [
    EvidenceItem("ev-1", "energy",  "Offshore wind expansion",          "Nordic nations announce 15 GW new offshore wind capacity by 2028.", "positive", 0.82),
    EvidenceItem("ev-2", "policy",  "EU Carbon Border Adjustment",      "CBAM phase-in accelerating; could increase costs for fossil imports.", "positive", 0.70),
    EvidenceItem("ev-3", "climate", "Arctic ice loss acceleration",     "Summer Arctic ice extent hits new record low.",                     "negative", 0.65),
    EvidenceItem("ev-4", "economy", "Green bond market growth",         "Global green bond issuance surpasses $1T annually.",                "positive", 0.60),
    EvidenceItem("ev-5", "energy",  "Coal plant retirements stall",     "Several SE Asian nations delay coal phase-out timelines.",          "negative", 0.75),
    EvidenceItem("ev-6", "policy",  "COP climate finance pledge",       "Developed nations pledge $200B in climate adaptation finance.",     "mixed",    0.55),
    EvidenceItem("ev-7", "climate", "Drought impacts on agriculture",   "Multi-year drought reduces crop yields across Sub-Saharan Africa.", "negative", 0.80),
    EvidenceItem("ev-8", "energy",  "Solar cost parity achieved",       "Solar LCOE drops below grid parity in 140+ countries.",            "positive", 0.90),
    EvidenceItem("ev-9", "economy", "Fossil fuel subsidy reform",       "Indonesia cuts fossil fuel subsidies by 40%.",                     "positive", 0.68),
    EvidenceItem("ev-10","policy",  "Grid interconnection treaty",      "Nordic-Baltic grid interconnection treaty signed.",                "positive", 0.72),
]


def pick_evidence(n: int = 2) -> list[EvidenceItem]:
    return random.sample(_EVIDENCE_POOL, min(n, len(_EVIDENCE_POOL)))


def generate_reasoning(agent: SimAgent, direction: str, evidence: list[EvidenceItem]) -> str:
    titles = ", ".join(e.title for e in evidence)
    if direction == "BUY":
        return f"{agent.name} sees upside based on: {titles}. Belief ({agent.current_belief:.0%}) exceeds market price."
    return f"{agent.name} is bearish citing: {titles}. Belief ({agent.current_belief:.0%}) below market price."


# ---------------------------------------------------------------------------
# Pre-configured agents (used for all regions)
# ---------------------------------------------------------------------------

def create_default_agents(starting_price: float) -> list[SimAgent]:
    """Create a diverse set of agents with beliefs centred around starting_price."""

    base = [
        SimAgent(
            id="agent-climate", name="Climate Analyst",
            agent_type="specialist", categories=["climate", "environment"],
            betting_power=3.0, confidence=0.85, effective_confidence=0.85,
            risk_tolerance=0.6, max_position=50, stubbornness=0.7,
            herd_sensitivity=0.15, update_frequency=0.8, contrarian=False,
            current_belief=starting_price + random.uniform(0.02, 0.12),
        ),
        SimAgent(
            id="agent-policy", name="Policy Expert",
            agent_type="specialist", categories=["policy", "governance"],
            betting_power=2.5, confidence=0.78, effective_confidence=0.78,
            risk_tolerance=0.4, max_position=40, stubbornness=0.8,
            herd_sensitivity=0.10, update_frequency=0.6, contrarian=False,
            current_belief=starting_price + random.uniform(-0.05, 0.08),
        ),
        SimAgent(
            id="agent-energy", name="Energy Specialist",
            agent_type="specialist", categories=["energy", "resources"],
            betting_power=3.5, confidence=0.90, effective_confidence=0.90,
            risk_tolerance=0.7, max_position=60, stubbornness=0.5,
            herd_sensitivity=0.20, update_frequency=0.9, contrarian=False,
            current_belief=starting_price + random.uniform(-0.08, 0.10),
        ),
        SimAgent(
            id="agent-contrarian", name="Contrarian Trader",
            agent_type="hybrid", categories=["economy", "markets"],
            betting_power=4.0, confidence=0.70, effective_confidence=0.70,
            risk_tolerance=0.9, max_position=80, stubbornness=0.3,
            herd_sensitivity=0.30, update_frequency=0.7, contrarian=True,
            current_belief=starting_price + random.uniform(-0.15, -0.02),
        ),
        SimAgent(
            id="agent-master", name="Master Aggregator",
            agent_type="master", categories=["climate", "policy", "energy", "economy"],
            betting_power=2.0, confidence=0.82, effective_confidence=0.82,
            risk_tolerance=0.5, max_position=45, stubbornness=0.6,
            herd_sensitivity=0.25, update_frequency=0.5, contrarian=False,
            current_belief=starting_price + random.uniform(-0.03, 0.06),
        ),
    ]

    # Clamp beliefs
    for a in base:
        a.current_belief = max(0.01, min(0.99, a.current_belief))

    return base
