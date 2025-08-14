from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.message import MessageCreate, MessageOut
from app.models.message import Message
from app.models.channel import Channel, ChannelMember
from app.models.user import User
from app.ws.manager import manager_broadcast_message

router = APIRouter(prefix="/messages", tags=["Messages"])


def ensure_channel_access(db: Session, channel_id: int, user_id: int) -> Channel:
    ch = db.query(Channel).filter(Channel.id == channel_id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    if ch.is_private:
        is_member = db.query(ChannelMember).filter(ChannelMember.channel_id == channel_id, ChannelMember.user_id == user_id).first()
        if not is_member:
            raise HTTPException(status_code=403, detail="Acesso negado ao canal privado")
    return ch


@router.post("/", response_model=MessageOut)
def create_message(data: MessageCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ch = ensure_channel_access(db, data.channel_id, user.id)
    msg = Message(channel_id=ch.id, author_id=user.id, content=data.content, parent_id=data.parent_id)
    db.add(msg)
    db.commit()
    db.refresh(msg)

    # Notificar via WebSocket
    manager_broadcast_message(channel_id=ch.id, payload={
        "type": "message.new",
        "message": {
            "id": msg.id,
            "channel_id": msg.channel_id,
            "author_id": msg.author_id,
            "content": msg.content,
            "parent_id": msg.parent_id,
            "created_at": msg.created_at.isoformat()
        }
    })
    return msg


@router.get("/channel/{channel_id}", response_model=List[MessageOut])
def list_messages(channel_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ensure_channel_access(db, channel_id, user.id)
    return db.query(Message).filter(Message.channel_id == channel_id).order_by(Message.created_at.asc()).all()