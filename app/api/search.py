from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.services.search import simple_search

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
def search(q: str, db: Session = Depends(get_db), user=Depends(get_current_user)) -> dict[str, list[dict[str, Any]]]:
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Informe pelo menos 2 caracteres para busca")
    return simple_search(db, user_id=user.id, query=q.strip())