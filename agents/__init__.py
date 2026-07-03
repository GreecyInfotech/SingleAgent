from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

_AGENTS_DIR = Path(__file__).parent

_AGENT_SPECS: dict[str, tuple[str, str]] = {
    "customer-agent": ("customer-agent", "CustomerAgent"),
    "loan-agent": ("loan-agent", "LoanAgent"),
    "fraud-agent": ("fraud-agent", "FraudAgent"),
    "support-agent": ("support-agent", "SupportAgent"),
    "recommendation-agent": ("recommendation-agent", "RecommendationAgent"),
}
_CLASS_CACHE: dict[str, type[Any]] = {}
_INSTANCE_CACHE: dict[str, Any] = {}


def _load_agent_class(folder: str, class_name: str) -> type[Any]:
    cache_key = f"{folder}:{class_name}"
    if cache_key in _CLASS_CACHE:
        return _CLASS_CACHE[cache_key]

    module_path = _AGENTS_DIR / folder / "agent.py"
    spec = importlib.util.spec_from_file_location(f"agents.{folder}", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load agent from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    agent_cls = getattr(module, class_name)
    _CLASS_CACHE[cache_key] = agent_cls
    return agent_cls


def get_agent(name: str) -> Any:
    if name not in _AGENT_SPECS:
        raise ValueError(f"Unknown agent: {name}. Available: {list_agents()}")

    if name in _INSTANCE_CACHE:
        return _INSTANCE_CACHE[name]

    folder, class_name = _AGENT_SPECS[name]
    instance = _load_agent_class(folder, class_name)()
    _INSTANCE_CACHE[name] = instance
    return instance


def list_agents() -> list[str]:
    return list(_AGENT_SPECS.keys())
