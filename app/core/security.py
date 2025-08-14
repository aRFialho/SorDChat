from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(subject: str | int, expires_minutes: int, scope: str) -> str:
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode: dict[str, Any] = {
        "exp": expire,
        "sub": str(subject),
        "scope": scope,
        "iat": datetime.now(tz=timezone.utc),
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def create_access_token(subject: str | int) -> str:
    return create_token(subject, settings.ACCESS_TOKEN_EXPIRE_MINUTES, scope="access")


def create_refresh_token(subject: str | int) -> str:
    return create_token(subject, settings.REFRESH_TOKEN_EXPIRE_MINUTES, scope="refresh")


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)