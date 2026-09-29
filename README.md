# Enterprise Document Intelligence & RAG Chatbot

> Production-style Retrieval-Augmented Generation (RAG) application built with Python, LangChain, FAISS, Transformer embeddings, FastAPI, Streamlit, and SQL metadata storage.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-RAG-green)](https://www.langchain.com/)
[![FAISS](https://img.shields.io/badge/Vector%20DB-FAISS-orange)](https://github.com/facebookresearch/faiss)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

Enterprise Document Intelligence & RAG Chatbot lets users upload enterprise documents and ask natural-language questions grounded in those documents.

The application implements the complete RAG lifecycle:

1. Upload PDF, DOCX, or TXT documents.
2. Extract and normalize text.
3. Split text into overlapping chunks.
4. Generate Transformer-based embeddings.
5. Store vectors in a persistent FAISS index.
6. Retrieve the most relevant chunks for a question.
7. Build a grounded prompt with retrieved context.
8. Generate an answer through an LLM provider.
9. Return source documents and page/chunk metadata.
10. Persist document metadata and ingestion status in SQLite/PostgreSQL-compatible SQLAlchemy storage.

The project also includes a REST API, Streamlit interface, evaluation utilities, Docker support, tests, and an optional Ollama local-LLM path.

## Why this project is portfolio-ready

This repository intentionally demonstrates the skills commonly requested for entry-level Generative AI engineering:

- Python engineering
- NLP and text preprocessing
- Tokenization/chunking concepts
- Transformer embeddings
- Semantic search
- Vector databases
- RAG architecture
- LangChain orchestration
- LLM integration
- SQL
- FastAPI
- Git/GitHub
- Testing
- Docker
- Retrieval evaluation
- Source attribution

## Architecture

```text
                         ┌─────────────────────┐
                         │   Streamlit UI      │
                         └──────────┬──────────┘
                                    │ HTTP
                         ┌──────────▼──────────┐
                         │     FastAPI API     │
                         └───────┬─────┬───────┘
                                 │     │
                    ┌────────────┘     └──────────────┐
                    ▼                                 ▼
          ┌─────────────────┐               ┌─────────────────┐
          │ Document Service│               │  Chat Service   │
          └────────┬────────┘               └────────┬────────┘
                   │                                  │
                   ▼                                  ▼
          ┌─────────────────┐               ┌─────────────────┐
          │ PDF/DOCX/TXT    │               │ Query Embedding │
          │ extraction      │               └────────┬────────┘
          └────────┬────────┘                        │
                   ▼                                 ▼
          ┌─────────────────┐               ┌─────────────────┐
          │ Text Splitter   │               │  FAISS Search   │
          └────────┬────────┘               └────────┬────────┘
                   ▼                                 │
          ┌─────────────────┐                         │ top-k
          │ Transformer     │                         ▼
          │ Embeddings      │               ┌─────────────────┐
          └────────┬────────┘               │ Context Builder │
                   │                        └────────┬────────┘
                   ▼                                 │
          ┌─────────────────┐                         ▼
          │ Persistent FAISS│               ┌─────────────────┐
          │ Vector Store    │               │ LangChain LLM   │
          └─────────────────┘               └────────┬────────┘
                                                     │
                                                     ▼
                                           ┌─────────────────┐
                                           │ Answer + Sources│
                                           └─────────────────┘

                  ┌────────────────────────────────────┐
                  │ SQLAlchemy metadata database       │
                  │ documents / chunks / ingestion     │
                  └────────────────────────────────────┘
```

## RAG flow

```text
Document
   ↓
Loader
   ↓
Clean text
   ↓
Recursive chunking
   ↓
Embedding model
   ↓
FAISS index
   ↓
User question
   ↓
Question embedding
   ↓
Similarity search
   ↓
Top-k context
   ↓
Grounded prompt
   ↓
LLM
   ↓
Answer + citations
```

## Key engineering decisions

### 1. Why RAG instead of sending the whole document to an LLM?

RAG separates knowledge retrieval from generation. Instead of placing an entire enterprise knowledge base into every prompt, the system retrieves only the most relevant chunks.

Benefits:

- lower prompt size
- lower cost
- better grounding
- easier source attribution
- knowledge can be updated without retraining the LLM

### 2. Why FAISS?

FAISS provides fast local vector similarity search and is excellent for a portfolio project because it is:

- open source
- lightweight
- fast
- easy to persist locally
- suitable for semantic retrieval experiments

For a production deployment, the same retriever abstraction can be replaced with a managed vector database.

### 3. Why Transformer embeddings?

Keyword search can miss semantically related language.

For example:

> "How many vacation days can an employee take?"

can retrieve content containing:

> "annual paid leave entitlement"

even when the exact words do not match.

### 4. Why chunking?

LLMs have finite context windows and large documents contain irrelevant content. Chunking creates retrieval units that are small enough to search effectively while preserving local context.

### 5. Why source citations?

A RAG system should make it possible to inspect where an answer came from. Every retrieved chunk retains:

- source filename
- document ID
- page number when available
- chunk index
- retrieval score

## Features

### Document ingestion

- PDF support
- DOCX support
- TXT/Markdown support
- file validation
- SHA-256 document IDs
- duplicate detection
- metadata persistence
- chunking
- embedding
- persistent FAISS index

### Retrieval

- Transformer embeddings
- cosine-style similarity via normalized FAISS vectors
- configurable `top_k`
- configurable minimum similarity threshold
- metadata-aware source tracking

### Generation

- LangChain prompt orchestration
- OpenAI-compatible provider
- Ollama local model option
- grounded answering
- explicit "not found in the documents" behavior
- source citations

### API

- health endpoint
- document ingestion
- document listing
- document deletion
- chat endpoint
- retrieval-only endpoint
- statistics endpoint

### UI

- upload documents
- view indexed documents
- ask questions
- inspect retrieved sources
- configure top-k
- configurable similarity threshold

### Quality

- unit tests
- retrieval evaluation dataset
- precision/recall-style retrieval metrics
- smoke test
- type hints
- structured logging
- environment-based configuration

## Project structure

```text
enterprise-rag-chatbot/
├── app/
│   ├── api/
│   │   ├── main.py
│   │   └── schemas.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging_config.py
│   ├── db/
│   │   ├── models.py
│   │   └── session.py
│   ├── ingestion/
│   │   ├── loaders.py
│   │   ├── chunking.py
│   │   └── pipeline.py
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── retriever.py
│   │   ├── prompts.py
│   │   └── chain.py
│   ├── services/
│   │   ├── document_service.py
│   │   └── chat_service.py
│   └── main.py
├── frontend/
│   └── streamlit_app.py
├── evaluation/
│   ├── dataset.json
│   └── evaluate_retrieval.py
├── scripts/
│   ├── ingest_sample.py
│   └── smoke_test.py
├── tests/
│   ├── test_chunking.py
│   ├── test_config.py
│   └── test_health.py
├── data/
│   ├── documents/
│   ├── faiss/
│   └── sample/
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── LICENSE
```

## Quick start

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/enterprise-rag-chatbot.git
cd enterprise-rag-chatbot
```

### 2. Create a virtual environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

For an OpenAI-compatible provider:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4o-mini
```

Or for a local Ollama model:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

### 5. Start the API

```bash
uvicorn app.api.main:app --reload
```

API docs:

```text
http://localhost:8000/docs
```

### 6. Start the Streamlit UI

In another terminal:

```bash
streamlit run frontend/streamlit_app.py
```

Open:

```text
http://localhost:8501
```

## Ollama local setup

If you do not want to send document questions to a hosted LLM:

```bash
ollama pull llama3.2:3b
ollama serve
```

Then:

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:3b
```

The embedding model remains local as well.

## API examples

### Health

```bash
curl http://localhost:8000/health
```

### Ingest a document

```bash
curl -X POST \
  -F "file=@data/sample/employee_handbook.txt" \
  http://localhost:8000/api/v1/documents
```

### List documents

```bash
curl http://localhost:8000/api/v1/documents
```

### Ask a question

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many annual leave days are available?",
    "top_k": 4
  }'
```

### Retrieval-only debugging

```bash
curl -X POST http://localhost:8000/api/v1/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the remote work policy?",
    "top_k": 5
  }'
```

## Evaluation

A RAG system should not be evaluated only by whether the demo "looks good."

The repository includes a small retrieval evaluation utility:

```bash
python evaluation/evaluate_retrieval.py
```

It reports:

- Hit@K
- Recall@K
- Mean Reciprocal Rank

For serious evaluation, expand `evaluation/dataset.json` with domain-specific questions and gold source documents.

## Testing

```bash
pytest -q
```

## Docker

Build:

```bash
docker compose build
```

Run:

```bash
docker compose up
```

The API will be available at:

```text
http://localhost:8000
```

## Environment variables

See `.env.example`.

Important variables:

| Variable | Purpose |
|---|---|
| `LLM_PROVIDER` | `openai` or `ollama` |
| `OPENAI_API_KEY` | Hosted LLM credential |
| `OPENAI_MODEL` | OpenAI model |
| `OLLAMA_BASE_URL` | Local Ollama URL |
| `OLLAMA_MODEL` | Local Ollama model |
| `EMBEDDING_MODEL` | Sentence Transformer model |
| `CHUNK_SIZE` | Chunk character size |
| `CHUNK_OVERLAP` | Chunk overlap |
| `TOP_K` | Number of retrieved chunks |
| `MIN_SIMILARITY` | Retrieval threshold |
| `DATABASE_URL` | SQLAlchemy database |
| `FAISS_INDEX_PATH` | Persistent FAISS location |

## Security considerations

This repository is a portfolio/learning implementation, not a production security boundary.

Before production deployment, add:

- authentication and authorization
- malware scanning
- file size limits
- content-type validation
- prompt-injection defenses
- tenant isolation
- encryption at rest
- secret management
- rate limiting
- audit logging
- PII detection/redaction
- vector-store access controls
- observability and tracing

## Interview discussion points

Be prepared to explain:

### NLP

- tokenization
- stop words
- stemming vs lemmatization
- embeddings
- semantic similarity

### Transformers

- self-attention
- query/key/value
- positional information
- encoder vs decoder
- why transformers replaced many recurrent architectures

### RAG

- retrieval vs generation
- chunk size
- overlap
- top-k
- similarity threshold
- hallucination
- context windows
- grounding

### Vector databases

- vector representation
- nearest-neighbor search
- cosine similarity
- FAISS index types
- persistence
- metadata filtering

### LangChain

- documents
- embeddings
- retrievers
- prompts
- model abstraction
- chains/runnables

### Production engineering

- API design
- testing
- logging
- Docker
- SQL
- scalability
- security

## Future improvements

- hybrid BM25 + vector retrieval
- reranking with a cross-encoder
- multi-query retrieval
- parent-document retrieval
- streaming responses
- asynchronous ingestion
- background workers
- PostgreSQL + pgvector
- Redis caching
- OpenTelemetry tracing
- evaluation with RAGAS
- role-based access control
- multi-tenant document isolation

## License

MIT
