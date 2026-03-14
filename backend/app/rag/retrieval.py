"""
CategoryRetriever — interface for evidence retrieval.
In MVP: returns seeded evidence from the data layer.

TODO: RAG — replace the seeded backend with a real vector store query.
"""

from app.data.evidence import EvidenceItem, get_evidence


class CategoryRetriever:
    """
    Retrieves evidence for a given category and region.

    TODO: RAG — replace __init__ and retrieve() with vector store client:
        self.vector_store = VectorStore(corpus_name=corpus_name)
        results = self.vector_store.query(
            embedding=embed(f"{region_id} sustainability"),
            top_k=top_k,
            filter={"corpus": self.corpus_name}
        )
    """

    def __init__(self, corpus_name: str):
        self.corpus_name = corpus_name

    def retrieve(self, region_id: str, top_k: int = 5) -> list[EvidenceItem]:
        """
        Retrieve evidence for a region and category.
        TODO: RAG — replace with vector store query.
        """
        items = get_evidence(region_id, self.corpus_name)  # TODO: RAG
        return items[:top_k]


def get_retrievers_for_agent(categories: list[str]) -> list[CategoryRetriever]:
    """
    Returns retrievers for the given category list.
    TODO: RAG — add access control enforcement here.
    """
    return [CategoryRetriever(cat) for cat in categories]
