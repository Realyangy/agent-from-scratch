"""Shared Chat Completions tool-calling loop used by lessons 05–09.

This deliberately exposes the steps: send tool schemas -> inspect tool_calls ->
execute Python functions -> send tool results -> request the final answer.
"""
from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from .llm_client import ModelConfig, call_llm


def function_tool(
    name: str,
    description: str,
    properties: dict[str, Any] | None = None,
    required: list[str] | None = None,
) -> dict[str, Any]:
    """Create an OpenAI-compatible function tool schema."""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties or {},
                "required": required or [],
                "additionalProperties": False,
            },
        },
    }


def run_tool_loop(
    client: Any,
    config: ModelConfig,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    handlers: dict[str, Callable[..., Any]],
    *,
    enable_thinking: bool = False,
    max_steps: int = 8,
    on_tool: Callable[[str, dict[str, Any], str], None] | None = None,
    propagate_tool_errors: bool = False,
    **request_kwargs: Any,
) -> str:
    """Run an agent until it responds without tool calls, or its budget is exhausted.

    messages is updated in place so the caller can retain conversation history.
    A tool error is sent back as an observation unless propagate_tool_errors=True.
    """
    if max_steps < 1:
        raise ValueError("max_steps must be at least 1")
    if not tools:
        raise ValueError("At least one tool must be provided")

    for _ in range(max_steps):
        response = call_llm(
            client,
            config,
            messages,
            enable_thinking=enable_thinking,
            tools=tools,
            tool_choice="auto",
            **request_kwargs,
        )
        if not response.choices:
            raise RuntimeError("LLM returned no choices")

        message = response.choices[0].message
        tool_calls = message.tool_calls or []
        assistant = {"role": "assistant", "content": message.content or ""}
        if tool_calls:
            assistant["tool_calls"] = [call.model_dump(exclude_none=True) for call in tool_calls]
        messages.append(assistant)

        if not tool_calls:
            answer = message.content or ""
            if not answer.strip():
                raise RuntimeError("LLM returned an empty final answer")
            return answer

        for tool_call in tool_calls:
            name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments or "{}")
                if not isinstance(args, dict):
                    raise ValueError("Function arguments must be a JSON object")
                if name not in handlers:
                    raise ValueError(f"Unknown tool: {name}")
                result = handlers[name](**args)
                content = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
            except (Exception) as exc:
                if propagate_tool_errors:
                    raise
                args = {"raw": tool_call.function.arguments}
                content = json.dumps({"error": str(exc)}, ensure_ascii=False)

            if on_tool is not None:
                on_tool(name, args, content)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": content,
            })

    raise RuntimeError(f"Agent exceeded max_steps={max_steps} without a final answer")
