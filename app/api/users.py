from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db, get_current_user, require_role
from app.schemas.user import UserOut, UserUpdate
from app.models.user import User, UserRole
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_role(UserRole.admin, UserRole.manager))):
    return db.query(User).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_role(UserRole.admin, UserRole.manager))):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return u


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _: User = Depends(require_role(UserRole.admin))):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if data.full_name is not None:
        u.full_name = data.full_name
    if data.password is not None:
        u.hashed_password = get_password_hash(data.password)
    if data.is_active is not None:
        u.is_active = data.is_active
    if data.role is not None:
        u.role = data.role
    db.commit()
    db.refresh(u)
    return u