import importlib.util
from pathlib import Path

_path = Path(__file__).parent.parent / "vector-db" / "client.py"
_spec = importlib.util.spec_from_file_location("rag.vector_db.client", _path)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

VectorDBClient = _mod.VectorDBClient
VectorDocument = _mod.VectorDocument

__all__ = ["VectorDBClient", "VectorDocument"]
