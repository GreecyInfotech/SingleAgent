import importlib.util
from pathlib import Path

_path = Path(__file__).parent.parent / "document-parser" / "tool.py"
_spec = importlib.util.spec_from_file_location("tools.document_parser.tool", _path)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

DocumentParserTool = _mod.DocumentParserTool
ParsedDocument = _mod.ParsedDocument

__all__ = ["DocumentParserTool", "ParsedDocument"]
