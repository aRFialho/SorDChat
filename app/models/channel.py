from __future__ import annotations
from datetime import datetime
from sqlalchemy import (
   String,
    ForeignKey,
    DateTime,
    func,
    UniqueConstraint,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Channel(Base):
        __tablename__ = "channel"
        __table_args__ = (
                UniqueConstraint("workspace_id", "name", name="uq_channel_workspace_name"),
                CheckConstraint("length(name) > 0", name="ck_channel_name_not_empty"),
                Index("ix_channel_workspace_created", "workspace_id", "created_at"),
        )
    
        id: Mapped[int] = mapped_column(primary_key=True)
        workspace_id: Mapped[int] = mapped_column(
                ForeignKey("workspace.id", ondelete="CASCADE"),
                index = True,
            nullable = False,
        )
        name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
        is_private: Mapped[bool] = mapped_column(default=False, nullable=False)
        created_at: Mapped[datetime] = mapped_column(
                DateTime(timezone=True),
                server_default = func.now(),
            nullable = False,
        )


workspace: Mapped["Workspace"] = relationship(
            "Workspace",
            back_populates = "channels",
        lazy = "selectin",
    )
    members: Mapped[list["ChannelMember"]] = relationship(
            "ChannelMember",
            back_populates = "channel",
        cascade = "all, delete-orphan",
        lazy = "selectin",
    )
    messages: Mapped[list["Message"]] = relationship(
            "Message",
            back_populates = "channel",
        cascade = "all, delete-orphan",
        lazy = "selectin",
    )




def __repr__(self) -> str:
    
    return f"Channel(id={self.id!r}, workspace_id={self.workspace_id!r}, name={self.name!r}, is_private={self.is_private!r})"


class ChannelMember(Base):
    _tablename__ = "channel_member"
    
        user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
        channel_id: Mapped[int] = mapped_column(ForeignKey("channel.id", ondelete="CASCADE"), primary_key=True)
user: Mapped["User"] = relationship("User", lazy="selectin")
    channel: Mapped["Channel"] = relationship("Channel", back_populates="members", lazy="selectin")

    def __repr__(self) -> str:
        return f"ChannelMember(user_id={self.user_id!r}, channel_id={self.channel_id!r})"