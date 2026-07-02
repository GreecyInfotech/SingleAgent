from __future__ import annotations


def plan_response(route: str, message: str, context: list[str]) -> tuple[str, float]:
    context_block = " | ".join(context) if context else "No matching knowledge."
    answer = f"[{route}] {message.strip()} :: {context_block}"
    confidence = 0.72 if context else 0.51
    return answer, confidence
