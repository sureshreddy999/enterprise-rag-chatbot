from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    top_k: int = Field(default=4, ge=1, le=20)


class SourceResponse(BaseModel):
    source: str
    page_number: int | None
    chunk_index: int | None
    score: float
    text: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]


class RetrieveRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    top_k: int = Field(default=4, ge=1, le=20)


class RetrieveResponse(BaseModel):
    sources: list[SourceResponse]
