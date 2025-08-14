from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.db.base import Base


class Workspace(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner = relationship("User")
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    channels = relationship("Channel", back_populates="workspace", cascade="all, delete-orphan")
    boards = relationship("TaskBoard", back_populates="workspace", cascade="all, delete-orphan")


class WorkspaceRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    member = "member"


class WorkspaceMember(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspace.id"), primary_key=True)
    role: Mapped[WorkspaceRole] = mapped_column(Enum(WorkspaceRole), default=WorkspaceRole.member)

    user = relationship("User", back_populates="memberships")
    workspace = relationship("Workspace", back_populates="members")