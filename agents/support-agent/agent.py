from typing import Any

from agents.shared.base import BaseEnterpriseAgent
from agents.shared.config_loader import load_agent_config

SUPPORT_SYSTEM_PROMPT = """You are an Enterprise Support Agent.
Your responsibilities:
- Resolve customer and employee support tickets
- Search knowledge base articles and documentation
- Create and update Jira tickets for unresolved issues
- Escalate to human agents for complex or sensitive cases

Be empathetic, concise, and solution-oriented.
Always provide ticket references when creating or updating issues."""


class SupportAgent(BaseEnterpriseAgent):
    def __init__(self) -> None:
        super().__init__(
            load_agent_config(
                "support-agent",
                {
                    "name": "support-agent",
                    "description": "Enterprise IT and customer support automation",
                    "system_prompt": SUPPORT_SYSTEM_PROMPT,
                    "tools": ["search", "email", "document_parser"],
                    "mcp_servers": ["jira", "confluence", "github"],
                    "rag_enabled": True,
                    "metadata": {"domain": "support", "version": "1.0.0"},
                },
            )
        )

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        ticket_id = input_data.get("ticket_id")
        query = input_data.get("query", "")
        priority = input_data.get("priority", "medium")
        actions: list[str] = []

        kb_results = await self.search_knowledge(query) if query else []
        if kb_results:
            actions.append("rag_search")

        resolution = self._attempt_resolution(query)
        actions.extend(resolution["actions"])

        jira_issue = None
        if resolution["type"] == "investigation" and "jira" in self.config.mcp_servers:
            jira_issue = await self.invoke_mcp(
                "jira",
                "create_issue",
                {"project": "SUP", "summary": query[:100], "description": query},
            )
            actions.append("create_jira_ticket")

        email_result = None
        if resolution["type"] == "self_service" and input_data.get("email"):
            email_result = await self._services.send_email(
                to=[input_data["email"]],
                subject="Password Reset Instructions",
                body=resolution["answer"],
            )
            actions.append("send_email")

        escalated = resolution["confidence"] < float(
            self.config.metadata.get("confidence_threshold", 0.6)
        )

        response = (
            f"Ticket {ticket_id or 'NEW'}: {resolution['answer']} "
            f"(confidence={resolution['confidence']:.0%})"
        )

        return self._build_response(
            input_data=input_data,
            response=response,
            confidence=resolution["confidence"],
            actions=actions,
            extra={
                "ticket_id": ticket_id,
                "priority": priority,
                "resolution_type": resolution["type"],
                "escalated": escalated,
                "jira_issue": jira_issue,
                "email_result": email_result,
                "kb_hits": len(kb_results),
            },
        )

    def _attempt_resolution(self, query: str) -> dict[str, Any]:
        query_lower = query.lower()
        if "password" in query_lower or "reset" in query_lower:
            return {
                "type": "self_service",
                "answer": "Direct user to password reset portal at /reset",
                "confidence": 0.95,
                "actions": ["send_reset_link"],
            }
        if "error" in query_lower or "bug" in query_lower:
            return {
                "type": "investigation",
                "answer": "Creating Jira ticket for engineering review",
                "confidence": 0.7,
                "actions": ["search_confluence"],
            }
        return {
            "type": "knowledge_search",
            "answer": "Searching knowledge base for relevant articles",
            "confidence": 0.5,
            "actions": ["escalate_if_unresolved"],
        }
