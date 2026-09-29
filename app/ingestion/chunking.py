from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_records(
    records: list[dict[str, Any]],
    chunk_size: int,
    chunk_overlap: int,
) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    documents: list[Document] = []
    chunk_index = 0

    for record in records:
        source_doc = Document(
            page_content=record["text"],
            metadata={
                "source": record["source"],
                "page_number": record.get("page_number"),
            },
        )
        chunks = splitter.split_documents([source_doc])

        for chunk in chunks:
            chunk.metadata["chunk_index"] = chunk_index
            documents.append(chunk)
            chunk_index += 1

    return documents
