from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(username: str, password: str):
    # Exemplo simples (não use em prod)
    return {"message": f"Welcome, {username}!"}
