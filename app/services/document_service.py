import hashlib
import logging
import shutil
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import ChunkRecord, DocumentRecord
from app.ingestion.chunking import split_records
from app.ingestion.loaders import SUPPORTED_EXTENSIONS, load_file
from app.rag.vector_store import PersistentFAISSStore

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.store = PersistentFAISSStore()

    @staticmethod
    def sha256_file(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    def ingest(self, original_name: str, content: bytes) -> DocumentRecord:
        suffix = Path(original_name).suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {suffix}")

        file_hash = hashlib.sha256(content).hexdigest()
        existing = self.db.scalar(
            select(DocumentRecord).where(DocumentRecord.sha256 == file_hash)
        )
        if existing:
            return existing

        document_id = uuid4().hex
        safe_name = f"{document_id}{suffix}"
        destination = Path(self.settings.upload_dir) / safe_name
        destination.write_bytes(content)

        try:
            records = load_file(destination)
            chunks = split_records(
                records,
                chunk_size=self.settings.chunk_size,
                chunk_overlap=self.settings.chunk_overlap,
            )
            if not chunks:
                raise ValueError("No extractable text was found in the document.")

            for chunk in chunks:
                chunk.metadata["document_id"] = document_id
                chunk.metadata["original_filename"] = original_name

            self.store.add_documents(chunks)

            record = DocumentRecord(
                id=document_id,
                filename=original_name,
                file_type=suffix.lstrip("."),
                file_size=len(content),
                sha256=file_hash,
                chunk_count=len(chunks),
                status="indexed",
            )
            self.db.add(record)

            for chunk in chunks:
                self.db.add(
                    ChunkRecord(
                        document_id=document_id,
                        chunk_index=int(chunk.metadata["chunk_index"]),
                        page_number=chunk.metadata.get("page_number"),
                        text_preview=chunk.page_content[:500],
                    )
                )

            self.db.commit()
            return record

        except Exception:
            self.db.rollback()
            destination.unlink(missing_ok=True)
            raise

    def list_documents(self) -> list[DocumentRecord]:
        return list(
            self.db.scalars(
                select(DocumentRecord).order_by(DocumentRecord.created_at.desc())
            )
        )

    def delete(self, document_id: str) -> bool:
        record = self.db.get(DocumentRecord, document_id)
        if not record:
            return False

        self.store.remove_document(document_id)

        file_path = Path(self.settings.upload_dir) / f"{document_id}.{record.file_type}"
        file_path.unlink(missing_ok=True)

        self.db.query(ChunkRecord).filter(ChunkRecord.document_id == document_id).delete(
            synchronize_session=False
        )
        self.db.delete(record)
        self.db.commit()
        return True
