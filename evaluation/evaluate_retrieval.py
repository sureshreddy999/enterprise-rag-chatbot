import json
from pathlib import Path

from app.rag.retriever import RAGRetriever


def reciprocal_rank(retrieved_sources: list[str], gold: set[str]) -> float:
    for rank, source in enumerate(retrieved_sources, start=1):
        if source in gold:
            return 1.0 / rank
    return 0.0


def main() -> None:
    dataset = json.loads(Path("evaluation/dataset.json").read_text())
    retriever = RAGRetriever()

    hits = 0
    reciprocal_ranks = []

    for item in dataset:
        results = retriever.retrieve(item["question"], top_k=5)
        sources = [
            result.document.metadata.get("source")
            or result.document.metadata.get("original_filename")
            for result in results
        ]
        gold = set(item["gold_sources"])

        if any(source in gold for source in sources):
            hits += 1
        reciprocal_ranks.append(reciprocal_rank(sources, gold))

    total = len(dataset)
    hit_at_5 = hits / total if total else 0
    mrr = sum(reciprocal_ranks) / total if total else 0

    print(f"Questions: {total}")
    print(f"Hit@5:    {hit_at_5:.3f}")
    print(f"MRR:      {mrr:.3f}")


if __name__ == "__main__":
    main()
