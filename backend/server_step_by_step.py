"""
Servidor SorDChat - Passo a passo
"""

from fastapi import FastAPI
import uvicorn
import socket
from datetime import datetime
import sys
from pathlib import Path


def is_port_available(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            return True
    except OSError:
        return False


def find_available_port(start_port=8000):
    port = start_port
    while not is_port_available(port) and port < 8010:
        port += 1
    return port if port < 8010 else None


# Adicionar o diretório atual ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Criar aplicação FastAPI
app = FastAPI(
    title="SorDChat API",
    description="API para sistema corporativo de mensagens, tickets e controle de tarefas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração CORS
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rotas básicas
@app.get("/")
async def root():
    return {
        "message": "SorDChat API está funcionando!",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "SorDChat API"
    }


# Tentar carregar rotas de autenticação
try:
    print("🔄 Tentando carregar rotas de autenticação...")
    from sordchat.routes import auth

    app.include_router(auth.router)
    print("✅ Rotas de autenticação carregadas com sucesso!")


    @app.get("/status")
    async def status():
        return {
            "auth_loaded": True,
            "message": "Todas as rotas carregadas"
        }

except ImportError as e:
    print(f"⚠️ Não foi possível carregar rotas de auth: {e}")


    @app.get("/status")
    async def status():
        return {
            "auth_loaded": False,
            "message": "Rodando sem autenticação",
            "error": str(e)
        }

if __name__ == "__main__":
    port = find_available_port(8000)

    if not port:
        print("❌ Nenhuma porta disponível")
    else:
        print("🚀 SorDChat API - Iniciando...")
        print(f"📡 Servidor: http://127.0.0.1:{port}")
        print(f"📚 Docs: http://127.0.0.1:{port}/docs")
        print(f"🔍 Status: http://127.0.0.1:{port}/status")
        print("=" * 40)

        uvicorn.run(app, host="127.0.0.1", port=port)