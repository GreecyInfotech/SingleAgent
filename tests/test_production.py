import pytest

from shared.safe_math import safe_evaluate


def test_safe_evaluate_basic():
    assert safe_evaluate("2 + 2") == "4"
    assert safe_evaluate("10 * 5") == "50"
    assert safe_evaluate("(3 + 4) * 2") == "14"


def test_safe_evaluate_invalid():
    assert "Error" in safe_evaluate("import os")
    assert "Error" in safe_evaluate("__import__('os')")


def test_agent_config_loader():
    from agents.shared.config_loader import load_agent_config

    config = load_agent_config(
        "customer-agent",
        {
            "name": "customer-agent",
            "description": "Test",
            "system_prompt": "Test prompt",
            "metadata": {"domain": "customer"},
        },
    )
    assert config.name == "customer-agent"
    assert config.rag_enabled is True
    assert "salesforce" in config.mcp_servers


@pytest.mark.asyncio
async def test_workflow_state_persistence():
    from orchestrator.workflows.runner import WorkflowRunner

    runner = WorkflowRunner()
    result = await runner.run("help with loan application", {"amount": 50000})
    assert result["workflow_id"]
    assert result["agent"] == "loan-agent"

    from uuid import UUID
    from orchestrator.state_management.store import state_store

    state = await state_store.get(UUID(result["workflow_id"]))
    assert state is not None
    assert state.status in ("completed", "running")
