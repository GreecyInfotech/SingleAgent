from __future__ import annotations

from retrieval.hybrid_search import search_context


def route_query(message: str) -> tuple[str, list[str]]:
    msg = message.lower()
    if "order" in msg or "cancel" in msg:
        route = "order_agent"
    elif "inventory" in msg or "stock" in msg:
        route = "inventory_agent"
    else:
        route = "knowledge_agent"
    return route, search_context(message)
