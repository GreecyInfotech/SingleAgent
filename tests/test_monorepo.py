import pytest

from agents import get_agent, list_agents


def test_list_agents():
    agents = list_agents()
    assert len(agents) == 5
    assert "customer-agent" in agents
    assert "fraud-agent" in agents


@pytest.mark.asyncio
async def test_customer_agent_process():
    agent = get_agent("customer-agent")
    result = await agent.process({"customer_id": "C001", "query": "What is my segment?"})
    assert result["agent"] == "customer-agent"
    assert result["intent"] == "segmentation"


@pytest.mark.asyncio
async def test_loan_agent_process():
    agent = get_agent("loan-agent")
    result = await agent.process({
        "application_id": "L001",
        "amount": 50000,
        "annual_income": 120000,
        "monthly_debt": 2000,
    })
    assert "dti_ratio" in result
    assert "risk_score" in result


@pytest.mark.asyncio
async def test_fraud_agent_process():
    agent = get_agent("fraud-agent")
    result = await agent.process({
        "transaction_id": "T001",
        "signals": ["unusual_amount", "geo_mismatch"],
    })
    assert result["risk_score"] > 0
    assert len(result["triggered_signals"]) == 2


@pytest.mark.asyncio
async def test_orchestrator_routing():
    from orchestrator.workflows.runner import WorkflowRunner

    runner = WorkflowRunner()
    result = await runner.run("I need help with a fraud alert")
    assert result["agent"] == "fraud-agent"
    assert result["result"] is not None


@pytest.mark.asyncio
async def test_mcp_jira_server():
    from mcp_servers import get_mcp_server

    server = get_mcp_server("jira")
    tools = await server.list_tools()
    assert len(tools) >= 3

    result = await server.call_tool("create_issue", {
        "project": "EAP",
        "summary": "Test issue",
    })
    assert result["key"] == "EAP-1001"


@pytest.mark.asyncio
async def test_rag_chunking():
    from rag.chunking.strategies import ChunkStrategy, get_chunker

    chunker = get_chunker(ChunkStrategy.FIXED_SIZE, chunk_size=100, overlap=10)
    chunks = chunker.chunk("A" * 250, {"source": "test"})
    assert len(chunks) >= 2


@pytest.mark.asyncio
async def test_rag_retrieval():
    from rag.embeddings.provider import OpenAIEmbeddingProvider
    from rag.retrievers.hybrid import HybridRetriever
    from rag.vector_db.client import VectorDBClient

    provider = OpenAIEmbeddingProvider(api_key="")
    db = VectorDBClient("test")
    retriever = HybridRetriever(provider, db, score_threshold=0.0)

    await retriever.index_documents(["Enterprise agent platform documentation"])
    result = await retriever.retrieve("agent platform")
    assert result.total_found >= 1
