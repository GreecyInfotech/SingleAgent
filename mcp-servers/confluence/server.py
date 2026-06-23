from typing import Any

from mcp_servers.shared.base_server import MCPServerBase


class ConfluenceMCPServer(MCPServerBase):
    name = "confluence"
    version = "1.0.0"

    async def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "search_pages",
                "description": "Search Confluence pages",
                "inputSchema": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}, "space": {"type": "string"}},
                    "required": ["query"],
                },
            },
            {
                "name": "get_page",
                "description": "Get page content by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {"page_id": {"type": "string"}},
                    "required": ["page_id"],
                },
            },
        ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        if name == "search_pages":
            return {"pages": [{"id": "1", "title": f"Results for: {arguments['query']}"}]}
        if name == "get_page":
            return {"id": arguments["page_id"], "content": "<p>Page content</p>"}
        raise ValueError(f"Unknown tool: {name}")
