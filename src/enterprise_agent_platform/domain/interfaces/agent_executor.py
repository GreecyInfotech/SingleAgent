from abc import ABC, abstractmethod

from enterprise_agent_platform.domain.models import (
    Agent,
    AgentExecutionResult,
    Conversation,
    Message,
)


class AgentExecutor(ABC):
    @abstractmethod
    async def execute(
        self,
        agent: Agent,
        conversation: Conversation,
        messages: list[Message],
        user_input: str,
    ) -> AgentExecutionResult: ...
