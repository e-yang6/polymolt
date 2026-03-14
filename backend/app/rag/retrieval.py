"""
CategoryRetriever — the single point of evidence access for all agents.

Phase 3: All evidence retrieval is routed through this class.
Currently backed by seeded data in app.data.evidence.

To enable real RAG:
  1. Set RAG_ENABLED=true in environment
  2. Implement the vector store query branch below
  3. Populate corpora using scripts/ingest.py (see corpus_map.py for structure)

TODO: RAG — replace the seeded backend with a vector store query.
"""

from app.data.evidence import EvidenceItem, get_evidence
from app.core.config import config


class CategoryRetriever:
    """
    Retrieves evidence items for a given sustainability category and region.

    Seeded mode (default, RAG_ENABLED=false):
        Returns pre-written evidence from app.data.evidence.

    RAG mode (RAG_ENABLED=true):
        TODO: RAG — query a vector store filtered by corpus_name.
        Expected swap:
            embedding = embed_query(f"{region_id} sustainability {self.corpus_name}")
            results = vector_store.query(
                collection=self.corpus_name,
                vector=embedding,
                top_k=top_k,
                filter={"region_hint": region_id}   # optional regional filter
            )
            return [EvidenceItem(**r["metadata"]) for r in results]
    """

    def __init__(self, corpus_name: str):
        self.corpus_name = corpus_name

    def retrieve(self, region_id: str, top_k: int = 6) -> list[EvidenceItem]:
        """
        Return up to top_k evidence items for this corpus and region.

        TODO: RAG — replace seeded call with vector store query when RAG_ENABLED=true.
        """
        if config.RAG_ENABLED:
            # TODO: RAG — implement vector store retrieval
            # from app.rag.vector_store import query_corpus
            # return query_corpus(self.corpus_name, region_id, top_k)
            raise NotImplementedError(
                "RAG retrieval is enabled (RAG_ENABLED=true) but not yet implemented. "
                "See app/rag/retrieval.py for the integration point."
            )

        # Seeded fallback — current production path
        items = get_evidence(region_id, self.corpus_name)

        # Prepend any active shock evidence (lazy import avoids circular deps)
        try:
            from app.core.state import app_state
            shock_items = app_state.get_shock_evidence(self.corpus_name)
        except Exception:
            shock_items = []

        combined = shock_items + items
        return combined[:top_k]

    def __repr__(self) -> str:
        mode = "RAG" if config.RAG_ENABLED else "seeded"
        return f"CategoryRetriever(corpus={self.corpus_name!r}, mode={mode})"
