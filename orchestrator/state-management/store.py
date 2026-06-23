from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class WorkflowState(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    workflow_name: str
    current_step: str = "init"
    status: str = "running"
    data: dict[str, Any] = Field(default_factory=dict)
    history: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class StateStore:
    """In-memory workflow state store (replace with Redis in production)."""

    def __init__(self) -> None:
        self._states: dict[UUID, WorkflowState] = {}

    async def create(self, workflow_name: str, initial_data: dict[str, Any] | None = None) -> WorkflowState:
        state = WorkflowState(workflow_name=workflow_name, data=initial_data or {})
        self._states[state.id] = state
        return state

    async def get(self, state_id: UUID) -> WorkflowState | None:
        return self._states.get(state_id)

    async def update(
        self,
        state_id: UUID,
        step: str,
        data: dict[str, Any] | None = None,
        status: str = "running",
    ) -> WorkflowState | None:
        state = self._states.get(state_id)
        if not state:
            return None
        state.current_step = step
        state.status = status
        state.updated_at = datetime.now(UTC)
        if data:
            state.data.update(data)
        state.history.append({"step": step, "timestamp": state.updated_at.isoformat()})
        return state

    async def complete(self, state_id: UUID, result: dict[str, Any]) -> WorkflowState | None:
        return await self.update(state_id, "completed", result, status="completed")


state_store = StateStore()
