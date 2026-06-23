import json
from collections.abc import Awaitable, Callable
from typing import Any

from shared.safe_math import safe_evaluate

from enterprise_agent_platform.core.config import get_settings
from enterprise_agent_platform.core.logging import get_logger
from enterprise_agent_platform.domain.models import ToolDefinition

logger = get_logger(__name__)

ToolHandler = Callable[..., Awaitable[Any]]


class ToolRegistry:
    """Central registry for agent tools with schema validation."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        self._handlers: dict[str, ToolHandler] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: ToolHandler,
    ) -> None:
        self._tools[name] = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            handler=name,
        )
        self._handlers[name] = handler
        logger.info("tool_registered", tool_name=name)

    def get_tool_schemas(self, tool_names: list[str]) -> list[dict[str, Any]]:
        schemas = []
        for name in tool_names:
            if tool_def := self._tools.get(name):
                schemas.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool_def.name,
                            "description": tool_def.description,
                            "parameters": tool_def.parameters,
                        },
                    }
                )
        return schemas

    async def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        handler = self._handlers.get(name)
        if not handler:
            raise ValueError(f"Tool '{name}' not found in registry")
        logger.info("tool_executing", tool_name=name, arguments=arguments)
        result = await handler(**arguments)
        logger.info("tool_executed", tool_name=name)
        return result

    def list_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())


def create_default_tool_registry() -> ToolRegistry:
    from tools.document_parser.tool import DocumentParserTool
    from tools.email.tool import EmailMessage, EmailTool
    from tools.pdf.tool import PDFTool
    from tools.reporting.tool import ReportingTool
    from tools.search.tool import SearchTool

    registry = ToolRegistry()
    search_tool = SearchTool()
    email_tool = EmailTool()
    doc_parser = DocumentParserTool()
    pdf_tool = PDFTool()
    reporting_tool = ReportingTool()

    async def get_current_time() -> str:
        from datetime import UTC, datetime

        return datetime.now(UTC).isoformat()

    async def calculate(expression: str) -> str:
        return safe_evaluate(expression)

    async def search_knowledge(query: str, limit: int = 5) -> str:
        from rag.embeddings.provider import OpenAIEmbeddingProvider
        from rag.retrievers.hybrid import HybridRetriever
        from rag.vector_db.client import VectorDBClient

        settings = get_settings()
        provider = OpenAIEmbeddingProvider(api_key=settings.openai_api_key)
        db = VectorDBClient("enterprise-kb")
        retriever = HybridRetriever(provider, db, top_k=limit, score_threshold=0.0)
        result = await retriever.retrieve(query)
        payload = [
            {"title": doc.content[:120], "score": doc.score, "metadata": doc.metadata}
            for doc in result.documents
        ]
        return json.dumps(payload)

    async def enterprise_search(query: str, limit: int = 10) -> str:
        results = await search_tool.search(query, limit=limit)
        return json.dumps([r.model_dump() for r in results])

    async def send_email(to: list[str], subject: str, body: str) -> str:
        result = await email_tool.send(EmailMessage(to=to, subject=subject, body=body))
        return json.dumps(result)

    async def parse_document(filename: str, content: str, content_type: str = "text/plain") -> str:
        parsed = await doc_parser.parse(filename, content.encode(), content_type)
        return json.dumps(parsed.model_dump())

    async def extract_pdf(content: str) -> str:
        doc = await pdf_tool.extract_text(content.encode())
        return json.dumps(doc.model_dump())

    async def generate_report(title: str, data: dict[str, Any]) -> str:
        report = await reporting_tool.generate(title, data)
        exported = await reporting_tool.export(report)
        return json.dumps(exported)

    registry.register(
        name="get_current_time",
        description="Get the current UTC date and time in ISO format",
        parameters={"type": "object", "properties": {}, "required": []},
        handler=get_current_time,
    )
    registry.register(
        name="calculate",
        description="Evaluate a mathematical expression safely",
        parameters={
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
        handler=calculate,
    )
    registry.register(
        name="search_knowledge",
        description="Search the enterprise knowledge base via RAG",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
        handler=search_knowledge,
    )
    registry.register(
        name="search",
        description="Search enterprise content and documents",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
        handler=enterprise_search,
    )
    registry.register(
        name="email",
        description="Send an email notification",
        parameters={
            "type": "object",
            "properties": {
                "to": {"type": "array", "items": {"type": "string"}},
                "subject": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["to", "subject", "body"],
        },
        handler=send_email,
    )
    registry.register(
        name="document_parser",
        description="Parse a text or document file",
        parameters={
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "content": {"type": "string"},
                "content_type": {"type": "string"},
            },
            "required": ["filename", "content"],
        },
        handler=parse_document,
    )
    registry.register(
        name="pdf",
        description="Extract text from a PDF document",
        parameters={
            "type": "object",
            "properties": {"content": {"type": "string"}},
            "required": ["content"],
        },
        handler=extract_pdf,
    )
    registry.register(
        name="reporting",
        description="Generate an enterprise report",
        parameters={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "data": {"type": "object"},
            },
            "required": ["title", "data"],
        },
        handler=generate_report,
    )

    return registry
