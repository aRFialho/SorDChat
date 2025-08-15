"""
Rotas para sistema de notificações
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ..utils.notifications import (
    notification_manager,
    notify_new_ticket,
    notify_ticket_assigned,
    notify_task_completed,
    notify_new_message,
    notify_system_update
)

# Importar função de verificação de token
try:
    from ..utils.auth import verify_token
except ImportError:
    import jwt

    SECRET_KEY = "sordchat_secret_key_2025"
    ALGORITHM = "HS256"


    def verify_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

router = APIRouter(prefix="/notifications", tags=["🔔 Notificações"])
security = HTTPBearer()


def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obtém usuário atual do token"""
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    return payload


# Schemas
class NotificationCreate(BaseModel):
    title: str
    message: str
    type: str = "info"
    data: Optional[Dict[str, Any]] = None


class PushSubscription(BaseModel):
    endpoint: str
    keys: Dict[str, str]


@router.get("/")
async def get_notifications(
        unread_only: bool = False,
        limit: int = 50,
        current_user=Depends(get_current_user_from_token)
):
    """📋 Lista notificações do usuário"""

    user_id = current_user.get("user_id")

    notifications = notification_manager.get_user_notifications(
        user_id=user_id,
        unread_only=unread_only,
        limit=limit
    )

    unread_count = notification_manager.get_unread_count(user_id)

    return {
        "notifications": notifications,
        "total": len(notifications),
        "unread_count": unread_count
    }


@router.get("/unread-count")
async def get_unread_count(current_user=Depends(get_current_user_from_token)):
    """🔢 Quantidade de notificações não lidas"""

    user_id = current_user.get("user_id")
    count = notification_manager.get_unread_count(user_id)

    return {"unread_count": count}


@router.post("/")
async def create_notification(
        notification_data: NotificationCreate,
        target_user_id: Optional[int] = None,
        current_user=Depends(get_current_user_from_token)
):
    """📤 Criar notificação (apenas admins podem enviar para outros usuários)"""

    user_id = current_user.get("user_id")
    access_level = current_user.get("access_level")

    # Se não especificou usuário alvo, enviar para si mesmo
    if target_user_id is None:
        target_user_id = user_id

    # Verificar permissão para enviar para outros usuários
    if target_user_id != user_id and access_level != "master":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem enviar notificações para outros usuários"
        )

    notification_id = await notification_manager.create_notification(
        user_id=target_user_id,
        title=notification_data.title,
        message=notification_data.message,
        notification_type=notification_data.type,
        data=notification_data.data
    )

    return {
        "message": "Notificação criada com sucesso",
        "notification_id": notification_id
    }


@router.post("/{notification_id}/read")
async def mark_notification_as_read(
        notification_id: str,
        current_user=Depends(get_current_user_from_token)
):
    """✅ Marcar notificação como lida"""

    user_id = current_user.get("user_id")

    success = notification_manager.mark_as_read(user_id, notification_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada"
        )

    return {"message": "Notificação marcada como lida"}


@router.post("/mark-all-read")
async def mark_all_notifications_as_read(current_user=Depends(get_current_user_from_token)):
    """✅ Marcar todas as notificações como lidas"""

    user_id = current_user.get("user_id")
    count = notification_manager.mark_all_as_read(user_id)

    return {
        "message": f"{count} notificações marcadas como lidas",
        "count": count
    }


@router.delete("/{notification_id}")
async def delete_notification(
        notification_id: str,
        current_user=Depends(get_current_user_from_token)
):
    """🗑️ Excluir notificação"""

    user_id = current_user.get("user_id")

    success = notification_manager.delete_notification(user_id, notification_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada"
        )

    return {"message": "Notificação excluída com sucesso"}


@router.post("/subscribe")
async def subscribe_to_push_notifications(
        subscription: PushSubscription,
        current_user=Depends(get_current_user_from_token)
):
    """🔔 Inscrever-se para push notifications"""

    user_id = current_user.get("user_id")

    notification_manager.subscribe_user(
        user_id=user_id,
        subscription_data=subscription.dict()
    )

    return {"message": "Inscrito para push notifications com sucesso"}


@router.delete("/unsubscribe")
async def unsubscribe_from_push_notifications(current_user=Depends(get_current_user_from_token)):
    """🔕 Cancelar inscrição de push notifications"""

    user_id = current_user.get("user_id")
    notification_manager.unsubscribe_user(user_id)

    return {"message": "Inscrição cancelada com sucesso"}


# Endpoints para testar diferentes tipos de notificação
@router.post("/test/ticket")
async def test_ticket_notification(current_user=Depends(get_current_user_from_token)):
    """🧪 Testar notificação de ticket"""

    user_id = current_user.get("user_id")
    await notify_new_ticket(user_id, "Ticket de Teste", 999)

    return {"message": "Notificação de ticket enviada"}


@router.post("/test/task")
async def test_task_notification(current_user=Depends(get_current_user_from_token)):
    """🧪 Testar notificação de task"""

    user_id = current_user.get("user_id")
    await notify_task_completed(user_id, "Task de Teste", 999)

    return {"message": "Notificação de task enviada"}


@router.post("/test/message")
async def test_message_notification(current_user=Depends(get_current_user_from_token)):
    """🧪 Testar notificação de mensagem"""

    user_id = current_user.get("user_id")
    await notify_new_message(user_id, "Sistema", "Esta é uma mensagem de teste do sistema de notificações")

    return {"message": "Notificação de mensagem enviada"}


@router.post("/broadcast")
async def broadcast_notification(
        notification_data: NotificationCreate,
        current_user=Depends(get_current_user_from_token)
):
    """📢 Enviar notificação para todos os usuários (apenas admin)"""

    access_level = current_user.get("access_level")

    if access_level != "master":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem enviar broadcasts"
        )

    # Simular envio para todos os usuários (IDs 1, 2, 3)
    user_ids = [1, 2, 3]
    sent_count = 0

    for user_id in user_ids:
        try:
            await notification_manager.create_notification(
                user_id=user_id,
                title=f"📢 {notification_data.title}",
                message=notification_data.message,
                notification_type=notification_data.type,
                data=notification_data.data
            )
            sent_count += 1
        except Exception as e:
            print(f"Erro ao enviar para usuário {user_id}: {e}")

    return {
        "message": f"Broadcast enviado para {sent_count} usuários",
        "sent_count": sent_count
    }


@router.get("/stats")
async def get_notification_stats(current_user=Depends(get_current_user_from_token)):
    """📊 Estatísticas de notificações"""

    user_id = current_user.get("user_id")

    all_notifications = notification_manager.get_user_notifications(user_id, limit=1000)
    unread_count = notification_manager.get_unread_count(user_id)

    # Contar por tipo
    type_counts = {}
    for notif in all_notifications:
        notif_type = notif['type']
        type_counts[notif_type] = type_counts.get(notif_type, 0) + 1

    return {
        "total_notifications": len(all_notifications),
        "unread_count": unread_count,
        "read_count": len(all_notifications) - unread_count,
        "by_type": type_counts,
        "recent_notifications": all_notifications[:5]
    }