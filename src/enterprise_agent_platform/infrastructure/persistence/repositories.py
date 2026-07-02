from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from enterprise_agent_platform.domain.interfaces import (
    AgentRepository,
    ConversationRepository,
    MessageRepository,
)
from enterprise_agent_platform.domain.models import Agent, Conversation, Message
from enterprise_agent_platform.infrastructure.persistence.models import (
    AgentORM,
    ConversationORM,
    MessageORM,
)


def _agent_to_domain(orm: AgentORM) -> Agent:
    return Agent(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        system_prompt=orm.system_prompt,
        model=orm.model,
        temperature=orm.temperature,
        max_tokens=orm.max_tokens,
        tools=orm.tools or [],
        status=orm.status,
        metadata=orm.metadata_ or {},
        created_at=orm.created_at,
        updated_at=orm.updated_at,
    )


def _conversation_to_domain(orm: ConversationORM) -> Conversation:
    return Conversation(
        id=orm.id,
        agent_id=orm.agent_id,
        user_id=orm.user_id,
        title=orm.title,
        status=orm.status,
        metadata=orm.metadata_ or {},
        created_at=orm.created_at,
        updated_at=orm.updated_at,
    )


def _message_to_domain(orm: MessageORM) -> Message:
    return Message(
        id=orm.id,
        conversation_id=orm.conversation_id,
        role=orm.role,
        content=orm.content,
        tool_calls=orm.tool_calls,
        tool_call_id=orm.tool_call_id,
        metadata=orm.metadata_ or {},
        created_at=orm.created_at,
    )


class SQLAgentRepository(AgentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, agent: Agent) -> Agent:
        orm = AgentORM(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            system_prompt=agent.system_prompt,
            model=agent.model,
            temperature=agent.temperature,
            max_tokens=agent.max_tokens,
            tools=agent.tools,
            status=agent.status,
            metadata_=agent.metadata,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return _agent_to_domain(orm)

    async def get_by_id(self, agent_id: UUID) -> Agent | None:
        result = await self._session.execute(select(AgentORM).where(AgentORM.id == agent_id))
        orm = result.scalar_one_or_none()
        return _agent_to_domain(orm) if orm else None

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Agent]:
        result = await self._session.execute(select(AgentORM).offset(skip).limit(limit))
        return [_agent_to_domain(orm) for orm in result.scalars().all()]

    async def update(self, agent: Agent) -> Agent:
        result = await self._session.execute(select(AgentORM).where(AgentORM.id == agent.id))
        orm = result.scalar_one()
        orm.name = agent.name
        orm.description = agent.description
        orm.system_prompt = agent.system_prompt
        orm.model = agent.model
        orm.temperature = agent.temperature
        orm.max_tokens = agent.max_tokens
        orm.tools = agent.tools
        orm.status = agent.status
        orm.metadata_ = agent.metadata
        await self._session.flush()
        return _agent_to_domain(orm)

    async def delete(self, agent_id: UUID) -> bool:
        result = await self._session.execute(delete(AgentORM).where(AgentORM.id == agent_id))
        return result.rowcount > 0  # type: ignore[union-attr]


class SQLConversationRepository(ConversationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, conversation: Conversation) -> Conversation:
        orm = ConversationORM(
            id=conversation.id,
            agent_id=conversation.agent_id,
            user_id=conversation.user_id,
            title=conversation.title,
            status=conversation.status,
            metadata_=conversation.metadata,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return _conversation_to_domain(orm)

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        result = await self._session.execute(
            select(ConversationORM).where(ConversationORM.id == conversation_id)
        )
        orm = result.scalar_one_or_none()
        return _conversation_to_domain(orm) if orm else None

    async def list_by_agent(
        self, agent_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Conversation]:
        result = await self._session.execute(
            select(ConversationORM)
            .where(ConversationORM.agent_id == agent_id)
            .offset(skip)
            .limit(limit)
        )
        return [_conversation_to_domain(orm) for orm in result.scalars().all()]

    async def update(self, conversation: Conversation) -> Conversation:
        result = await self._session.execute(
            select(ConversationORM).where(ConversationORM.id == conversation.id)
        )
        orm = result.scalar_one()
        orm.title = conversation.title
        orm.status = conversation.status
        orm.metadata_ = conversation.metadata
        await self._session.flush()
        return _conversation_to_domain(orm)


class SQLMessageRepository(MessageRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, message: Message) -> Message:
        orm = MessageORM(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            tool_calls=message.tool_calls,
            tool_call_id=message.tool_call_id,
            metadata_=message.metadata,
            created_at=message.created_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return _message_to_domain(orm)

    async def get_by_conversation(self, conversation_id: UUID, limit: int = 50) -> list[Message]:
        result = await self._session.execute(
            select(MessageORM)
            .where(MessageORM.conversation_id == conversation_id)
            .order_by(MessageORM.created_at)
            .limit(limit)
        )
        return [_message_to_domain(orm) for orm in result.scalars().all()]
