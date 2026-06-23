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


def _load_agent_class(folder: str, class_name: str) -> type:
    module_path = _AGENTS_DIR / folder / "agent.py"
    spec = importlib.util.spec_from_file_location(f"agents.{folder}", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load agent from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)


def get_agent(name: str) -> Any:
    if name not in _AGENT_SPECS:
        raise ValueError(f"Unknown agent: {name}. Available: {list_agents()}")
    folder, class_name = _AGENT_SPECS[name]
    agent_cls = _load_agent_class(folder, class_name)
    return agent_cls()


def list_agents() -> list[str]:
    return list(_AGENT_SPECS.keys())
