from typing import Any

from agents.shared.base import BaseEnterpriseAgent
from agents.shared.config_loader import load_agent_config
from agents.shared.services import agent_services

CUSTOMER_SYSTEM_PROMPT = """You are a Customer Intelligence Agent for an enterprise platform.
Your responsibilities:
- Analyze customer profiles, segments, and lifecycle stages
- Provide personalized recommendations based on customer history
- Answer questions about customer accounts, preferences, and interactions
- Escalate complex issues to human agents when confidence is low

Always protect customer PII. Mask sensitive data in responses.
Use available tools to fetch real customer data before answering."""


class CustomerAgent(BaseEnterpriseAgent):
    def __init__(self) -> None:
        super().__init__(
            load_agent_config(
                "customer-agent",
                {
                    "name": "customer-agent",
                    "description": "Customer intelligence, segmentation, and personalization",
                    "system_prompt": CUSTOMER_SYSTEM_PROMPT,
                    "tools": ["search", "get_customer_profile", "get_interaction_history"],
                    "mcp_servers": ["salesforce", "postgres"],
                    "rag_enabled": True,
                    "metadata": {"domain": "customer", "version": "1.0.0"},
                },
            )
        )

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        customer_id = input_data.get("customer_id", "unknown")
        query = input_data.get("query", "")
        intent = self._classify_intent(query)
        actions: list[str] = ["classify_intent"]

        profile = None
        if customer_id and "salesforce" in self.config.mcp_servers:
            profile = await self.invoke_mcp(
                "salesforce",
                "get_account",
                {"account_id": customer_id},
            )
            actions.append("fetch_salesforce_account")

        kb_results = []
        if self.config.rag_enabled and query:
            kb_results = await self.search_knowledge(query)
            actions.append("rag_search")

        search_results = await self.search(query) if query else {"results": []}
        actions.append("enterprise_search")

        response = (
            f"Customer {customer_id}: intent={intent}. "
            f"Profile: {profile['Name'] if profile else 'N/A'}. "
            f"KB hits: {len(kb_results)}. Search hits: {len(search_results.get('results', []))}."
        )

        return self._build_response(
            input_data=input_data,
            response=response,
            confidence=0.92 if profile else 0.75,
            actions=actions,
            extra={"intent": intent, "customer_id": customer_id, "profile": profile},
        )

    def _classify_intent(self, query: str) -> str:
        query_lower = query.lower()
        if "segment" in query_lower:
            return "segmentation"
        if "history" in query_lower or "interaction" in query_lower:
            return "interaction_history"
        if "recommend" in query_lower:
            return "recommendation"
        return "general_inquiry"
