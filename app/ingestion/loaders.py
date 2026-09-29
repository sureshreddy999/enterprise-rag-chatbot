from pathlib import Path
from typing import Any

from docx import Document as DocxDocument
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def load_file(path: str | Path) -> list[dict[str, Any]]:
    """Return page/document records with text and source metadata."""
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}")

    if suffix == ".pdf":
        reader = PdfReader(str(file_path))
        records = []
        for page_no, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                records.append(
                    {
                        "text": text,
                        "page_number": page_no,
                        "source": file_path.name,
                    }
                )
        return records

    if suffix == ".docx":
        doc = DocxDocument(str(file_path))
        text = "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
        return [{"text": text, "page_number": None, "source": file_path.name}] if text else []

    text = file_path.read_text(encoding="utf-8", errors="ignore").strip()
    return [{"text": text, "page_number": None, "source": file_path.name}] if text else []
