from __future__ import annotations

import json
from typing import Any


class AgentServiceBridge:
    """Bridge domain agents to MCP servers, RAG, and platform tools."""

    def __init__(self) -> None:
        self._rag_bundle: tuple[Any, Any] | None = None

    async def call_mcp(self, server_name: str, tool_name: str, arguments: dict[str, Any]) -> Any:
        from mcp_servers import get_mcp_server

        server = get_mcp_server(server_name)
        return await server.call_tool(tool_name, arguments)

    def _get_rag_bundle(self) -> tuple[Any, Any]:
        if self._rag_bundle is None:
            from rag.embeddings.provider import OpenAIEmbeddingProvider
            from rag.vector_db.client import VectorDBClient

            provider = OpenAIEmbeddingProvider()
            db = VectorDBClient("enterprise-kb")
            self._rag_bundle = (provider, db)
        return self._rag_bundle

    async def search_knowledge(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        from rag.retrievers.hybrid import HybridRetriever

        provider, db = self._get_rag_bundle()
        retriever = HybridRetriever(provider, db, top_k=limit, score_threshold=0.0)
        result = await retriever.retrieve(query)
        return [
            {"title": doc.content[:80], "score": doc.score, "metadata": doc.metadata}
            for doc in result.documents
        ]

    async def search(self, query: str, limit: int = 10) -> dict[str, Any]:
        from tools.search.tool import SearchTool

        tool = SearchTool()
        results = await tool.search(query, limit=limit)
        return {"query": query, "results": [r.model_dump() for r in results]}

    async def send_email(self, to: list[str], subject: str, body: str) -> dict[str, Any]:
        from tools.email.tool import EmailMessage, EmailTool

        tool = EmailTool()
        return await tool.send(EmailMessage(to=to, subject=subject, body=body))

    async def generate_report(self, title: str, data: dict[str, Any]) -> dict[str, Any]:
        from tools.reporting.tool import ReportingTool

        tool = ReportingTool()
        report = await tool.generate(title, data)
        return await tool.export(report)

    def format_tool_results(self, results: Any) -> str:
        return json.dumps(results, default=str)


agent_services = AgentServiceBridge()
