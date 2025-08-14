from datetime import datetime
from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Channel(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspace.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    is_private: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="channels")
    members = relationship("ChannelMember", back_populates="channel", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="channel", cascade="all, delete-orphan")


class ChannelMember(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channel.id"), primary_key=True)

    user = relationship("User")
    channel = relationship("Channel", back_populates="members")