from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str = Field(min_length=1, max_length=128)


class ChatResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    route: str
