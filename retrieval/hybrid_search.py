from __future__ import annotations


def search_context(query: str) -> list[str]:
    # Placeholder hybrid retrieval pipeline (BM25 + vectors) for production extension.
    knowledge = [
        "Orders require customer ID and SKU list.",
        "Payments are validated before shipment creation.",
        "Use Idempotency-Key for mutation endpoints.",
    ]
    return [item for item in knowledge if any(token in item.lower() for token in query.lower().split())]
