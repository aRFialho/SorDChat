from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.task import BoardCreate, BoardOut, ColumnCreate, ColumnOut, TaskCreate, TaskOut, TaskUpdate
from app.models.task import TaskBoard, TaskColumn, Task
from app.models.workspace import WorkspaceMember
from app.models.user import User

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def ensure_workspace_member(db: Session, workspace_id: int, user_id: int):
    m = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id
    ).first()
    if not m:
        raise HTTPException(status_code=403, detail="Você não pertence a este workspace")


@router.post("/boards", response_model=BoardOut)
def create_board(data: BoardCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ensure_workspace_member(db, data.workspace_id, user.id)
    b = TaskBoard(workspace_id=data.workspace_id, name=data.name)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


@router.get("/boards/{workspace_id}", response_model=List[BoardOut])
def list_boards(workspace_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ensure_workspace_member(db, workspace_id, user.id)
    return db.query(TaskBoard).filter(TaskBoard.workspace_id == workspace_id).all()


@router.post("/columns", response_model=ColumnOut)
def create_column(data: ColumnCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    board = db.query(TaskBoard).filter(TaskBoard.id == data.board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board não encontrado")
    ensure_workspace_member(db, board.workspace_id, user.id)
    col = TaskColumn(board_id=data.board_id, name=data.name, position=data.position)
    db.add(col)
    db.commit()
    db.refresh(col)
    return col


@router.post("/cards", response_model=TaskOut)
def create_task(data: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    col = db.query(TaskColumn).filter(TaskColumn.id == data.column_id).first()
    if not col:
        raise HTTPException(status_code=404, detail="Coluna não encontrada")
    board = db.query(TaskBoard).filter(TaskBoard.id == col.board_id).first()
    ensure_workspace_member(db, board.workspace_id, user.id)
    t = Task(column_id=data.column_id, title=data.title, description=data.description, assignee_id=data.assignee_id)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.get("/cards/{column_id}", response_model=List[TaskOut])
def list_tasks(column_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    col = db.query(TaskColumn).filter(TaskColumn.id == column_id).first()
    if not col:
        raise HTTPException(status_code=404, detail="Coluna não encontrada")
    board = db.query(TaskBoard).filter(TaskBoard.id == col.board_id).first()
    ensure_workspace_member(db, board.workspace_id, user.id)
    return db.query(Task).filter(Task.column_id == column_id).all()


@router.patch("/cards/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    col = db.query(TaskColumn).filter(TaskColumn.id == t.column_id).first()
    board = db.query(TaskBoard).filter(TaskBoard.id == col.board_id).first()
    ensure_workspace_member(db, board.workspace_id, user.id)

    if data.title is not None:
        t.title = data.title
    if data.description is not None:
        t.description = data.description
    if data.assignee_id is not None:
        t.assignee_id = data.assignee_id
    if data.done is not None:
        t.done = data.done
    if data.column_id is not None:
        # mover de coluna
        new_col = db.query(TaskColumn).filter(TaskColumn.id == data.column_id).first()
        if not new_col:
            raise HTTPException(status_code=404, detail="Nova coluna não encontrada")
        t.column_id = data.column_id

    db.commit()
    db.refresh(t)
    return t