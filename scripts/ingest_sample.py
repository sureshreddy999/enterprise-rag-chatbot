from pathlib import Path

from app.db.session import SessionLocal, init_db
from app.services.document_service import DocumentService


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        service = DocumentService(db)
        for path in Path("data/sample").glob("*"):
            if path.suffix.lower() in {".pdf", ".docx", ".txt", ".md"}:
                record = service.ingest(path.name, path.read_bytes())
                print(f"Indexed: {record.filename} ({record.chunk_count} chunks)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
