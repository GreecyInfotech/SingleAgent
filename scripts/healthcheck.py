from __future__ import annotations

import sys

import httpx


def main() -> int:
    try:
        res = httpx.get("http://127.0.0.1:8000/health", timeout=3.0)
        print(res.json())
        return 0 if res.status_code == 200 else 1
    except Exception as exc:  # pragma: no cover
        print(f"healthcheck failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
