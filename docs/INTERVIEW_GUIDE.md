# Interview Guide

## 60-second project explanation

"I built an enterprise document intelligence assistant using a Retrieval-Augmented Generation architecture. Documents are parsed and split into overlapping chunks, transformed into normalized Transformer embeddings, and persisted in a FAISS vector index. For each user question, the system performs semantic retrieval, constructs a grounded prompt with the top relevant chunks, and sends that context to an LLM through LangChain. The API is implemented with FastAPI, document metadata is stored in SQLAlchemy, and a Streamlit UI provides document upload and source-aware answers."

## Explain RAG

RAG has two major phases:

1. Retrieval: find relevant knowledge from an external corpus.
2. Generation: give that knowledge to an LLM so it can produce a natural-language answer.

## Explain embeddings

An embedding is a dense numerical representation of text. Semantically similar text tends to occupy nearby regions of the embedding space.

## Explain FAISS

FAISS is a library for efficient similarity search over vectors. This project uses normalized embeddings so inner-product similarity behaves like cosine similarity.

## Explain chunk overlap

Overlap prevents important information near a chunk boundary from being separated too aggressively.

## Explain hallucination mitigation

The prompt instructs the LLM to answer only from retrieved context and explicitly state when the context is insufficient. Source citations make the retrieved evidence inspectable.

## Explain production improvements

For a larger system I would consider:

- PostgreSQL + pgvector
- hybrid lexical/vector retrieval
- cross-encoder reranking
- background ingestion workers
- object storage
- authentication
- tenant isolation
- prompt-injection detection
- tracing and evaluation
- automated regression datasets
