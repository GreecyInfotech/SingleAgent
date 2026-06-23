from typing import Any

from pydantic import BaseModel


class SearchResult(BaseModel):
    title: str
    snippet: str
    url: str
    score: float


class SearchTool:
    async def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        return [
            SearchResult(
                title=f"Result {i + 1} for: {query}",
                snippet=f"Relevant content matching '{query}'",
                url=f"https://internal/search/{i}",
                score=0.95 - i * 0.1,
            )
            for i in range(min(limit, 5))
        ]

    async def search_enterprise(
        self, query: str, sources: list[str] | None = None
    ) -> dict[str, Any]:
        results = await self.search(query)
        return {
            "query": query,
            "sources": sources or ["kb", "confluence", "jira"],
            "results": [r.model_dump() for r in results],
        }
