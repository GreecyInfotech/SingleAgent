from typing import Any

from agents.shared.base import BaseEnterpriseAgent
from agents.shared.config_loader import load_agent_config

RECOMMENDATION_SYSTEM_PROMPT = """You are a Recommendation Agent for an enterprise platform.
Your responsibilities:
- Generate personalized product and content recommendations
- Analyze user behavior and preferences
- Apply business rules and compliance filters to recommendations
- Explain why each recommendation was made

Balance relevance with diversity. Respect user privacy preferences."""


class RecommendationAgent(BaseEnterpriseAgent):
    def __init__(self) -> None:
        super().__init__(
            load_agent_config(
                "recommendation-agent",
                {
                    "name": "recommendation-agent",
                    "description": "Personalized product and content recommendations",
                    "system_prompt": RECOMMENDATION_SYSTEM_PROMPT,
                    "tools": ["search", "get_user_preferences", "reporting"],
                    "mcp_servers": ["salesforce", "postgres"],
                    "rag_enabled": True,
                    "metadata": {"domain": "recommendations", "version": "1.0.0"},
                },
            )
        )

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        user_id = input_data.get("user_id", "anonymous")
        context = input_data.get("context", "general")
        limit = int(input_data.get("limit", self.config.metadata.get("limit", 5)))
        actions = ["load_catalog"]

        catalog_docs = await self.search_knowledge(f"product recommendations {context}")
        actions.append("rag_product_search")

        account = None
        if user_id != "anonymous" and "salesforce" in self.config.mcp_servers:
            account = await self.invoke_mcp(
                "salesforce",
                "get_account",
                {"account_id": user_id},
            )
            actions.append("fetch_salesforce_account")

        recommendations = self._generate_recommendations(user_id, context, limit, catalog_docs)

        response = (
            f"Generated {len(recommendations)} recommendations for user {user_id} "
            f"in context '{context}'."
        )

        return self._build_response(
            input_data=input_data,
            response=response,
            confidence=0.9 if account else 0.8,
            actions=actions,
            extra={
                "user_id": user_id,
                "context": context,
                "recommendations": recommendations,
                "algorithm": self.config.metadata.get("algorithm", "hybrid_collaborative_content"),
                "account": account,
            },
        )

    def _generate_recommendations(
        self,
        user_id: str,
        context: str,
        limit: int,
        catalog_docs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        catalog = [
            {"id": "prod-001", "name": "Enterprise Analytics Suite", "score": 0.94},
            {"id": "prod-002", "name": "AI Agent Platform", "score": 0.91},
            {"id": "prod-003", "name": "Compliance Dashboard", "score": 0.87},
            {"id": "prod-004", "name": "Customer 360 View", "score": 0.85},
            {"id": "prod-005", "name": "Fraud Detection Module", "score": 0.82},
        ]
        if context == "lending":
            catalog = [p for p in catalog if "Compliance" in p["name"] or "Fraud" in p["name"]]

        boost = 0.02 * len(catalog_docs)
        return [
            {
                **item,
                "score": round(min(item["score"] + boost, 1.0), 2),
                "reason": f"Based on profile similarity for user {user_id}",
            }
            for item in catalog[:limit]
        ]
