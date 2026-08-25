from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    category: str
    importance: int
    pinned: bool
    created_at: datetime
    updated_at: datetime