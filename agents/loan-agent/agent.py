from typing import Any

from agents.shared.base import BaseEnterpriseAgent
from agents.shared.config_loader import load_agent_config

LOAN_SYSTEM_PROMPT = """You are a Loan Processing Agent for an enterprise financial platform.
Your responsibilities:
- Evaluate loan applications against credit policies
- Calculate debt-to-income ratios and risk scores
- Guide applicants through required documentation
- Route applications for manual review when risk thresholds are exceeded

Never approve loans autonomously above configured limits.
Always cite the policy rules used in your assessment."""


class LoanAgent(BaseEnterpriseAgent):
    def __init__(self) -> None:
        super().__init__(
            load_agent_config(
                "loan-agent",
                {
                    "name": "loan-agent",
                    "description": "Loan application processing and risk assessment",
                    "system_prompt": LOAN_SYSTEM_PROMPT,
                    "temperature": 0.3,
                    "tools": ["calculate_dti", "check_credit_score", "document_parser", "pdf"],
                    "mcp_servers": ["oracle", "postgres", "sap"],
                    "rag_enabled": True,
                    "metadata": {"domain": "lending", "version": "1.0.0"},
                },
            )
        )

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        application_id = input_data.get("application_id", "APP-UNKNOWN")
        amount = float(input_data.get("amount", 0))
        income = float(input_data.get("annual_income", 0))
        debt = float(input_data.get("monthly_debt", 0))

        dti = self._calculate_dti(income, debt, amount)
        risk_score = self._assess_risk(dti, amount)
        max_auto = float(self.config.metadata.get("max_auto_approve", 50000))
        max_dti = float(self.config.metadata.get("max_dti", 0.43))

        actions = ["calculate_dti", "assess_risk"]
        policy_hits = await self.search_knowledge(f"loan policy DTI {dti}")
        actions.append("rag_policy_lookup")

        customer = None
        if input_data.get("customer_id") and "oracle" in self.config.mcp_servers:
            customer = await self.invoke_mcp(
                "oracle",
                "get_customer",
                {"customer_id": input_data["customer_id"]},
            )
            actions.append("fetch_oracle_customer")

        if dti > max_dti or amount > max_auto or risk_score > 0.7:
            decision = "manual_review"
        else:
            decision = "pre_approved"

        response = (
            f"Application {application_id}: DTI={dti:.2%}, risk={risk_score:.2f}, "
            f"decision={decision}. Policies matched: {len(policy_hits)}."
        )

        return self._build_response(
            input_data=input_data,
            response=response,
            confidence=0.88,
            actions=actions,
            extra={
                "application_id": application_id,
                "dti_ratio": dti,
                "risk_score": risk_score,
                "decision": decision,
                "required_documents": ["income_proof", "identity", "bank_statements"],
                "customer": customer,
            },
        )

    def _calculate_dti(self, income: float, debt: float, loan_amount: float) -> float:
        if income <= 0:
            return 1.0
        monthly_income = income / 12
        estimated_payment = loan_amount * 0.02
        return round((debt + estimated_payment) / monthly_income, 3)

    def _assess_risk(self, dti: float, amount: float) -> float:
        base = min(dti, 1.0) * 0.6
        if amount > 100000:
            base += 0.2
        return round(min(base, 1.0), 2)
