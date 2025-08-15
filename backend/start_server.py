"""
Script para iniciar o servidor SorDChat
"""

import uvicorn
import sys
import os

def main():
    """Inicia o servidor FastAPI"""
    print("🚀 Iniciando servidor SorDChat...")
    print("📡 API: http://127.0.0.1:8000")
    print("📚 Documentação: http://127.0.0.1:8000/docs")
    print("🔄 Pressione Ctrl+C para parar")
    print("=" * 50)

    # Configuração para funcionar tanto no terminal quanto no PyCharm
    uvicorn.run(
        "sordchat.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        reload_dirs=["./sordchat"]  # Especifica o diretório para reload
    )

if __name__ == "__main__":
    main()