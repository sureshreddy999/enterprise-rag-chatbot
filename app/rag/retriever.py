from dataclasses import dataclass

from langchain_core.documents import Document

from app.core.config import get_settings
from app.rag.vector_store import PersistentFAISSStore


@dataclass
class RetrievedChunk:
    document: Document
    score: float


class RAGRetriever:
    def __init__(self, store: PersistentFAISSStore | None = None) -> None:
        self.store = store or PersistentFAISSStore()

    def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        settings = get_settings()
        k = top_k or settings.top_k

        raw = self.store.similarity_search_with_score(query, k=k)
        results: list[RetrievedChunk] = []

        # With normalized embeddings and FAISS IndexFlatIP, larger is better.
        # For portability, the configured threshold is applied only when scores
        # are within the expected [0,1] range.
        for doc, score in raw:
            similarity = float(score)
            if 0.0 <= similarity <= 1.0 and similarity < settings.min_similarity:
                continue
            results.append(RetrievedChunk(document=doc, score=similarity))

        return results
