from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.message import Message
from app.models.channel import Channel, ChannelMember
from app.models.task import Task
from app.models.workspace import WorkspaceMember


def simple_search(db: Session, user_id: int, query: str) -> dict[str, list[dict[str, Any]]]:
    # Canais acessíveis
    private_channel_ids = [cm.channel_id for cm in db.query(ChannelMember).filter(ChannelMember.user_id == user_id).all()]
    public_channels = db.query(Channel).filter(Channel.is_private == False).all()
    public_ids = [c.id for c in public_channels]
    allowed_channel_ids = set(public_ids) | set(private_channel_ids)

    # Mensagens
    msgs = db.query(Message).filter(
        Message.channel_id.in_(allowed_channel_ids),
        Message.content.ilike(f"%{query}%")
    ).limit(50).all()

    # Tasks do(s) workspace(s) do user
    user_ws_ids = [m.workspace_id for m in db.query(WorkspaceMember).filter(WorkspaceMember.user_id == user_id).all()]
    tasks = db.query(Task).filter(
        Task.title.ilike(f"%{query}%")
    ).limit(50).all()

    # Simplesmente retorna sem verificação de workspace nas tasks (poderíamos ligar Task->Column->Board->Workspace)
    # Para precisão, vamos filtrar manualmente:
    filtered_tasks = []
    for t in tasks:
        board = t.column.board  # lazy load
        if board.workspace_id in user_ws_ids:
            filtered_tasks.append(t)

    return {
        "messages": [
            {
                "id": m.id,
                "channel_id": m.channel_id,
                "author_id": m.author_id,
                "snippet": m.content[:200]
            } for m in msgs
        ],
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "column_id": t.column_id,
                "assignee_id": t.assignee_id,
                "done": t.done
            } for t in filtered_tasks
        ]
    }