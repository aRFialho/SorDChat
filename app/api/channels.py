from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.channel import ChannelCreate, ChannelUpdate, ChannelOut
from app.models.channel import Channel, ChannelMember
from app.models.workspace import Workspace, WorkspaceMember
from app.models.user import User

router = APIRouter(prefix="/channels", tags=["Channels"])


def ensure_workspace_member(db: Session, workspace_id: int, user_id: int) -> None:
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Você não pertence a este workspace")


@router.post("/", response_model=ChannelOut)
def create_channel(data: ChannelCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Confirma associação ao workspace
    ensure_workspace_member(db, data.workspace_id, user.id)
    channel = Channel(
        workspace_id=data.workspace_id,
        name=data.name,
        is_private=data.is_private
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    # Auto-add criador ao canal
    db.add(ChannelMember(user_id=user.id, channel_id=channel.id))
    db.commit()
    return channel


@router.get("/workspace/{workspace_id}", response_model=List[ChannelOut])
def list_channels(workspace_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ensure_workspace_member(db, workspace_id, user.id)
    # Se canal privado, lista apenas se membro
    private_ids = [cm.channel_id for cm in db.query(ChannelMember).filter(ChannelMember.user_id == user.id).all()]
    channels = db.query(Channel).filter(Channel.workspace_id == workspace_id).all()
    result: list[Channel] = []
    for c in channels:
        if not c.is_private or c.id in private_ids:
            result.append(c)
    return result


@router.patch("/{channel_id}", response_model=ChannelOut)
def update_channel(channel_id: int, data: ChannelUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ch = db.query(Channel).filter(Channel.id == channel_id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    ensure_workspace_member(db, ch.workspace_id, user.id)

    if data.name is not None:
        ch.name = data.name
    if data.is_private is not None:
        ch.is_private = data.is_private
    db.commit()
    db.refresh(ch)
    return ch


@router.post("/{channel_id}/join")
def join_channel(channel_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ch = db.query(Channel).filter(Channel.id == channel_id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    ensure_workspace_member(db, ch.workspace_id, user.id)

    exists = db.query(ChannelMember).filter(ChannelMember.channel_id == channel_id, ChannelMember.user_id == user.id).first()
    if not exists:
        db.add(ChannelMember(channel_id=channel_id, user_id=user.id))
        db.commit()
    return {"message": "Entrou no canal"}