# app/main.py
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, channels, messages, workspaces, tasks, search
from fastapi.responses import ORJSONResponse

app = FastAPI(default_response_class=ORJSONResponse)

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # ajustar por ambiente
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(channels.router, prefix="/api/channels", tags=["channels"])
    app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
    app.include_router(workspaces.router, prefix="/api/workspaces", tags=["workspaces"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
    app.include_router(search.router, prefix="/api/search", tags=["search"])

    return app

app = create_app()