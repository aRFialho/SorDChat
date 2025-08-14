import os
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "SorDChat"
    API_V1_PREFIX: str = "/api"

    # Segurança
    JWT_SECRET: str = Field(default="CHANGE_ME_SUPER_SECRET", description="Chave secreta para JWT")
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # Database (SQLite default)
    DATABASE_URL: str = Field(default="sqlite:///./sordchat.db")

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])

    # Redis para broadcast (opcional)
    REDIS_URL: str | None = None

    # Ambiente
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()