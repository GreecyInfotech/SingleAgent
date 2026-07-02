from pydantic import BaseModel


class PDFPage(BaseModel):
    page_number: int
    text: str


class PDFDocument(BaseModel):
    filename: str
    pages: list[PDFPage]
    total_pages: int
    metadata: dict


class PDFTool:
    async def extract_text(self, content: bytes, filename: str = "document.pdf") -> PDFDocument:
        # Production: use pypdf or pdfplumber
        text = "[PDF text extraction placeholder - integrate pypdf in production]"
        return PDFDocument(
            filename=filename,
            pages=[PDFPage(page_number=1, text=text)],
            total_pages=1,
            metadata={"size_bytes": len(content)},
        )

    async def extract_tables(self, content: bytes) -> list[dict]:
        return []
