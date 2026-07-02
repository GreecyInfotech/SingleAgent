from abc import ABC, abstractmethod
from uuid import UUID

from enterprise_agent_platform.domain.models import Agent, Conversation, Message


class AgentRepository(ABC):
    @abstractmethod
    async def create(self, agent: Agent) -> Agent: ...

    @abstractmethod
    async def get_by_id(self, agent_id: UUID) -> Agent | None: ...

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Agent]: ...

    @abstractmethod
    async def update(self, agent: Agent) -> Agent: ...

    @abstractmethod
    async def delete(self, agent_id: UUID) -> bool: ...


class ConversationRepository(ABC):
    @abstractmethod
    async def create(self, conversation: Conversation) -> Conversation: ...

    @abstractmethod
    async def get_by_id(self, conversation_id: UUID) -> Conversation | None: ...

    @abstractmethod
    async def list_by_agent(
        self, agent_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Conversation]: ...

    @abstractmethod
    async def update(self, conversation: Conversation) -> Conversation: ...


class MessageRepository(ABC):
    @abstractmethod
    async def create(self, message: Message) -> Message: ...

    @abstractmethod
    async def get_by_conversation(
        self, conversation_id: UUID, limit: int = 50
    ) -> list[Message]: ...
