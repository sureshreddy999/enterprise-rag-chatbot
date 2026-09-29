from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "Enterprise RAG Chatbot"
    app_env: str = "development"
    log_level: str = "INFO"

    llm_provider: Literal["openai", "ollama"] = "openai"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str | None = None

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    chunk_size: int = Field(default=900, ge=200, le=5000)
    chunk_overlap: int = Field(default=150, ge=0, le=1000)
    top_k: int = Field(default=4, ge=1, le=20)
    min_similarity: float = Field(default=0.20, ge=0.0, le=1.0)

    database_url: str = "sqlite:///./data/rag.db"
    faiss_index_path: str = "./data/faiss"
    upload_dir: str = "./data/documents"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def ensure_directories(self) -> None:
        Path(self.faiss_index_path).mkdir(parents=True, exist_ok=True)
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)
        if self.database_url.startswith("sqlite:///"):
            db_path = Path(self.database_url.removeprefix("sqlite:///"))
            db_path.parent.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
