import time

from fastapi import APIRouter, Depends, Response

from enterprise_agent_platform import __version__
from enterprise_agent_platform.api.deps import get_db
from enterprise_agent_platform.application.dto.schemas import HealthResponse
from enterprise_agent_platform.core.config import Settings, get_settings
from enterprise_agent_platform.infrastructure.persistence.database import Database

router = APIRouter()

_START_TIME = time.time()
_REQUEST_COUNT = 0


def increment_request_count() -> None:
    global _REQUEST_COUNT
    _REQUEST_COUNT += 1


@router.get("/health", response_model=HealthResponse)
async def health_check(
    settings: Settings = Depends(get_settings),
    db: Database = Depends(get_db),
) -> HealthResponse:
    increment_request_count()
    db_status = "healthy"
    try:
        async for session in db.get_session():
            from sqlalchemy import text

            await session.execute(text("SELECT 1"))
            break
    except Exception:
        db_status = "unhealthy"

    redis_status = "not_configured"
    if settings.redis_url:
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(str(settings.redis_url))
            await client.ping()
            await client.aclose()
            redis_status = "healthy"
        except Exception:
            redis_status = "unhealthy"

    overall = "healthy" if db_status == "healthy" else "degraded"

    return HealthResponse(
        status=overall,
        version=__version__,
        environment=settings.app_env,
        database=db_status,
        redis=redis_status,
    )


@router.get("/ready")
async def readiness() -> dict[str, str]:
    return {"status": "ready"}


@router.get("/live")
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/metrics")
async def metrics(settings: Settings = Depends(get_settings)) -> Response:
    """Prometheus-compatible metrics endpoint."""
    uptime = time.time() - _START_TIME
    lines = [
        "# HELP eap_up Platform is running",
        "# TYPE eap_up gauge",
        "eap_up 1",
        "# HELP eap_uptime_seconds Uptime in seconds",
        "# TYPE eap_uptime_seconds gauge",
        f"eap_uptime_seconds {uptime:.2f}",
        "# HELP eap_requests_total Total health check requests",
        "# TYPE eap_requests_total counter",
        f"eap_requests_total {_REQUEST_COUNT}",
        "# HELP eap_info Platform info",
        "# TYPE eap_info gauge",
        f'eap_info{{version="{__version__}",env="{settings.app_env}"}} 1',
    ]
    return Response(content="\n".join(lines) + "\n", media_type="text/plain")
