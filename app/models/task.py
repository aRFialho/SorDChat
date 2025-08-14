from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class TaskBoard(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspace.id"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="boards")
    columns = relationship("TaskColumn", back_populates="board", cascade="all, delete-orphan")


class TaskColumn(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    board_id: Mapped[int] = mapped_column(ForeignKey("taskboard.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0)

    board = relationship("TaskBoard", back_populates="columns")
    tasks = relationship("Task", back_populates="column", cascade="all, delete-orphan")


class Task(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    column_id: Mapped[int] = mapped_column(ForeignKey("taskcolumn.id"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True)
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    column = relationship("TaskColumn", back_populates="tasks")
    assignee = relationship("User")