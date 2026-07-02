from datetime import UTC, datetime
from uuid import UUID

from enterprise_agent_platform.application.dto.schemas import (
    ChatResponse,
    ConversationResponse,
    CreateConversationRequest,
    MessageResponse,
)
from enterprise_agent_platform.core.config import Settings
from enterprise_agent_platform.core.exceptions import NotFoundError
from enterprise_agent_platform.domain.interfaces import (
    AgentExecutor,
    AgentRepository,
    ConversationRepository,
    MessageRepository,
)
from enterprise_agent_platform.domain.models import Conversation, Message, MessageRole


class ConversationService:
    def __init__(
        self,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
        agent_repo: AgentRepository,
        agent_executor: AgentExecutor,
        settings: Settings,
    ) -> None:
        self._conversation_repo = conversation_repo
        self._message_repo = message_repo
        self._agent_repo = agent_repo
        self._executor = agent_executor
        self._settings = settings

    async def create(self, request: CreateConversationRequest) -> ConversationResponse:
        agent = await self._agent_repo.get_by_id(request.agent_id)
        if not agent:
            raise NotFoundError("Agent", str(request.agent_id))

        conversation = Conversation(
            agent_id=request.agent_id,
            user_id=request.user_id,
            title=request.title,
            metadata=request.metadata,
        )
        created = await self._conversation_repo.create(conversation)
        return self._to_conversation_response(created)

    async def get(self, conversation_id: UUID) -> ConversationResponse:
        conversation = await self._conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundError("Conversation", str(conversation_id))
        return self._to_conversation_response(conversation)

    async def list_by_agent(
        self, agent_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[ConversationResponse]:
        conversations = await self._conversation_repo.list_by_agent(agent_id, skip, limit)
        return [self._to_conversation_response(c) for c in conversations]

    async def get_messages(self, conversation_id: UUID) -> list[MessageResponse]:
        if not await self._conversation_repo.get_by_id(conversation_id):
            raise NotFoundError("Conversation", str(conversation_id))
        messages = await self._message_repo.get_by_conversation(
            conversation_id, limit=self._settings.max_conversation_history
        )
        return [self._to_message_response(m) for m in messages]

    async def send_message(self, conversation_id: UUID, content: str) -> ChatResponse:
        conversation = await self._conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundError("Conversation", str(conversation_id))

        agent = await self._agent_repo.get_by_id(conversation.agent_id)
        if not agent:
            raise NotFoundError("Agent", str(conversation.agent_id))

        history = await self._message_repo.get_by_conversation(
            conversation_id, limit=self._settings.max_conversation_history
        )

        user_message = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=content,
        )
        saved_user_msg = await self._message_repo.create(user_message)

        result = await self._executor.execute(agent, conversation, history, content)
        saved_assistant_msg = await self._message_repo.create(result.message)

        conversation.updated_at = datetime.now(UTC)
        await self._conversation_repo.update(conversation)

        return ChatResponse(
            conversation=self._to_conversation_response(conversation),
            user_message=self._to_message_response(saved_user_msg),
            assistant_message=self._to_message_response(saved_assistant_msg),
            tool_calls_made=result.tool_calls_made,
            tokens_used=result.tokens_used,
            latency_ms=result.latency_ms,
        )

    @staticmethod
    def _to_conversation_response(conversation: Conversation) -> ConversationResponse:
        return ConversationResponse(
            id=conversation.id,
            agent_id=conversation.agent_id,
            user_id=conversation.user_id,
            title=conversation.title,
            status=conversation.status,
            metadata=conversation.metadata,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )

    @staticmethod
    def _to_message_response(message: Message) -> MessageResponse:
        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            tool_calls=message.tool_calls,
            metadata=message.metadata,
            created_at=message.created_at,
        )
