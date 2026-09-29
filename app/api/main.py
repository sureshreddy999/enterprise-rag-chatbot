from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.schemas import (
    ChatRequest,
    ChatResponse,
    DocumentResponse,
    HealthResponse,
    RetrieveRequest,
    RetrieveResponse,
    SourceResponse,
)
from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.db.session import get_db, init_db
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    init_db()
    yield


app = FastAPI(
    title="Enterprise Document Intelligence & RAG Chatbot",
    version="1.0.0",
    description="Production-style RAG API using LangChain, FAISS and Transformer embeddings.",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="enterprise-rag-chatbot")


@app.get("/api/v1/documents", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    return DocumentService(db).list_documents()


@app.post("/api/v1/documents", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        return DocumentService(db).ingest(file.filename or "uploaded_document", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc


@app.delete("/api/v1/documents/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    deleted = DocumentService(db).delete(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"deleted": True, "document_id": document_id}


def _source_response(item) -> SourceResponse:
    meta = item.document.metadata
    return SourceResponse(
        source=meta.get("source") or meta.get("original_filename", "unknown"),
        page_number=meta.get("page_number"),
        chunk_index=meta.get("chunk_index"),
        score=float(item.score),
        text=item.document.page_content,
    )


@app.post("/api/v1/retrieve", response_model=RetrieveResponse)
def retrieve(request: RetrieveRequest):
    try:
        results = ChatService().retrieve(request.question, request.top_k)
        return RetrieveResponse(sources=[_source_response(x) for x in results])
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        answer, results = ChatService().answer(request.question, request.top_k)
        return ChatResponse(
            answer=answer,
            sources=[_source_response(x) for x in results],
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
