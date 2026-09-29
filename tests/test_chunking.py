from app.ingestion.chunking import split_records


def test_chunking_creates_documents():
    records = [
        {
            "text": "Python is a programming language. " * 100,
            "page_number": 1,
            "source": "test.txt",
        }
    ]
    docs = split_records(records, chunk_size=100, chunk_overlap=20)
    assert len(docs) > 1
    assert all(doc.metadata["source"] == "test.txt" for doc in docs)
    assert docs[0].metadata["chunk_index"] == 0
