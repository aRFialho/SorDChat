# SorDChat (Backend FastAPI)

## Descrição
MVP completo de backend para chats, canais, mensagens (com threads), workspaces, tarefas (Kanban), busca simples, autenticação JWT e WebSockets com broadcast local e via Redis (opcional).

## Requisitos
- Python 3.11+
- Pip
- (Opcional) Postgres
- (Opcional) Redis

## Instalação
1. Crie um virtualenv:
   python -m venv .venv
   source .venv/bin/activate  (Linux/Mac)
   .venv\Scripts\activate     (Windows)

2. Instale dependências:
   pip install -r requirements.txt

3. Configure variáveis:
   cp .env.example .env
   (edite o JWT_SECRET e a DATABASE_URL se desejar)

4. Rode:
   python run.py
   API em http://localhost:8000
   Docs em http://localhost:8000/docs

## Fluxo básico
- POST /api/auth/register
- POST /api/auth/login (OAuth2PasswordRequestForm: username=email, password)
- Use o access_token como Bearer nos endpoints

## WebSocket
- Conecte em: ws://localhost:8000/ws/{channel_id}
- Envie mensagens REST para /api/messages para broadcast automático no canal

## Notas
- O banco é criado automaticamente (SQLite) no startup.
- Para produção: use Postgres + Alembic + Redis + workers gerenciados.