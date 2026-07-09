from __future__ import annotations

import csv
import io
from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


class DocumentParser:
    """Extract plain text from supported document formats."""

    def parse(self, content: bytes, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        if ext == ".pdf":
            return self._parse_pdf(content)
        if ext == ".docx":
            return self._parse_docx(content)
        if ext == ".csv":
            return self._parse_csv(content)
        raise ValueError(f"Unsupported format: {ext}")

    @staticmethod
    def _parse_pdf(content: bytes) -> str:
        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()

    @staticmethod
    def _parse_docx(content: bytes) -> str:
        doc = DocxDocument(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()

    @staticmethod
    def _parse_csv(content: bytes) -> str:
        text = content.decode("utf-8", errors="replace")
        reader = csv.reader(io.StringIO(text))
        rows = [" | ".join(cell.strip() for cell in row) for row in reader if any(row)]
        return "\n".join(rows).strip()


document_parser = DocumentParser()
