from functools import lru_cache
from typing import Any

from langchain_core.language_models import BaseChatModel

from app.core.config import get_settings
from app.rag.prompts import RAG_PROMPT


@lru_cache
def get_llm() -> BaseChatModel:
    settings = get_settings()

    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. Set it in .env or use LLM_PROVIDER=ollama."
            )

        from langchain_openai import ChatOpenAI

        kwargs: dict[str, Any] = {
            "model": settings.openai_model,
            "temperature": 0,
            "api_key": settings.openai_api_key,
        }
        if settings.openai_base_url:
            kwargs["base_url"] = settings.openai_base_url
        return ChatOpenAI(**kwargs)

    if settings.llm_provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0,
        )

    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")


def build_context(retrieved: list[Any]) -> str:
    blocks = []
    for index, item in enumerate(retrieved, start=1):
        doc = item.document
        meta = doc.metadata
        source = meta.get("source", "unknown")
        page = meta.get("page_number")
        location = f"page {page}" if page else f"chunk {meta.get('chunk_index', '?')}"
        blocks.append(
            f"[Source {index}] {source} ({location})\n"
            f"{doc.page_content.strip()}"
        )
    return "\n\n".join(blocks)


def generate_answer(question: str, retrieved: list[Any]) -> str:
    if not retrieved:
        return "I could not find enough information in the indexed documents to answer that."

    chain = RAG_PROMPT | get_llm()
    result = chain.invoke(
        {
            "question": question,
            "context": build_context(retrieved),
        }
    )
    return str(result.content)
