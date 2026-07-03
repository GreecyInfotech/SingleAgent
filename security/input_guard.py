from __future__ import annotations

import re

PROMPT_INJECTION_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"ignore\s+previous\s+instructions",
        r"system\s+prompt",
        r"reveal\s+secrets?",
    )
)


def is_safe_user_input(text: str) -> bool:
    return not any(pattern.search(text) for pattern in PROMPT_INJECTION_PATTERNS)
