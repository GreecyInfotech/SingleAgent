import importlib.util
from pathlib import Path

_SERVERS_DIR = Path(__file__).parent.parent / "mcp-servers"

_SERVER_REGISTRY: dict[str, tuple[str, str]] = {
    "jira": ("jira", "JiraMCPServer"),
    "confluence": ("confluence", "ConfluenceMCPServer"),
    "github": ("github", "GitHubMCPServer"),
    "salesforce": ("salesforce", "SalesforceMCPServer"),
    "sap": ("sap", "SAPMCPServer"),
    "oracle": ("oracle", "OracleMCPServer"),
    "postgres": ("postgres", "PostgresMCPServer"),
}


def _load_server(folder: str, class_name: str):
    server_path = _SERVERS_DIR / folder / "server.py"
    spec = importlib.util.spec_from_file_location(f"mcp_servers.{folder}", server_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)


def get_mcp_server(name: str):
    if name not in _SERVER_REGISTRY:
        raise ValueError(f"Unknown MCP server: {name}")
    folder, class_name = _SERVER_REGISTRY[name]
    return _load_server(folder, class_name)()


def list_mcp_servers() -> list[str]:
    return list(_SERVER_REGISTRY.keys())
