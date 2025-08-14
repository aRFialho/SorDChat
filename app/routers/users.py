from fastapi import APIRouter

router = APIRouter()

@router.get("/", summary="Lista usuários")
async def list_users():
    return [{"id": 1, "name": "Alice"}]

@router.get("/{user_id}", summary="Detalha usuário")
async def get_user(user_id: int):
    return {"id": user_id, "name": f"User {user_id}"}