from typing import Any

from mcp_servers.shared.base_server import MCPServerBase


class JiraMCPServer(MCPServerBase):
    name = "jira"
    version = "1.0.0"

    def __init__(self, base_url: str = "", api_token: str = "") -> None:
        self._base_url = base_url
        self._api_token = api_token

    async def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "create_issue",
                "description": "Create a Jira issue",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project": {"type": "string"},
                        "summary": {"type": "string"},
                        "description": {"type": "string"},
                        "issue_type": {"type": "string", "default": "Task"},
                    },
                    "required": ["project", "summary"],
                },
            },
            {
                "name": "get_issue",
                "description": "Get Jira issue by key",
                "inputSchema": {
                    "type": "object",
                    "properties": {"issue_key": {"type": "string"}},
                    "required": ["issue_key"],
                },
            },
            {
                "name": "search_issues",
                "description": "Search issues using JQL",
                "inputSchema": {
                    "type": "object",
                    "properties": {"jql": {"type": "string"}},
                    "required": ["jql"],
                },
            },
        ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        if name == "create_issue":
            return {
                "key": f"{arguments['project']}-1001",
                "summary": arguments["summary"],
                "status": "Open",
            }
        if name == "get_issue":
            return {"key": arguments["issue_key"], "status": "In Progress", "assignee": "agent"}
        if name == "search_issues":
            return {"issues": [], "total": 0, "jql": arguments["jql"]}
        raise ValueError(f"Unknown tool: {name}")
