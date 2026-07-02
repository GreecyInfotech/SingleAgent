from typing import Any

from mcp_servers.shared.base_server import MCPServerBase


class GitHubMCPServer(MCPServerBase):
    name = "github"
    version = "1.0.0"

    async def list_tools(self) -> list[dict[str, Any]]:
        return [
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

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        if name == "search_repos":
            return {"repos": [{"name": "enterprise-agent-platform", "stars": 42}]}
        if name == "get_pull_request":
            return {"number": arguments["pr_number"], "state": "open", "title": "Feature PR"}
        if name == "create_issue":
            return {"number": 101, "title": arguments["title"], "state": "open"}
        raise ValueError(f"Unknown tool: {name}")
