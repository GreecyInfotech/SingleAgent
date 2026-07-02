from datetime import UTC, datetime
from uuid import UUID

from enterprise_agent_platform.application.dto.schemas import (
    AgentResponse,
    CreateAgentRequest,
    UpdateAgentRequest,
)
from enterprise_agent_platform.core.config import Settings
from enterprise_agent_platform.core.exceptions import NotFoundError
from enterprise_agent_platform.domain.interfaces import AgentRepository
from enterprise_agent_platform.domain.models import Agent


class AgentService:
    def __init__(self, agent_repo: AgentRepository, settings: Settings) -> None:
        self._repo = agent_repo
        self._settings = settings

    async def create(self, request: CreateAgentRequest) -> AgentResponse:
        agent = Agent(
            name=request.name,
            description=request.description,
            system_prompt=request.system_prompt,
            model=request.model or self._settings.openai_model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            tools=request.tools,
            metadata=request.metadata,
        )
        created = await self._repo.create(agent)
        return self._to_response(created)

    async def get(self, agent_id: UUID) -> AgentResponse:
        agent = await self._repo.get_by_id(agent_id)
        if not agent:
            raise NotFoundError("Agent", str(agent_id))
        return self._to_response(agent)

    async def list_agents(self, skip: int = 0, limit: int = 100) -> list[AgentResponse]:
        agents = await self._repo.list_all(skip=skip, limit=limit)
        return [self._to_response(a) for a in agents]

    async def update(self, agent_id: UUID, request: UpdateAgentRequest) -> AgentResponse:
        agent = await self._repo.get_by_id(agent_id)
        if not agent:
            raise NotFoundError("Agent", str(agent_id))

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        agent.updated_at = datetime.now(UTC)

        updated = await self._repo.update(agent)
        return self._to_response(updated)

    async def delete(self, agent_id: UUID) -> bool:
        if not await self._repo.get_by_id(agent_id):
            raise NotFoundError("Agent", str(agent_id))
        return await self._repo.delete(agent_id)

    async def get_domain_agent(self, agent_id: UUID) -> Agent:
        agent = await self._repo.get_by_id(agent_id)
        if not agent:
            raise NotFoundError("Agent", str(agent_id))
        return agent

    @staticmethod
    def _to_response(agent: Agent) -> AgentResponse:
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            system_prompt=agent.system_prompt,
            model=agent.model,
            temperature=agent.temperature,
            max_tokens=agent.max_tokens,
            tools=agent.tools,
            status=agent.status,
            metadata=agent.metadata,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
        )
