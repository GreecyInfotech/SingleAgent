from __future__ import annotations

from retrieval.hybrid_search import search_context

_ROUTE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("order_agent", ("order", "cancel")),
    ("inventory_agent", ("inventory", "stock")),
)


def route_query(message: str) -> tuple[str, list[str]]:
    msg = message.lower()
    route = next(
        (name for name, keywords in _ROUTE_RULES if any(keyword in msg for keyword in keywords)),
        "knowledge_agent",
    )
    return route, search_context(message)
