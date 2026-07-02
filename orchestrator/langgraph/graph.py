from typing import Annotated, Any, Literal, TypedDict

from langgraph.graph import END, StateGraph


class OrchestratorState(TypedDict):
    messages: list[dict[str, Any]]
    current_agent: str | None
    intent: str | None
    context: dict[str, Any]
    result: dict[str, Any] | None
    error: str | None


def route_intent(state: OrchestratorState) -> OrchestratorState:
    """Classify user intent and select target agent."""
    last_message = state["messages"][-1]["content"].lower() if state["messages"] else ""

    intent_map: dict[str, str] = {
        "loan": "loan-agent",
        "credit": "loan-agent",
        "fraud": "fraud-agent",
        "suspicious": "fraud-agent",
        "support": "support-agent",
        "ticket": "support-agent",
        "recommend": "recommendation-agent",
        "suggest": "recommendation-agent",
    }

    intent = "customer_inquiry"
    agent = "customer-agent"

    for keyword, target_agent in intent_map.items():
        if keyword in last_message:
            intent = keyword
            agent = target_agent
            break

    return {**state, "intent": intent, "current_agent": agent}


async def execute_agent(state: OrchestratorState) -> OrchestratorState:
    """Execute the selected domain agent."""
    from agents import get_agent

    agent_name = state.get("current_agent", "customer-agent")
    try:
        agent = get_agent(agent_name)
        input_data = {
            "query": state["messages"][-1]["content"] if state["messages"] else "",
            **state.get("context", {}),
        }
        result = await agent.process(input_data)
        return {**state, "result": result, "error": None}
    except Exception as e:
        return {**state, "error": str(e), "result": None}


def should_continue(state: OrchestratorState) -> Literal["execute", "end"]:
    if state.get("error"):
        return "end"
    return "execute"


def build_orchestrator_graph() -> StateGraph:
    """Build LangGraph orchestration workflow."""
    graph = StateGraph(OrchestratorState)

    graph.add_node("route", route_intent)
    graph.add_node("execute", execute_agent)

    graph.set_entry_point("route")
    graph.add_edge("route", "execute")
    graph.add_edge("execute", END)

    return graph


def compile_orchestrator():
    return build_orchestrator_graph().compile()
