"""
Base agent type for the RAG + LLM pipeline.
Each agent is defined in its own file under agents/definitions/.
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
