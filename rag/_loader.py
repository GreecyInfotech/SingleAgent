import importlib.util
from pathlib import Path


def load_module(relative_path: str, module_name: str):
    base = Path(__file__).parent.parent
    path = base / relative_path
    if path.is_dir():
        path = path / "__init__.py"
        if not path.exists():
            path = base / relative_path.replace("-", "_") / "__init__.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {relative_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
