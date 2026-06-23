from typing import Any

from fastapi import APIRouter, Depends

from enterprise_agent_platform.api.deps import get_platform_service, verify_api_key
from enterprise_agent_platform.application.dto.platform_schemas import (
    AgentExecuteRequest,
    MCPToolRequest,
    OrchestrateRequest,
)
from enterprise_agent_platform.application.services.platform_service import PlatformService

router = APIRouter()


@router.get("/platform/agents")
async def list_domain_agents(
    service: PlatformService = Depends(get_platform_service),
    _: str = Depends(verify_api_key),
) -> dict[str, Any]:
    return await service.list_domain_agents()


@router.get("/platform/agents/{agent_name}")
async def get_domain_agent(
    agent_name: str,
    service: PlatformService = Depends(get_platform_service),
    _: str = Depends(verify_api_key),
) -> dict[str, Any]:
    return await service.get_domain_agent(agent_name)


@router.post("/platform/agents/{agent_name}/execute")
async def execute_domain_agent(
    agent_name: str,
    request: AgentExecuteRequest,
    service: PlatformService = Depends(get_platform_service),
    _: str = Depends(verify_api_key),
) -> dict[str, Any]:
    return await service.execute_domain_agent(agent_name, request.to_input())


@router.post("/platform/orchestrate")
async def orchestrate(
    request: OrchestrateRequest,
    service: PlatformService = Depends(get_platform_service),
    _: str = Depends(verify_api_key),
) -> dict[str, Any]:
    return await service.orchestrate(request)


@router.get("/platform/workflows/{workflow_id}")
async def get_workflow_state(
    workflow_id: str,
    service: PlatformService = Depends(get_platform_service),
    _: str = Depends(verify_api_key),
) -> dict[str, Any]:
    return await service.get_workflow_state(workflow_id)


@router.get("/platform/mcp-servers")
async def list_mcp(
    service: PlatformService = Depends(get_platform_service),
    _: str = Depends(verify_api_key),
) -> dict[str, Any]:
    return await service.list_mcp_servers()


@router.post("/platform/mcp-servers/{server_name}/tools/{tool_name}")
async def call_mcp_tool(
    server_name: str,
    tool_name: str,
    request: MCPToolRequest,
    service: PlatformService = Depends(get_platform_service),
    _: str = Depends(verify_api_key),
) -> dict[str, Any]:
    return await service.call_mcp_tool(server_name, tool_name, request.arguments)
