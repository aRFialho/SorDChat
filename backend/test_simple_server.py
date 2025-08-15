"""
Servidor de teste super simples
"""

from fastapi import FastAPI
import uvicorn
import socket


def is_port_available(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            return True
    except OSError:
        return False


# Criar app simples
app = FastAPI(title="SorDChat - Teste Simples")


@app.get("/")
def read_root():
    return {"message": "SorDChat funcionando!", "status": "OK"}


@app.get("/test")
def test():
    return {"test": "Servidor respondendo corretamente"}


if __name__ == "__main__":
    # Encontrar porta disponível
    port = 8000
    while not is_port_available(port) and port < 8010:
        port += 1

    if port >= 8010:
        print("❌ Nenhuma porta disponível")
    else:
        print(f"🚀 Servidor teste na porta {port}")
        print(f"🌐 Acesse: http://127.0.0.1:{port}")
        uvicorn.run(app, host="127.0.0.1", port=port)