from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    channel_id: int
    content: str
    parent_id: Optional[int] = None


class MessageOut(BaseModel):
    id: int
    channel_id: int
    author_id: int
    content: str
    parent_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True