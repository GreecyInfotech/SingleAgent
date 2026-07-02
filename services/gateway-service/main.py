from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Gateway Service", version="1.0.0")

SERVICE_ROUTES: dict[str, str] = {
    "auth": "http://localhost:8001",
    "users": "http://localhost:8002",
    "audit": "http://localhost:8003",
    "notifications": "http://localhost:8004",
    "agents": "http://localhost:8000",
}


@app.api_route("/gateway/{service}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(service: str, path: str, request: Request) -> JSONResponse:
    base_url = SERVICE_ROUTES.get(service)
    if not base_url:
        raise HTTPException(status_code=404, detail=f"Unknown service: {service}")

    url = f"{base_url}/{path}"
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            params=dict(request.query_params),
        )

    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/gateway/services")
async def list_services() -> dict[str, Any]:
    return {"services": list(SERVICE_ROUTES.keys()), "routes": SERVICE_ROUTES}


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "service": "gateway-service"}
