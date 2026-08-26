from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


# --- Auth ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Documents ---
class DocumentOut(BaseModel):
    id: str
    filename: str
    num_chunks: str | None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Chat ---
class ChatRequest(BaseModel):
    query: str


class SourceChunk(BaseModel):
    filename: str
    chunk_index: int
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]


class ChatMessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
