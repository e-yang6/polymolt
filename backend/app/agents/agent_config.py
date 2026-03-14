"""
Agent definitions for Polymolt. 9 agents with asymmetric knowledge and behavior traits.
Each agent is defined as a dataclass instance. State is managed separately in AppState.
"""

from dataclasses import dataclass, field
from typing import Literal

AgentType = Literal["specialist", "hybrid", "master"]


@dataclass
class AgentConfig:
    """Static agent configuration — traits and knowledge access."""
    id: str
    name: str
    agent_type: AgentType
    categories: list[str]        # corpus names this agent can access
    betting_power: float         # 1.0 specialist, 1.5 hybrid, 2.0 master

    # Behavior traits (all 0.0–1.0 unless noted)
    confidence: float            # how strongly they act on beliefs
    risk_tolerance: float        # willingness to take large positions
    stubbornness: float          # resistance to updating on price movement (higher = more resistant)
    herd_sensitivity: float      # tendency to follow market price direction
    update_frequency: float      # probability of trading in any given round (0=never, 1=always)
    contrarian: bool = False     # if True, trades against consensus direction


# ─── Category constants ────────────────────────────────────────────────────────
CLIMATE = "climate_and_emissions"
ENERGY = "energy_and_resource_systems"
WATER = "water_and_ecosystems"
INFRA = "infrastructure_and_built_environment"
SOCIAL = "economy_and_social_resilience"
GOVERNANCE = "governance_and_policy"

ALL_CATEGORIES = [CLIMATE, ENERGY, WATER, INFRA, SOCIAL, GOVERNANCE]


# ─── Agent definitions ─────────────────────────────────────────────────────────

AGENT_CONFIGS: list[AgentConfig] = [
    # ── Specialists (1.0x) ──────────────────────────────────────────────────
    AgentConfig(
        id="climate",
        name="Climate Agent",
        agent_type="specialist",
        categories=[CLIMATE],
        betting_power=1.0,
        confidence=0.85,
        risk_tolerance=0.60,
        stubbornness=0.70,
        herd_sensitivity=0.20,
        update_frequency=0.80,
    ),
    AgentConfig(
        id="energy",
        name="Energy Agent",
        agent_type="specialist",
        categories=[ENERGY],
        betting_power=1.0,
        confidence=0.80,
        risk_tolerance=0.65,
        stubbornness=0.60,
        herd_sensitivity=0.25,
        update_frequency=0.70,
    ),
    AgentConfig(
        id="water",
        name="Water & Ecosystem Agent",
        agent_type="specialist",
        categories=[WATER],
        betting_power=1.0,
        confidence=0.75,
        risk_tolerance=0.50,
        stubbornness=0.65,
        herd_sensitivity=0.30,
        update_frequency=0.75,
    ),
    AgentConfig(
        id="infrastructure",
        name="Infrastructure Agent",
        agent_type="specialist",
        categories=[INFRA],
        betting_power=1.0,
        confidence=0.70,
        risk_tolerance=0.70,
        stubbornness=0.50,
        herd_sensitivity=0.35,
        update_frequency=0.65,
    ),
    AgentConfig(
        id="social",
        name="Social Resilience Agent",
        agent_type="specialist",
        categories=[SOCIAL],
        betting_power=1.0,
        confidence=0.65,
        risk_tolerance=0.55,
        stubbornness=0.40,
        herd_sensitivity=0.50,
        update_frequency=0.60,
    ),
    AgentConfig(
        id="governance",
        name="Governance Agent",
        agent_type="specialist",
        categories=[GOVERNANCE],
        betting_power=1.0,
        confidence=0.72,
        risk_tolerance=0.60,
        stubbornness=0.55,
        herd_sensitivity=0.40,
        update_frequency=0.70,
    ),

    # ── Hybrids (1.5x) ──────────────────────────────────────────────────────
    AgentConfig(
        id="env_generalist",
        name="Environmental Generalist",
        agent_type="hybrid",
        categories=[CLIMATE, ENERGY, WATER],
        betting_power=1.5,
        confidence=0.68,
        risk_tolerance=0.70,
        stubbornness=0.35,
        herd_sensitivity=0.45,
        update_frequency=0.85,
    ),
    AgentConfig(
        id="human_generalist",
        name="Human Systems Generalist",
        agent_type="hybrid",
        categories=[INFRA, SOCIAL, GOVERNANCE],
        betting_power=1.5,
        confidence=0.65,
        risk_tolerance=0.65,
        stubbornness=0.30,
        herd_sensitivity=0.50,
        update_frequency=0.80,
    ),

    # ── Master Generalist (2.0x) ─────────────────────────────────────────────
    AgentConfig(
        id="master",
        name="Master Generalist",
        agent_type="master",
        categories=ALL_CATEGORIES,
        betting_power=2.0,
        confidence=0.60,
        risk_tolerance=0.75,
        stubbornness=0.20,
        herd_sensitivity=0.60,
        update_frequency=0.90,
    ),
]


def get_agent_config(agent_id: str) -> AgentConfig | None:
    return next((a for a in AGENT_CONFIGS if a.id == agent_id), None)
