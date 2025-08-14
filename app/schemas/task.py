from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BoardCreate(BaseModel):
    workspace_id: int
    name: str


class BoardOut(BoardCreate):
    id: int

    class Config:
        from_attributes = True


class ColumnCreate(BaseModel):
    board_id: int
    name: str
    position: int = 0


class ColumnOut(ColumnCreate):
    id: int

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    column_id: int
    title: str
    description: str = ""
    assignee_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    done: Optional[bool] = None
    column_id: Optional[int] = None


class TaskOut(BaseModel):
    id: int
    column_id: int
    title: str
    description: str
    assignee_id: int | None
    done: bool
    created_at: datetime

    class Config:
        from_attributes = True