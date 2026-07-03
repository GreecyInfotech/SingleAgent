from typing import Any

from mcp_servers.shared.base_server import DeclarativeMCPServer


class JiraMCPServer(DeclarativeMCPServer):
    name = "jira"
    version = "1.0.0"
    TOOL_DEFINITIONS = [
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

    def __init__(self, base_url: str = "", api_token: str = "") -> None:
        self._base_url = base_url
        self._api_token = api_token

    def _build_tool_handlers(self):
        return {
            "create_issue": self._create_issue,
            "get_issue": self._get_issue,
            "search_issues": self._search_issues,
        }

    async def _create_issue(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {
            "key": f"{arguments['project']}-1001",
            "summary": arguments["summary"],
            "status": "Open",
        }

    async def _get_issue(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"key": arguments["issue_key"], "status": "In Progress", "assignee": "agent"}

    async def _search_issues(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"issues": [], "total": 0, "jql": arguments["jql"]}
