import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from enterprise_agent_platform.api.deps import set_database, set_tool_registry
from enterprise_agent_platform.core.config import Settings
from enterprise_agent_platform.infrastructure.agents.tool_registry import create_default_tool_registry
from enterprise_agent_platform.infrastructure.persistence.database import Database
from enterprise_agent_platform.infrastructure.persistence.models import Base
from enterprise_agent_platform.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        app_env="testing",
        debug=True,
        secret_key="test-secret-key-at-least-32-chars-long",
        database_url="sqlite+aiosqlite:///:memory:",
        redis_url="redis://localhost:6379/0",
        openai_api_key="test-key",
    )


@pytest_asyncio.fixture
async def test_db(test_settings: Settings) -> Database:
    engine = create_async_engine(str(test_settings.database_url))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    class TestDatabase(Database):
        def __init__(self) -> None:
            self._engine = engine
            self._session_factory = session_factory

    db = TestDatabase()
    set_database(db)
    set_tool_registry(create_default_tool_registry())
    yield db
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db: Database, test_settings: Settings, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-at-least-32-chars-long")
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

    from enterprise_agent_platform.core.config import get_settings

    get_settings.cache_clear()

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_liveness(client: AsyncClient) -> None:
    response = await client.get("/api/v1/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


@pytest.mark.asyncio
async def test_create_and_get_agent(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/v1/agents",
        json={
            "name": "Support Agent",
            "description": "Customer support agent",
            "system_prompt": "You are a helpful customer support agent.",
            "tools": ["get_current_time"],
        },
    )
    assert create_response.status_code == 201
    agent = create_response.json()
    assert agent["name"] == "Support Agent"
    assert agent["status"] == "active"

    get_response = await client.get(f"/api/v1/agents/{agent['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == agent["id"]


@pytest.mark.asyncio
async def test_list_agents(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/agents",
        json={
            "name": "Agent 1",
            "system_prompt": "Test prompt",
        },
    )
    response = await client.get("/api/v1/agents")
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_create_conversation(client: AsyncClient) -> None:
    agent_response = await client.post(
        "/api/v1/agents",
        json={
            "name": "Chat Agent",
            "system_prompt": "You are helpful.",
        },
    )
    agent_id = agent_response.json()["id"]

    conv_response = await client.post(
        "/api/v1/conversations",
        json={"agent_id": agent_id, "title": "Test Chat"},
    )
    assert conv_response.status_code == 201
    conversation = conv_response.json()
    assert conversation["agent_id"] == agent_id
    assert conversation["title"] == "Test Chat"


@pytest.mark.asyncio
async def test_list_tools(client: AsyncClient) -> None:
    response = await client.get("/api/v1/tools")
    assert response.status_code == 200
    tools = response.json()
    assert len(tools) >= 3
    tool_names = {t["name"] for t in tools}
    assert "get_current_time" in tool_names
    assert "calculate" in tool_names


@pytest.mark.asyncio
async def test_agent_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/agents/00000000-0000-0000-0000-000000000001")
    assert response.status_code == 404
