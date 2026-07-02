from typing import Any
from uuid import UUID

from enterprise_agent_platform.application.dto.platform_schemas import OrchestrateRequest


class PlatformService:
    """Orchestrates domain agents, workflows, and MCP integrations."""

    async def list_domain_agents(self) -> dict[str, Any]:
        from agents import get_agent, list_agents

        agents = [get_agent(name).to_platform_agent() for name in list_agents()]
        return {"agents": agents, "count": len(agents)}

    async def get_domain_agent(self, agent_name: str) -> dict[str, Any]:
        from agents import get_agent

        return get_agent(agent_name).to_platform_agent()

    async def execute_domain_agent(
        self, agent_name: str, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        from agents import get_agent

        agent = get_agent(agent_name)
        return await agent.process(input_data)

    async def orchestrate(self, request: OrchestrateRequest) -> dict[str, Any]:
        from orchestrator.workflows.runner import WorkflowRunner

        runner = WorkflowRunner()
        return await runner.run(request.message, request.context)

    async def get_workflow_state(self, workflow_id: str) -> dict[str, Any]:
        from orchestrator.state_management.store import state_store

        state = await state_store.get(UUID(workflow_id))
        if not state:
            return {"error": "Workflow not found"}
        return state.model_dump(mode="json")

    async def list_mcp_servers(self) -> dict[str, Any]:
        from mcp_servers import get_mcp_server, list_mcp_servers

        servers = []
        for name in list_mcp_servers():
            server = get_mcp_server(name)
            tools = await server.list_tools()
            servers.append({**server.get_server_info(), "tools": [t["name"] for t in tools]})
        return {"servers": servers}

    async def call_mcp_tool(
        self, server_name: str, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        from mcp_servers import get_mcp_server

        server = get_mcp_server(server_name)
        result = await server.call_tool(tool_name, arguments)
        return {"server": server_name, "tool": tool_name, "result": result}
