"""
Discover and collect all agents from `app.agents.agents`.

Each module in `app.agents.agents` must define a top-level `agent: AgentConfig`.
Adding a new agent = adding a new file in that package with an `agent` export.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil
from typing import Optional

from app.agents.base import AgentConfig

logger = logging.getLogger(__name__)


def _discover_agents() -> list[AgentConfig]:
    """Import every module in `app.agents.agents` and collect its `agent`."""
    agents: list[AgentConfig] = []
    try:
        pkg = importlib.import_module("app.agents.agents")
        pkgpath = getattr(pkg, "__path__", None)
        if not pkgpath:
            return agents
        for _importer, modname, _ispkg in pkgutil.iter_modules(pkgpath, prefix="app.agents.agents."):
            if modname.endswith(".__init__"):
                continue
            try:
                mod = importlib.import_module(modname)
                a = getattr(mod, "agent", None)
                if isinstance(a, AgentConfig):
                    agents.append(a)
                else:
                    logger.warning("Module %s has no 'agent: AgentConfig'", modname)
            except Exception as e:
                logger.warning("Failed to load agent from %s: %s", modname, e)
    except Exception as e:
        logger.exception("Failed to discover agents: %s", e)
    return agents


# Discover once at import time
AGENTS: list[AgentConfig] = _discover_agents()


def get_agent(agent_id: str) -> Optional[AgentConfig]:
    """Return the agent config for the given id, or None."""
    for a in AGENTS:
        if a.id == agent_id:
            return a
    return None


def list_agents() -> list[AgentConfig]:
    """Return all defined agents."""
    return list(AGENTS)
