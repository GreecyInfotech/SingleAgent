from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="production-ai-app-frontend")


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Production AI App</title></head>
    <body>
      <h1>Production AI App</h1>
      <p>Backend API is available at <code>/api/v1/chat</code>.</p>
    </body>
    </html>
    """
