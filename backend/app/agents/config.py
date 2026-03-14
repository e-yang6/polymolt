"""
Example agent config — one entry per specialized agent.
Used by the pipeline to resolve agent_type → system_prompt (and optional model).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AgentConfig:
    """Single agent definition for RAG + LLM pipeline."""
    id: str
    name: str
    system_prompt: str
    model: Optional[str] = None  # override default CHAT_MODEL for this agent
    description: str = ""


# Example agents — extend this list for more.
AGENTS: list[AgentConfig] = [
    AgentConfig(
        id="climate",
        name="Climate Analyst",
        description="Climate and sustainability focus.",
        system_prompt=(
            "You are a climate and sustainability analyst. "
            "Answer only using the provided context when available. Be concise. "
            "Cite specific evidence when possible."
        ),
        model=None,
    ),
    AgentConfig(
        id="policy",
        name="Policy Expert",
        description="Governance and policy focus.",
        system_prompt=(
            "You are a governance and policy expert. "
            "Answer based only on the context. Be precise and neutral. "
            "Distinguish between facts and interpretation."
        ),
        model=None,
    ),
    AgentConfig(
        id="regional",
        name="Regional Analyst",
        description="Regional implications focus.",
        system_prompt=(
            "You are a regional sustainability analyst. "
            "Use only the RAG context. Focus on implications for the region. "
            "Highlight local vs. global factors when relevant."
        ),
        model=None,
    ),
    AgentConfig(
        id="energy",
        name="Energy Specialist",
        description="Energy and resource systems.",
        system_prompt=(
            "You are an energy and resource systems specialist. "
            "Use only the provided context. Be concise. "
            "Focus on renewables, grid, and resource use."
        ),
        model=None,
    ),
    AgentConfig(
        id="gemini",
        name="Gemini Analyst",
        description="Same pipeline but uses Google Gemini (set GOOGLE_API_KEY).",
        system_prompt=(
            "You are a sustainability analyst. "
            "Answer only using the provided context when available. Be concise."
        ),
        model="gemini-1.5-flash",
    ),
]


def get_agent(agent_id: str) -> Optional[AgentConfig]:
    """Return the agent config for the given id, or None."""
    for a in AGENTS:
        if a.id == agent_id:
            return a
    return None


def list_agents() -> list[AgentConfig]:
    """Return all defined agents."""
    return list(AGENTS)
