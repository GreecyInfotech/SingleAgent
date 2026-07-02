from pydantic import BaseModel


class ParsedDocument(BaseModel):
    filename: str
    content_type: str
    text: str
    metadata: dict
    pages: int = 1


class DocumentParserTool:
    SUPPORTED_TYPES = {
        "application/pdf": "pdf",
        "text/plain": "text",
        "text/markdown": "markdown",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    }

    async def parse(self, filename: str, content: bytes, content_type: str) -> ParsedDocument:
        doc_type = self.SUPPORTED_TYPES.get(content_type, "unknown")
        text = content.decode("utf-8", errors="replace") if doc_type == "text" else f"[{doc_type} content]"

        return ParsedDocument(
            filename=filename,
            content_type=content_type,
            text=text,
            metadata={"type": doc_type, "size_bytes": len(content)},
            pages=1,
        )
