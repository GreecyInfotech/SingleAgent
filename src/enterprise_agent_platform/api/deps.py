from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from enterprise_agent_platform.application.services.agent_service import AgentService
from enterprise_agent_platform.application.services.conversation_service import ConversationService
from enterprise_agent_platform.application.services.platform_service import PlatformService
from enterprise_agent_platform.core.config import Settings, get_settings
from enterprise_agent_platform.core.exceptions import PlatformError
from enterprise_agent_platform.infrastructure.agents.llm_executor import LLMAgentExecutor
from enterprise_agent_platform.infrastructure.agents.tool_registry import ToolRegistry
from enterprise_agent_platform.infrastructure.persistence.database import Database
from enterprise_agent_platform.infrastructure.persistence.repositories import (
    SQLAgentRepository,
    SQLConversationRepository,
    SQLMessageRepository,
)

_database: Database | None = None
_tool_registry: ToolRegistry | None = None


def set_database(db: Database) -> None:
    global _database
    _database = db


def set_tool_registry(registry: ToolRegistry) -> None:
    global _tool_registry
    _tool_registry = registry


def get_db() -> Database:
    if _database is None:
        raise RuntimeError("Database not initialized")
    return _database


def get_tool_registry() -> ToolRegistry:
    if _tool_registry is None:
        raise RuntimeError("Tool registry not initialized")
    return _tool_registry


@lru_cache
def get_platform_service() -> PlatformService:
    return PlatformService()


async def get_session(
    db: Annotated[Database, Depends(get_db)],
) -> AsyncGenerator[AsyncSession, None]:
    async for session in db.get_session():
        yield session


def get_agent_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AgentService:
    return AgentService(SQLAgentRepository(session), settings)


def get_conversation_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    tool_registry: Annotated[ToolRegistry, Depends(get_tool_registry)],
) -> ConversationService:
    executor = LLMAgentExecutor(settings, tool_registry)
    return ConversationService(
        SQLConversationRepository(session),
        SQLMessageRepository(session),
        SQLAgentRepository(session),
        executor,
        settings,
    )


async def verify_api_key(
    settings: Annotated[Settings, Depends(get_settings)],
    x_api_key: Annotated[str | None, Header()] = None,
) -> str:
    """Validate API key in production environments."""
    if settings.is_production and (not x_api_key or x_api_key != settings.secret_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return x_api_key or "anonymous"


def handle_platform_error(error: PlatformError) -> HTTPException:
    status_map = {
        "NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "AGENT_EXECUTION_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "AUTHENTICATION_ERROR": status.HTTP_401_UNAUTHORIZED,
        "AUTHORIZATION_ERROR": status.HTTP_403_FORBIDDEN,
    }
    return HTTPException(
        status_code=status_map.get(error.code, status.HTTP_500_INTERNAL_SERVER_ERROR),
        detail={"code": error.code, "message": error.message, "details": error.details},
    )
