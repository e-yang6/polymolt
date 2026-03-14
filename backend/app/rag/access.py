"""
Agent knowledge access control.

Controls which corpora each agent is permitted to query.
In Phase 3: access is defined entirely by agent.categories (set at config time).

Future RAG integration may add:
  - Corpus-level authentication tokens
  - Per-region access restrictions
  - Dynamic access grants based on market conditions

TODO: RAG — add corpus-level auth enforcement here when using a real vector store.
"""

from app.agents.agent_config import AgentConfig
from app.rag.retrieval import CategoryRetriever


class AgentKnowledgeGate:
    """
    Validates and returns the set of retrievers an agent is allowed to use.

    Currently trust-based: an agent's categories list is treated as authoritative.

    TODO: RAG — add server-side enforcement:
        allowed = fetch_agent_permissions(agent.id, corpus_registry)
        return [CategoryRetriever(c) for c in agent.categories if c in allowed]
    """

    def __init__(self, agent: AgentConfig):
        self.agent = agent

    def get_retrievers(self) -> list[CategoryRetriever]:
        """
        Return one CategoryRetriever per corpus the agent is permitted to access.
        TODO: RAG — add permission check before constructing retrievers.
        """
        return [CategoryRetriever(cat) for cat in self.agent.categories]

    def can_access(self, corpus_name: str) -> bool:
        """Check if agent has access to a specific corpus."""
        return corpus_name in self.agent.categories


def get_retrievers_for_agent(agent: AgentConfig) -> list[CategoryRetriever]:
    """
    Convenience function: returns all retrievers for an agent's allowed corpora.
    This is the primary access point used by belief_engine.

    TODO: RAG — AgentKnowledgeGate.get_retrievers() will enforce real permissions.
    """
    gate = AgentKnowledgeGate(agent)
    return gate.get_retrievers()
