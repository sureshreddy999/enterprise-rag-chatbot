import json
import logging
import shutil
from pathlib import Path
from threading import RLock
from typing import Any

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.core.config import get_settings
from app.rag.embeddings import get_embeddings

logger = logging.getLogger(__name__)


class PersistentFAISSStore:
    """Thread-safe wrapper around a persistent FAISS index."""

    def __init__(self) -> None:
        settings = get_settings()
        self.path = Path(settings.faiss_index_path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.index_name = "enterprise_rag"
        self.lock = RLock()

    @property
    def index_file(self) -> Path:
        return self.path / f"{self.index_name}.faiss"

    @property
    def metadata_file(self) -> Path:
        return self.path / f"{self.index_name}.pkl"

    @property
    def manifest_file(self) -> Path:
        return self.path / "manifest.json"

    def exists(self) -> bool:
        return self.index_file.exists() and self.metadata_file.exists()

    def _load(self) -> FAISS:
        if not self.exists():
            raise FileNotFoundError("FAISS index does not exist. Ingest a document first.")

        return FAISS.load_local(
            str(self.path),
            get_embeddings(),
            index_name=self.index_name,
            allow_dangerous_deserialization=True,
        )

    def add_documents(self, documents: list[Document]) -> None:
        if not documents:
            return

        with self.lock:
            if self.exists():
                store = self._load()
                store.add_documents(documents)
            else:
                store = FAISS.from_documents(documents, get_embeddings())

            store.save_local(str(self.path), index_name=self.index_name)
            self._update_manifest(len(documents))

    def similarity_search_with_score(self, query: str, k: int) -> list[tuple[Document, float]]:
        with self.lock:
            store = self._load()
            return store.similarity_search_with_score(query, k=k)

    def remove_document(self, document_id: str) -> None:
        """Rebuild the index excluding all chunks for a document.

        FAISS deletion semantics differ across index types; rebuilding is explicit
        and reliable for this small portfolio implementation.
        """
        with self.lock:
            if not self.exists():
                return

            store = self._load()
            remaining = [
                doc
                for doc in store.docstore._dict.values()
                if doc.metadata.get("document_id") != document_id
            ]

            if not remaining:
                self.clear()
                return

            new_store = FAISS.from_documents(remaining, get_embeddings())
            new_store.save_local(str(self.path), index_name=self.index_name)
            self._write_manifest_from_documents(remaining)

    def clear(self) -> None:
        with self.lock:
            for path in self.path.glob(f"{self.index_name}.*"):
                path.unlink(missing_ok=True)
            self.manifest_file.unlink(missing_ok=True)

    def _update_manifest(self, added: int) -> None:
        data = {"chunks_added_last_operation": added}
        self.manifest_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _write_manifest_from_documents(self, docs: list[Document]) -> None:
        data = {"chunks_in_index": len(docs)}
        self.manifest_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
