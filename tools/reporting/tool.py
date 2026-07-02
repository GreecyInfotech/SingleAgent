from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class ReportSection(BaseModel):
    title: str
    content: str
    data: dict[str, Any] = Field(default_factory=dict)


class Report(BaseModel):
    title: str
    sections: list[ReportSection]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    format: str = "json"


class ReportingTool:
    async def generate(
        self,
        title: str,
        data: dict[str, Any],
        template: str = "default",
    ) -> Report:
        sections = [
            ReportSection(title="Summary", content=f"Report: {title}", data={"template": template}),
            ReportSection(title="Metrics", content="Key metrics", data=data),
        ]
        return Report(title=title, sections=sections)

    async def export(self, report: Report, format: str = "json") -> dict:
        return {
            "format": format,
            "title": report.title,
            "generated_at": report.generated_at.isoformat(),
            "content": report.model_dump(),
        }
