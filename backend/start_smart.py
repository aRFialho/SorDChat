"""
Iniciador inteligente do SorDChat - testa várias portas
"""

import uvicorn
import socket
import sys
import os
from pathlib import Path


def is_port_available(port):
    """Verifica se uma porta está disponível"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            return True
    except OSError:
        return False


def find_available_port(start_port=8000, max_attempts=10):
    """Encontra uma porta disponível"""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    return None


def main():
    """Inicia o servidor em uma porta disponível"""

    # Adicionar o diretório atual ao path
    backend_dir = Path(__file__).parent
    sys.path.insert(0, str(backend_dir))

    try:
        # Importar a aplicação
        from sordchat.main import app

        # Encontrar porta disponível
        port = find_available_port(8000)

        if not port:
            print("❌ Nenhuma porta disponível encontrada entre 8000-8009")
            return

        print("🚀 SorDChat API - Iniciando...")
        print(f"📡 Servidor: http://127.0.0.1:{port}")
        print(f"📚 Documentação: http://127.0.0.1:{port}/docs")
        print(f"🔧 Porta escolhida: {port}")
        print("🔄 Pressione Ctrl+C para parar")
        print("=" * 50)

        # Iniciar servidor
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=port,
            reload=True,
            log_level="info"
        )

    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        print("Verifique se todos os arquivos estão no lugar correto")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    main()