from app.rag.chain import generate_answer
from app.rag.retriever import RAGRetriever, RetrievedChunk


class ChatService:
    def __init__(self, retriever: RAGRetriever | None = None) -> None:
        self.retriever = retriever or RAGRetriever()

    def retrieve(self, question: str, top_k: int | None = None) -> list[RetrievedChunk]:
        return self.retriever.retrieve(question, top_k=top_k)

    def answer(self, question: str, top_k: int | None = None) -> tuple[str, list[RetrievedChunk]]:
        retrieved = self.retrieve(question, top_k=top_k)
        answer = generate_answer(question, retrieved)
        return answer, retrieved
