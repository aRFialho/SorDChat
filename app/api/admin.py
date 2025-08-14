from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db, require_role
from app.models.user import User, UserRole
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRole

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/workspaces", response_model=dict)
def create_workspace(name: str, owner_id: int, db: Session = Depends(get_db), _: User = Depends(require_role(UserRole.admin))):
    owner = db.query(User).filter(User.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner não encontrado")
    ws = Workspace(name=name, owner_id=owner_id)
    db.add(ws)
    db.commit()
    db.refresh(ws)
    # Owner vira membro owner
    db.add(WorkspaceMember(user_id=owner_id, workspace_id=ws.id, role=WorkspaceRole.owner))
    db.commit()
    return {"id": ws.id, "name": ws.name}


@router.post("/workspaces/{workspace_id}/add-member", response_model=dict)
def add_member(workspace_id: int, user_id: int, role: WorkspaceRole = WorkspaceRole.member, db: Session = Depends(get_db), _: User = Depends(require_role(UserRole.admin, UserRole.manager))):
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    exists = db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == user_id).first()
    if not exists:
        db.add(WorkspaceMember(user_id=user_id, workspace_id=workspace_id, role=role))
        db.commit()
    return {"message": "Membro adicionado"}