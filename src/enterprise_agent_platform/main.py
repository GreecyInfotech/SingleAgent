from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from enterprise_agent_platform import __version__
from enterprise_agent_platform.api.deps import set_database, set_tool_registry
from enterprise_agent_platform.api.exception_handlers import platform_error_handler
from enterprise_agent_platform.api.v1 import health, platform, router
from enterprise_agent_platform.core.config import get_settings
from enterprise_agent_platform.core.exceptions import PlatformError
from enterprise_agent_platform.core.logging import get_logger, setup_logging
from enterprise_agent_platform.infrastructure.agents.tool_registry import (
    create_default_tool_registry,
)
from enterprise_agent_platform.infrastructure.persistence.database import Database

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(settings)

    database = Database(settings)
    if not settings.is_production:
        await database.create_tables()

    tool_registry = create_default_tool_registry()

    set_database(database)
    set_tool_registry(tool_registry)

    app.state.settings = settings
    app.state.database = database
    app.state.tool_registry = tool_registry

    logger.info(
        "application_started",
        version=__version__,
        environment=settings.app_env,
    )

    yield

    await database.close()
    logger.info("application_stopped")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Enterprise Agent Platform",
        description="Production-ready AI agent orchestration platform",
        version=__version__,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(PlatformError, platform_error_handler)
    app.include_router(health.router, prefix=settings.api_v1_prefix, tags=["Health"])
    app.include_router(router.router, prefix=settings.api_v1_prefix, tags=["API v1"])
    app.include_router(platform.router, prefix=settings.api_v1_prefix, tags=["Platform"])

    return app


app = create_app()


def run() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "enterprise_agent_platform.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run()
