from uuid import UUID

from fastapi import APIRouter, Depends, Query

from enterprise_agent_platform.api.deps import (
    get_agent_service,
    get_conversation_service,
    get_tool_registry,
    handle_platform_error,
    verify_api_key,
)
from enterprise_agent_platform.application.dto.schemas import (
    AgentResponse,
    ChatResponse,
    ConversationResponse,
    CreateAgentRequest,
    CreateConversationRequest,
    MessageResponse,
    SendMessageRequest,
    ToolResponse,
    UpdateAgentRequest,
)
from enterprise_agent_platform.application.services.agent_service import AgentService
from enterprise_agent_platform.application.services.conversation_service import ConversationService
from enterprise_agent_platform.core.exceptions import PlatformError
from enterprise_agent_platform.infrastructure.agents.tool_registry import ToolRegistry

router = APIRouter()


@router.post("/agents", response_model=AgentResponse, status_code=201)
async def create_agent(
    request: CreateAgentRequest,
    service: AgentService = Depends(get_agent_service),
    _: str = Depends(verify_api_key),
) -> AgentResponse:
    try:
        return await service.create(request)
    except PlatformError as e:
        raise handle_platform_error(e) from e


@router.get("/agents", response_model=list[AgentResponse])
async def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: AgentService = Depends(get_agent_service),
    _: str = Depends(verify_api_key),
) -> list[AgentResponse]:
    return await service.list_agents(skip=skip, limit=limit)


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    service: AgentService = Depends(get_agent_service),
    _: str = Depends(verify_api_key),
) -> AgentResponse:
    try:
        return await service.get(agent_id)
    except PlatformError as e:
        raise handle_platform_error(e) from e


@router.patch("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    request: UpdateAgentRequest,
    service: AgentService = Depends(get_agent_service),
    _: str = Depends(verify_api_key),
) -> AgentResponse:
    try:
        return await service.update(agent_id, request)
    except PlatformError as e:
        raise handle_platform_error(e) from e


@router.delete("/agents/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: UUID,
    service: AgentService = Depends(get_agent_service),
    _: str = Depends(verify_api_key),
) -> None:
    try:
        await service.delete(agent_id)
    except PlatformError as e:
        raise handle_platform_error(e) from e


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    request: CreateConversationRequest,
    service: ConversationService = Depends(get_conversation_service),
    _: str = Depends(verify_api_key),
) -> ConversationResponse:
    try:
        return await service.create(request)
    except PlatformError as e:
        raise handle_platform_error(e) from e


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    service: ConversationService = Depends(get_conversation_service),
    _: str = Depends(verify_api_key),
) -> ConversationResponse:
    try:
        return await service.get(conversation_id)
    except PlatformError as e:
        raise handle_platform_error(e) from e


@router.get("/agents/{agent_id}/conversations", response_model=list[ConversationResponse])
async def list_agent_conversations(
    agent_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: ConversationService = Depends(get_conversation_service),
    _: str = Depends(verify_api_key),
) -> list[ConversationResponse]:
    return await service.list_by_agent(agent_id, skip=skip, limit=limit)


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    conversation_id: UUID,
    service: ConversationService = Depends(get_conversation_service),
    _: str = Depends(verify_api_key),
) -> list[MessageResponse]:
    try:
        return await service.get_messages(conversation_id)
    except PlatformError as e:
        raise handle_platform_error(e) from e


@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: UUID,
    request: SendMessageRequest,
    service: ConversationService = Depends(get_conversation_service),
    _: str = Depends(verify_api_key),
) -> ChatResponse:
    try:
        return await service.send_message(conversation_id, request.content)
    except PlatformError as e:
        raise handle_platform_error(e) from e


@router.get("/tools", response_model=list[ToolResponse])
async def list_tools(
    registry: ToolRegistry = Depends(get_tool_registry),
    _: str = Depends(verify_api_key),
) -> list[ToolResponse]:
    return [
        ToolResponse(
            name=t.name,
            description=t.description,
            parameters=t.parameters,
        )
        for t in registry.list_tools()
    ]
