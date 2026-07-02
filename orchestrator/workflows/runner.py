from typing import Any
from uuid import UUID

from orchestrator.langgraph.graph import OrchestratorState, compile_orchestrator
from orchestrator.state_management.store import state_store


class WorkflowRunner:
    """Execute multi-step agent workflows with persisted state."""

    def __init__(self) -> None:
        self._graph = compile_orchestrator()

    async def run(
        self,
        message: str,
        context: dict[str, Any] | None = None,
        workflow_id: UUID | None = None,
    ) -> dict[str, Any]:
        workflow_state = await state_store.create("agent-orchestration", context or {})
        workflow_id = workflow_state.id

        initial_state: OrchestratorState = {
            "messages": [{"role": "user", "content": message}],
            "current_agent": None,
            "intent": None,
            "context": context or {},
            "result": None,
            "error": None,
        }

        await state_store.update(workflow_id, "routing", {"message": message})

        final_state = await self._graph.ainvoke(initial_state)

        if final_state.get("error"):
            await state_store.update(
                workflow_id,
                "failed",
                {"error": final_state["error"]},
                status="failed",
            )
        else:
            await state_store.complete(workflow_id, final_state.get("result") or {})

        return {
            "workflow_id": str(workflow_id),
            "agent": final_state.get("current_agent"),
            "intent": final_state.get("intent"),
            "result": final_state.get("result"),
            "error": final_state.get("error"),
        }
