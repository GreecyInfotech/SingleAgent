import time
from typing import Any

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from enterprise_agent_platform.core.config import Settings
from enterprise_agent_platform.core.exceptions import AgentExecutionError
from enterprise_agent_platform.core.logging import get_logger
from enterprise_agent_platform.domain.interfaces import AgentExecutor
from enterprise_agent_platform.domain.models import (
    Agent,
    AgentExecutionResult,
    Conversation,
    Message,
    MessageRole,
)
from enterprise_agent_platform.infrastructure.agents.tool_registry import ToolRegistry

logger = get_logger(__name__)


class LLMAgentExecutor(AgentExecutor):
    """Executes agents using OpenAI-compatible LLM APIs with tool calling."""

    def __init__(self, settings: Settings, tool_registry: ToolRegistry) -> None:
        self._settings = settings
        self._tools = tool_registry
        client_kwargs: dict[str, Any] = {"api_key": settings.openai_api_key}
        if settings.openai_base_url:
            client_kwargs["base_url"] = settings.openai_base_url
        self._client = AsyncOpenAI(**client_kwargs)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def _call_llm(
        self,
        model: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
        temperature: float,
        max_tokens: int,
    ) -> Any:
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        return await self._client.chat.completions.create(**kwargs)

    async def execute(
        self,
        agent: Agent,
        conversation: Conversation,
        messages: list[Message],
        user_input: str,
    ) -> AgentExecutionResult:
        start = time.perf_counter()
        tool_calls_made: list[str] = []

        llm_messages = self._build_messages(agent, messages, user_input)
        tool_schemas = self._tools.get_tool_schemas(agent.tools) if agent.tools else None

        try:
            response = await self._call_llm(
                model=agent.model,
                messages=llm_messages,
                tools=tool_schemas,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens,
            )
        except Exception as e:
            logger.error("llm_call_failed", agent_id=str(agent.id), error=str(e))
            raise AgentExecutionError(
                message=f"LLM call failed: {e}",
                agent_id=str(agent.id),
            ) from e

        choice = response.choices[0]
        assistant_message = choice.message
        tokens_used = response.usage.total_tokens if response.usage else 0

        # Handle tool calls iteratively (max 5 rounds)
        for _ in range(5):
            if not assistant_message.tool_calls:
                break

            llm_messages.append(assistant_message.model_dump())

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_calls_made.append(tool_name)
                import json

                args = json.loads(tool_call.function.arguments)
                tool_result = await self._tools.execute(tool_name, args)

                llm_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result),
                    }
                )

            response = await self._call_llm(
                model=agent.model,
                messages=llm_messages,
                tools=tool_schemas,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens,
            )
            choice = response.choices[0]
            assistant_message = choice.message
            tokens_used += response.usage.total_tokens if response.usage else 0

        latency_ms = (time.perf_counter() - start) * 1000

        result_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=assistant_message.content or "",
            tool_calls=(
                [tc.model_dump() for tc in assistant_message.tool_calls]
                if assistant_message.tool_calls
                else None
            ),
            metadata={"tokens_used": tokens_used, "latency_ms": latency_ms},
        )

        logger.info(
            "agent_executed",
            agent_id=str(agent.id),
            conversation_id=str(conversation.id),
            tokens=tokens_used,
            latency_ms=round(latency_ms, 2),
            tool_calls=tool_calls_made,
        )

        return AgentExecutionResult(
            conversation_id=conversation.id,
            message=result_message,
            tool_calls_made=tool_calls_made,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
        )

    def _build_messages(
        self,
        agent: Agent,
        history: list[Message],
        user_input: str,
    ) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": agent.system_prompt},
        ]
        for msg in history:
            entry: dict[str, Any] = {"role": msg.role.value, "content": msg.content}
            if msg.tool_calls:
                entry["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                entry["tool_call_id"] = msg.tool_call_id
            messages.append(entry)
        messages.append({"role": "user", "content": user_input})
        return messages
