"""第 05～09 节通用的同步 Tool Calling 循环。

职责分工：
- llm_client.call_llm：模型 API 请求、模型专属参数
- tool_loop.run_tool_loop：读取 tool_calls、执行 Python 工具、回传结果
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
    """生成 OpenAI Chat Completions 所需的函数工具定义。"""
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
    max_tokens: int | None = None,
    on_tool: Callable[[str, dict[str, Any], str], None] | None = None,
    propagate_tool_errors: bool = False,
    **request_kwargs: Any,
) -> str:
    """调用 LLM，执行工具，并将 Observation 发送回模型，直至得到最终回答。

    messages 会被原地更新；max_steps 限制 LLM 请求轮数，而非工具总次数。
    max_tokens=None 表示不人为限制每轮输出长度。
    工具调用出错时，默认把错误作为 Observation 返回给模型；
    propagate_tool_errors=True 则将异常直接抛给调用方。
    """
    if max_steps < 1:
        raise ValueError("max_steps must be at least 1.")
    if not tools:
        raise ValueError("At least one tool is required.")

    for _ in range(max_steps):
        # 只通过统一的 call_llm 请求模型，不在这里重新处理 Thinking Mode。
        response = call_llm(
            client,
            config,
            messages,
            max_tokens=max_tokens,
            enable_thinking=enable_thinking,
            tools=tools,
            tool_choice="auto",
            **request_kwargs,
        )
        if not response.choices:
            raise RuntimeError("LLM returned no choices.")

        message = response.choices[0].message
        tool_calls = message.tool_calls or []

        # 保留工具调用记录，下轮必须让模型知道自己调用过哪些工具。
        assistant: dict[str, Any] = {
            "role": "assistant",
            "content": message.content or "",
        }
        if tool_calls:
            assistant["tool_calls"] = [
                call.model_dump(exclude_none=True) for call in tool_calls
            ]
        messages.append(assistant)

        if not tool_calls:
            answer = message.content or ""
            if not answer.strip():
                raise RuntimeError("LLM returned an empty final answer.")
            return answer

        for tool_call in tool_calls:
            name = tool_call.function.name
            raw_args = tool_call.function.arguments or "{}"
            args: dict[str, Any] = {}
            parsed_ok = False

            try:
                parsed = json.loads(raw_args)
                if not isinstance(parsed, dict):
                    raise ValueError("Tool arguments must be a JSON object.")
                args = parsed
                parsed_ok = True

                if name not in handlers:
                    raise ValueError(f"Unknown tool: {name}")
                result = handlers[name](**args)
                content = (
                    result if isinstance(result, str)
                    else json.dumps(result, ensure_ascii=False)
                )
            except Exception as exc:
                if propagate_tool_errors:
                    raise
                content = json.dumps(
                    {"error": f"{type(exc).__name__}: {exc}"},
                    ensure_ascii=False,
                )

            if on_tool is not None:
                # 解析失败时记录原始参数，工具执行失败时仍保留正确的解析参数。
                log_args = args if parsed_ok else {"raw": raw_args}
                on_tool(name, log_args, content)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": content,
            })

    raise RuntimeError(f"Agent exceeded max_steps={max_steps} without a final answer.")
