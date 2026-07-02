from __future__ import annotations

import re


PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"system\s+prompt",
    r"reveal\s+secrets?",
]


def is_safe_user_input(text: str) -> bool:
    lowered = text.lower()
    return not any(re.search(pattern, lowered) for pattern in PROMPT_INJECTION_PATTERNS)
