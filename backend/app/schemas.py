from pydantic import BaseModel
from typing import List


class ChatRequest(BaseModel):
    question: str


class SourceItem(BaseModel):
    source: str
    page: int | None = None
    chunk_index: int
    text: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
