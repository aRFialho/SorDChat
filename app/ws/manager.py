import asyncio
import json
from typing import Dict, Set
from starlette.websockets import WebSocket, WebSocketDisconnect
from fastapi import APIRouter, WebSocket

from app.core.config import settings

router = APIRouter()

# Conexões em memória (canal_id -> set de websockets)
_channels_connections: Dict[int, Set[WebSocket]] = {}
_broadcast_queue: "asyncio.Queue[tuple[int, dict]]" = asyncio.Queue()

# Opcional: se REDIS_URL, podemos integrar Redis Pub/Sub
_redis = None
if settings.REDIS_URL:
    try:
        import redis.asyncio as aioredis  # type: ignore
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    except Exception:
        _redis = None


async def _broadcast_worker():
    while True:
        channel_id, payload = await _broadcast_queue.get()
        # Broadcast local
        conns = _channels_connections.get(channel_id, set()).copy()
        message = json.dumps(payload)
        for ws in conns:
            try:
                await ws.send_text(message)
            except Exception:
                pass
        # Broadcast Redis (se configurado)
        if _redis:
            try:
                await _redis.publish(f"sordchat:channel:{channel_id}", message)
            except Exception:
                pass


# Inicia worker global
_worker_task: asyncio.Task | None = None
def ensure_worker_running():
    global _worker_task
    if _worker_task is None or _worker_task.done():
        _worker_task = asyncio.create_task(_broadcast_worker())


def manager_broadcast_message(channel_id: int, payload: dict):
    ensure_worker_running()
    # Coloca na fila para envio assíncrono
    try:
        _broadcast_queue.put_nowait((channel_id, payload))
    except Exception:
        pass


@router.websocket("/ws/{channel_id}")
async def websocket_endpoint(websocket: WebSocket, channel_id: int):
    await websocket.accept()
    _channels_connections.setdefault(channel_id, set()).add(websocket)

    # Se houver Redis, assina o canal
    redis_pubsub = None
    if _redis:
        redis_pubsub = _redis.pubsub()
        await redis_pubsub.subscribe(f"sordchat:channel:{channel_id}")

    try:
        while True:
            # Espera mensagens do cliente e ignora (somente ping/pong ou client broadcast local)
            data = await websocket.receive_text()
            # Echo opcional ou validação
            await websocket.send_text(json.dumps({"type": "ws.ack", "received": data}))
    except WebSocketDisconnect:
        pass
    finally:
        # Cleanup
        try:
            _channels_connections.get(channel_id, set()).discard(websocket)
        except Exception:
            pass
        if redis_pubsub:
            try:
                await redis_pubsub.unsubscribe(f"sordchat:channel:{channel_id}")
                await redis_pubsub.close()
            except Exception:
                pass