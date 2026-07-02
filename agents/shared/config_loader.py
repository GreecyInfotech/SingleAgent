from pathlib import Path
from typing import Any

from agents.shared.base import AgentConfig
from shared.yaml_config import load_yaml_config

_AGENTS_ROOT = Path(__file__).parent.parent


def load_agent_config(agent_folder: str, defaults: dict[str, Any]) -> AgentConfig:
    """Load agent config from config.yaml merged with code defaults."""
    yaml_path = _AGENTS_ROOT / agent_folder / "config.yaml"
    file_config = load_yaml_config(yaml_path)

    rag_config = file_config.get("rag", {})
    limits = file_config.get("limits", {})
    escalation = file_config.get("escalation", {})

    metadata = {
        **defaults.get("metadata", {}),
        "version": file_config.get("version", defaults.get("metadata", {}).get("version", "1.0.0")),
        "domain": file_config.get("domain", defaults.get("metadata", {}).get("domain", "")),
        **limits,
        **escalation,
    }

    return AgentConfig(
        name=file_config.get("name", defaults["name"]),
        description=defaults.get("description", ""),
        system_prompt=defaults["system_prompt"],
        model=file_config.get("model", defaults.get("model", "gpt-4o-mini")),
        temperature=float(file_config.get("temperature", defaults.get("temperature", 0.7))),
        max_tokens=int(defaults.get("max_tokens", 4096)),
        tools=file_config.get("tools", defaults.get("tools", [])),
        mcp_servers=file_config.get("mcp_servers", defaults.get("mcp_servers", [])),
        rag_enabled=bool(rag_config.get("enabled", defaults.get("rag_enabled", False))),
        metadata={
            **metadata,
            "rag_collections": rag_config.get("collections", []),
        },
    )
