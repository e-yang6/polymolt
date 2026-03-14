"""
Application configuration.
Reads from environment variables with safe defaults.

To enable real RAG or Langflow:
  RAG_ENABLED=true
  LANGFLOW_ENABLED=true
  LANGFLOW_BASE_URL=http://localhost:7860
  LANGFLOW_API_KEY=your_key_here

TODO: RAG — set RAG_ENABLED=true and configure a vector store backend.
TODO: Langflow — set LANGFLOW_ENABLED=true and point at a running Langflow instance.
"""

import os


class Config:
    # ── RAG / Retrieval ──────────────────────────────────────────────────────
    RAG_ENABLED: bool = os.getenv("RAG_ENABLED", "false").lower() == "true"
    """
    If True, CategoryRetriever will attempt real vector store queries.
    If False (default), seeded evidence from app.data.evidence is used.
    TODO: RAG — set to True once a vector store is configured.
    """

    VECTOR_STORE_URL: str = os.getenv("VECTOR_STORE_URL", "http://localhost:6333")
    """URL for vector store (e.g. Qdrant, Chroma, Weaviate). TODO: RAG"""

    EMBED_MODEL: str = os.getenv("EMBED_MODEL", "text-embedding-3-small")
    """Embedding model name for query vectorization. TODO: RAG"""

    # ── Langflow ─────────────────────────────────────────────────────────────
    LANGFLOW_ENABLED: bool = os.getenv("LANGFLOW_ENABLED", "false").lower() == "true"
    """
    If True, AgentReasoner will call Langflow workflows for LLM reasoning.
    If False (default), template-based reasoning is used.
    TODO: Langflow — set to True once Langflow workflows are deployed.
    """

    LANGFLOW_BASE_URL: str = os.getenv("LANGFLOW_BASE_URL", "http://localhost:7860")
    """Base URL for a running Langflow instance. TODO: Langflow"""

    LANGFLOW_API_KEY: str = os.getenv("LANGFLOW_API_KEY", "")
    """API key for Langflow authentication. TODO: Langflow"""

    # ── Workflow IDs ─────────────────────────────────────────────────────────
    LANGFLOW_WORKFLOW_AGENT_REASONING: str = os.getenv(
        "LANGFLOW_WORKFLOW_AGENT_REASONING", "agent_reasoning"
    )
    """Langflow workflow ID for agent reasoning generation. TODO: Langflow"""

    LANGFLOW_WORKFLOW_TRADE_DECISION: str = os.getenv(
        "LANGFLOW_WORKFLOW_TRADE_DECISION", "trade_decision"
    )
    """Langflow workflow ID for trade decision logic. TODO: Langflow"""

    # ── Simulation ────────────────────────────────────────────────────────────
    TRADE_INTERVAL_SECONDS: float = float(os.getenv("TRADE_INTERVAL", "1.2"))
    ROUND_INTERVAL_SECONDS: float = float(os.getenv("ROUND_INTERVAL", "2.0"))
    DEFAULT_REGION: str = os.getenv("DEFAULT_REGION", "scandinavia")


config = Config()
