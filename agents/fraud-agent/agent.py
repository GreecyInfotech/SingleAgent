from typing import Any

from agents.shared.base import BaseEnterpriseAgent
from agents.shared.config_loader import load_agent_config

FRAUD_SYSTEM_PROMPT = """You are a Fraud Detection Agent for an enterprise financial platform.
Your responsibilities:
- Analyze transactions for anomalous patterns
- Score fraud risk using behavioral and transactional signals
- Flag suspicious activity for investigation
- Generate fraud investigation reports

Be conservative: false positives are preferable to missed fraud.
Always explain the signals that contributed to the risk score."""


class FraudAgent(BaseEnterpriseAgent):
    FRAUD_SIGNALS = {
        "unusual_amount": 0.3,
        "new_device": 0.2,
        "geo_mismatch": 0.35,
        "velocity_breach": 0.4,
        "blacklist_match": 0.8,
    }

    def __init__(self) -> None:
        super().__init__(
            load_agent_config(
                "fraud-agent",
                {
                    "name": "fraud-agent",
                    "description": "Real-time fraud detection and investigation",
                    "system_prompt": FRAUD_SYSTEM_PROMPT,
                    "temperature": 0.1,
                    "tools": ["search", "reporting", "get_transaction_history"],
                    "mcp_servers": ["postgres", "oracle"],
                    "metadata": {"domain": "fraud", "version": "1.0.0"},
                },
            )
        )

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        transaction_id = input_data.get("transaction_id", "TXN-UNKNOWN")
        signals = input_data.get("signals", [])
        risk_score, triggered = self._score_transaction(signals)
        action = self._determine_action(risk_score)
        actions = ["score_transaction", "determine_action"]

        report = await self._services.generate_report(
            title=f"Fraud Analysis - {transaction_id}",
            data={"transaction_id": transaction_id, "risk_score": risk_score, "signals": triggered},
        )
        actions.append("generate_report")

        if "postgres" in self.config.mcp_servers:
            await self.invoke_mcp(
                "postgres",
                "query",
                {"sql": "SELECT 1", "params": []},
            )
            actions.append("audit_log_query")

        response = (
            f"Transaction {transaction_id}: risk={risk_score:.2f}, action={action}. "
            f"Signals: {', '.join(triggered) or 'none'}."
        )

        return self._build_response(
            input_data=input_data,
            response=response,
            confidence=0.95,
            actions=actions,
            extra={
                "transaction_id": transaction_id,
                "risk_score": risk_score,
                "triggered_signals": triggered,
                "action": action,
                "investigation_required": risk_score >= float(
                    self.config.metadata.get("alert", 0.75)
                ),
                "report": report,
            },
        )

    def _score_transaction(self, signals: list[str]) -> tuple[float, list[str]]:
        score = 0.0
        triggered = []
        for signal in signals:
            weight = self.FRAUD_SIGNALS.get(signal, 0.1)
            score += weight
            triggered.append(signal)
        return round(min(score, 1.0), 2), triggered

    def _determine_action(self, risk_score: float) -> str:
        block_threshold = float(self.config.metadata.get("block", 0.90))
        alert_threshold = float(self.config.metadata.get("alert", 0.75))
        step_up_threshold = float(self.config.metadata.get("step_up_auth", 0.50))

        if risk_score >= block_threshold:
            return "block"
        if risk_score >= alert_threshold:
            return "hold_for_review"
        if risk_score >= step_up_threshold:
            return "step_up_auth"
        return "allow"
