from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router

app = FastAPI(title="SorDChat API")
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    return """
    <html>
      <head><title>SorDChat API</title></head>
      <body>
        <h1>SorDChat API</h1>
        <p>Status: OK</p>
        <p>Documentação: <a href="/docs">/docs</a></p>
      </body>
    </html>
    """

# Inclui os routers
app.include_router(users_router)
app.include_router(auth_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
