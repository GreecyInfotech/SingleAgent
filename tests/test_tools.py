import json

import pytest

from enterprise_agent_platform.infrastructure.agents.tool_registry import create_default_tool_registry
from rag.embeddings.provider import OpenAIEmbeddingProvider
from rag.retrievers.hybrid import HybridRetriever
from rag.vector_db.client import VectorDBClient


@pytest.fixture
def registry():
    return create_default_tool_registry()


@pytest.mark.asyncio
async def test_get_current_time(registry) -> None:
    result = await registry.execute("get_current_time", {})
    assert "T" in result


@pytest.mark.asyncio
async def test_calculate(registry) -> None:
    result = await registry.execute("calculate", {"expression": "2 + 2"})
    assert result == "4"


@pytest.mark.asyncio
async def test_calculate_invalid(registry) -> None:
    result = await registry.execute("calculate", {"expression": "import os"})
    assert "Error" in result


@pytest.mark.asyncio
async def test_search_knowledge(registry) -> None:
    provider = OpenAIEmbeddingProvider(api_key="")
    db = VectorDBClient("test-kb")
    retriever = HybridRetriever(provider, db, score_threshold=0.0)
    await retriever.index_documents([f"Document about enterprise AI platform"])

    result = await registry.execute("search_knowledge", {"query": "enterprise AI"})
    payload = json.loads(result)
    assert isinstance(payload, list)


@pytest.mark.asyncio
async def test_enterprise_search(registry) -> None:
    result = await registry.execute("search", {"query": "compliance"})
    payload = json.loads(result)
    assert len(payload) >= 1


def test_tool_schemas(registry) -> None:
    schemas = registry.get_tool_schemas(["get_current_time", "calculate", "search"])
    assert len(schemas) == 3
    assert schemas[0]["function"]["name"] == "get_current_time"


def test_list_tools(registry) -> None:
    tools = registry.list_tools()
    assert len(tools) == 8
    tool_names = {t.name for t in tools}
    assert "search_knowledge" in tool_names
    assert "reporting" in tool_names
