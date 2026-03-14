"""
Agent config — re-exports for backward compatibility.

Agent definitions live in agents/definitions/ (one file per agent).
The registry auto-discovers them. To add an agent, add a new file there
that defines a top-level `agent: AgentConfig`.
"""

from app.agents.base import AgentConfig
from app.agents.registry import AGENTS, get_agent, list_agents

__all__ = ["AgentConfig", "AGENTS", "get_agent", "list_agents"]
