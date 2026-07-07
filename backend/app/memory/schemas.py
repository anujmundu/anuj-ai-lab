from datetime import datetime

from pydantic import BaseModel


class MemoryCreate(BaseModel):
    content: str
    category: str = "general"
    importance: int = 1


class MemoryUpdate(BaseModel):
    content: str
    category: str
    importance: int
    pinned: bool


class MemoryResponse(BaseModel):
    id: int
    content: str
    category: str
    importance: int
    pinned: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True