import importlib.util
from pathlib import Path
from typing import Any

from mcp_servers.shared.base_server import MCPServerBase

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
_CLASS_CACHE: dict[str, type[Any]] = {}
_INSTANCE_CACHE: dict[str, MCPServerBase] = {}


def _load_server(folder: str, class_name: str) -> type[Any]:
    cache_key = f"{folder}:{class_name}"
    if cache_key in _CLASS_CACHE:
        return _CLASS_CACHE[cache_key]

    server_path = _SERVERS_DIR / folder / "server.py"
    if not server_path.exists():
        raise FileNotFoundError(f"Server module not found: {server_path}")

    spec = importlib.util.spec_from_file_location(f"mcp_servers.{folder}", server_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module spec for: {folder}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    loaded_class = getattr(module, class_name, None)
    if loaded_class is None:
        raise AttributeError(f"Class {class_name} not found in {server_path}")
    _CLASS_CACHE[cache_key] = loaded_class
    return loaded_class


def get_mcp_server(name: str) -> MCPServerBase:
    if name not in _SERVER_REGISTRY:
        available = ", ".join(sorted(_SERVER_REGISTRY))
        raise ValueError(f"Unknown MCP server: {name}. Available: {available}")

    if name in _INSTANCE_CACHE:
        return _INSTANCE_CACHE[name]

    folder, class_name = _SERVER_REGISTRY[name]
    instance = _load_server(folder, class_name)()
    _INSTANCE_CACHE[name] = instance
    return instance


def list_mcp_servers() -> list[str]:
    return list(_SERVER_REGISTRY.keys())
