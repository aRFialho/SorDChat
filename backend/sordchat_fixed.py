from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import jwt
import uvicorn
import json
import asyncio
import os
import uuid

# Configurações
SECRET_KEY = "sordchat_secret_key_super_secure_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 horas

# Configuração do banco de dados
SQLALCHEMY_DATABASE_URL = "sqlite:///./sordchat.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Configuração de hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Modelos do banco de dados
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    access_level = Column(String, default="usuario")  # usuario, coordenador, master
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")
    uploaded_files = relationship("FileUpload", back_populates="uploader")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # None para chat geral
    message_type = Column(String, default="text")  # text, file, image
    file_path = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    # Relacionamentos
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")


class FileUpload(Base):
    __tablename__ = "file_uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    content_type = Column(String)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    upload_date = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    uploader = relationship("User", back_populates="uploaded_files")


# Criar tabelas
Base.metadata.create_all(bind=engine)

# Instância da aplicação
app = FastAPI(title="SorDChat API", version="1.0.0")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de segurança
security = HTTPBearer()


# Dependência para obter sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Criar sessão global (temporário para desenvolvimento)
session = SessionLocal()


# Funções utilitárias
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = session.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user


# Classe para gerenciar conexões WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.user_connections: Dict[int, int] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        connection_id = id(websocket)
        self.active_connections[connection_id] = websocket
        self.user_connections[user_id] = connection_id
        await self.broadcast_user_status(user_id, True)
        await self.send_online_users(websocket)
        return connection_id

    def disconnect(self, user_id: int):
        if user_id in self.user_connections:
            connection_id = self.user_connections[user_id]
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
            del self.user_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.user_connections:
            connection_id = self.user_connections[user_id]
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    print(f"Erro ao enviar mensagem pessoal: {e}")
                    self.disconnect(user_id)

    async def broadcast(self, message: str, exclude_user: int = None):
        disconnected = []
        for user_id, connection_id in self.user_connections.items():
            if exclude_user and user_id == exclude_user:
                continue
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    print(f"Erro no broadcast: {e}")
                    disconnected.append(user_id)

        for user_id in disconnected:
            self.disconnect(user_id)

    async def broadcast_user_status(self, user_id: int, is_online: bool):
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                message = {
                    "type": "user_status",
                    "user_id": user_id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "is_online": is_online
                }
                await self.broadcast(json.dumps(message), exclude_user=user_id)
        except Exception as e:
            print(f"Erro ao broadcast status: {e}")

    async def send_online_users(self, websocket: WebSocket):
        try:
            online_users = []
            for user_id in self.user_connections.keys():
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    online_users.append({
                        "id": user.id,
                        "username": user.username,
                        "full_name": user.full_name
                    })

            message = {
                "type": "online_users",
                "users": online_users
            }
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Erro ao enviar usuários online: {e}")


# Instanciar gerenciador
manager = ConnectionManager()


# Criar usuários padrão
def create_default_users():
    # Verificar se já existem usuários
    existing_users = session.query(User).count()
    if existing_users > 0:
        return

    default_users = [
        {
            "username": "admin",
            "email": "admin@sordchat.com",
            "full_name": "Administrador Master",
            "password": "admin123",
            "access_level": "master"
        },
        {
            "username": "coordenador",
            "email": "coord@sordchat.com",
            "full_name": "Coordenador Sistema",
            "password": "coord123",
            "access_level": "coordenador"
        },
        {
            "username": "usuario",
            "email": "user@sordchat.com",
            "full_name": "Usuário Padrão",
            "password": "user123",
            "access_level": "usuario"
        }
    ]

    for user_data in default_users:
        hashed_password = get_password_hash(user_data["password"])
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            hashed_password=hashed_password,
            access_level=user_data["access_level"]
        )
        session.add(user)

    session.commit()
    print("✅ Usuários padrão criados!")


# Rotas da API
@app.get("/")
async def root():
    return {
        "message": "SorDChat API",
        "version": "1.0.0",
        "status": "online"
    }


@app.post("/auth/login")
async def login(credentials: dict):
    username = credentials.get("username")
    password = credentials.get("password")

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username e password são obrigatórios")

    user = session.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Usuário inativo")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "access_level": user.access_level
        }
    }


@app.post("/auth/logout")
async def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Logout realizado com sucesso"}


@app.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "access_level": current_user.access_level
    }


# WebSocket endpoint
@app.websocket("/messages/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    user = None
    try:
        # Verificar token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if not user_id:
            await websocket.close(code=1008)
            return

        user = session.query(User).filter(User.id == int(user_id)).first()
        if not user:
            await websocket.close(code=1008)
            return

        # Conectar usuário
        await manager.connect(websocket, user.id)
        print(f"✅ {user.username} conectado ao WebSocket")

        # Mensagem de boas-vindas
        welcome_message = {
            "type": "connection",
            "message": f"Conectado como {user.full_name}! 🎉"
        }
        await websocket.send_text(json.dumps(welcome_message))

        # Enviar histórico
        recent_messages = session.query(Message).order_by(Message.timestamp.desc()).limit(50).all()
        messages_data = []

        for msg in reversed(recent_messages):
            sender = session.query(User).filter(User.id == msg.sender_id).first()
            messages_data.append({
                "id": msg.id,
                "content": msg.content,
                "sender_id": msg.sender_id,
                "sender_name": sender.full_name if sender else "Usuário",
                "receiver_id": msg.receiver_id,
                "message_type": msg.message_type,
                "timestamp": msg.timestamp.isoformat(),
                "file_path": msg.file_path
            })

        history_message = {
            "type": "message_history",
            "messages": messages_data
        }
        await websocket.send_text(json.dumps(history_message))

        # Loop principal
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)

                if message_data["type"] == "chat_message":
                    # Nova mensagem
                    new_message = Message(
                        content=message_data["content"],
                        sender_id=user.id,
                        receiver_id=message_data.get("receiver_id"),
                        message_type=message_data.get("message_type", "text"),
                        file_path=message_data.get("file_path")
                    )

                    session.add(new_message)
                    session.commit()

                    # Broadcast
                    broadcast_message = {
                        "type": "new_message",
                        "message": {
                            "id": new_message.id,
                            "content": new_message.content,
                            "sender_id": user.id,
                            "sender_name": user.full_name,
                            "receiver_id": new_message.receiver_id,
                            "message_type": new_message.message_type,
                            "timestamp": new_message.timestamp.isoformat(),
                            "file_path": new_message.file_path
                        }
                    }

                    if new_message.receiver_id:
                        await manager.send_personal_message(json.dumps(broadcast_message), new_message.receiver_id)
                        await manager.send_personal_message(json.dumps(broadcast_message), user.id)
                    else:
                        await manager.broadcast(json.dumps(broadcast_message))

                elif message_data["type"] == "typing":
                    # Indicador de digitação
                    typing_message = {
                        "type": "typing",
                        "user_id": user.id,
                        "username": user.username,
                        "is_typing": message_data["is_typing"]
                    }

                    if message_data.get("receiver_id"):
                        await manager.send_personal_message(json.dumps(typing_message), message_data["receiver_id"])
                    else:
                        await manager.broadcast(json.dumps(typing_message), exclude_user=user.id)

                elif message_data["type"] == "ping":
                    pong_message = {"type": "pong"}
                    await websocket.send_text(json.dumps(pong_message))

            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Erro no WebSocket: {e}")
                break

    except Exception as e:
        print(f"Erro na conexão: {e}")
    finally:
        if user:
            manager.disconnect(user.id)
            await manager.broadcast_user_status(user.id, False)


# Upload de arquivos
@app.post("/files/upload")
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    try:
        # Verificações
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/plain']

        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Tipo de arquivo não permitido")

        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="Arquivo muito grande")

        # Salvar arquivo
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)

        with open(file_path, "wb") as f:
            f.write(content)

        # Salvar no banco
        file_record = FileUpload(
            filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            content_type=file.content_type,
            uploaded_by=current_user.id
        )

        session.add(file_record)
        session.commit()

        return {
            "id": file_record.id,
            "filename": file.filename,
            "file_path": file_path,
            "file_size": len(content),
            "content_type": file.content_type
        }

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files/download/{file_id}")
async def download_file(file_id: int, current_user: User = Depends(get_current_user)):
    file_record = session.query(FileUpload).filter(FileUpload.id == file_id).first()

    if not file_record:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    if not os.path.exists(file_record.file_path):
        raise HTTPException(status_code=404, detail="Arquivo não existe")

    return FileResponse(
        path=file_record.file_path,
        filename=file_record.filename,
        media_type=file_record.content_type
    )


if __name__ == "__main__":
    create_default_users()
    print("🚀 Iniciando SorDChat Backend...")
    print("📡 WebSocket: ws://127.0.0.1:8001/messages/ws/{token}")
    print("🌐 API Docs: http://127.0.0.1:8001/docs")
    uvicorn.run(app, host="127.0.0.1", port=8001)