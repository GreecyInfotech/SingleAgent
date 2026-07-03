from typing import Any

from mcp_servers.shared.base_server import DeclarativeMCPServer


class GitHubMCPServer(DeclarativeMCPServer):
    name = "github"
    version = "1.0.0"
    TOOL_DEFINITIONS = [
        {
            "name": "search_repos",
            "description": "Search GitHub repositories",
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
        {
            "name": "get_pull_request",
            "description": "Get pull request details",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "pr_number": {"type": "integer"},
                },
                "required": ["owner", "repo", "pr_number"],
            },
        },
        {
            "name": "create_issue",
            "description": "Create a GitHub issue",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "title": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["owner", "repo", "title"],
            },
        },
    ]

    def _build_tool_handlers(self):
        return {
            "search_repos": self._search_repos,
            "get_pull_request": self._get_pull_request,
            "create_issue": self._create_issue,
        }

    async def _search_repos(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"repos": [{"name": "enterprise-agent-platform", "stars": 42, "query": arguments["query"]}]}

    async def _get_pull_request(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"number": arguments["pr_number"], "state": "open", "title": "Feature PR"}

    async def _create_issue(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"number": 101, "title": arguments["title"], "state": "open"}
