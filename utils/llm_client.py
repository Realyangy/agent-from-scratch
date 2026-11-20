"""模型配置和统一的 LLM API 调用。

call_llm 同时支持 OpenAI 和 AsyncOpenAI 客户端：
同步客户端直接返回响应；异步客户端返回协程，需要在调用处 await。
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI


# 读取仓库根目录的 .env
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MODEL_NAMES = ("Qwen3.5-27b-AWQ-4bit", "DeepSeekV4.1-Flash")


@dataclass(frozen=True)
class ModelConfig:
    name: str       # 项目内部使用的模型名称
    model: str      # API 服务器实际识别的模型 ID
    base_url: str
    api_key: str


def get_model_config(model_name: str | None = None) -> ModelConfig:
    """根据模型名称读取配置，并检查必填参数。"""
    name = (model_name or os.getenv("AGENT_MODEL_NAME") or MODEL_NAMES[0]).strip()

    if name == MODEL_NAMES[0]:
        config = ModelConfig(
            name=name,
            model=os.getenv("VLLM_MODEL", "").strip(),
            base_url=os.getenv("VLLM_BASE_URL", "").strip(),
            api_key=os.getenv("VLLM_API_KEY", "EMPTY").strip(),
        )
    elif name == MODEL_NAMES[1]:
        config = ModelConfig(
            name=name,
            model=os.getenv("DEEPSEEK_MODEL", "").strip(),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "").strip(),
            api_key=(
                os.getenv("DEEPSEEK_API_KEY")
                or os.getenv("LYY_DEEPSEEK_API_KEY")
                or ""
            ).strip(),
        )
    else:
        raise ValueError(f"Unknown model: {name}. Choose from {MODEL_NAMES}.")

    if not config.model:
        raise ValueError(f"{name} is missing a model ID.")
    if not config.base_url:
        raise ValueError(f"{name} is missing a base_url.")
    if not config.api_key:
        raise ValueError(f"{name} is missing an API key.")
    return config


def _client_options(config: ModelConfig) -> dict[str, Any]:
    """同步和异步客户端共用的连接参数。"""
    return {
        "api_key": config.api_key,
        "base_url": config.base_url,
        "timeout": float(os.getenv("AGENT_API_TIMEOUT", "100")),
        "max_retries": int(os.getenv("AGENT_API_MAX_RETRIES", "2")),
    }


def get_client(model_name: str | None = None) -> OpenAI:
    """创建同步客户端。"""
    return OpenAI(**_client_options(get_model_config(model_name)))


def get_async_client(model_name: str | None = None) -> AsyncOpenAI:
    """创建异步客户端。"""
    return AsyncOpenAI(**_client_options(get_model_config(model_name)))


def print_token_usage(usage: object | None) -> None:
    """打印 API 返回的 Token 使用量。"""
    if usage is None:
        print("No token usage info received.")
        return

    print(
        f"Input: {getattr(usage, 'prompt_tokens', '?')}\n"
        f"Output: {getattr(usage, 'completion_tokens', '?')}\n"
        f"Total: {getattr(usage, 'total_tokens', '?')}"
    )


def call_llm(
    client: OpenAI | AsyncOpenAI,
    config: ModelConfig,
    messages: list[dict[str, Any]],
    max_tokens: int | None = None,
    enable_thinking: bool = False,
    **kwargs: Any,
) -> Any:
    """统一调用 Chat Completions，处理模型专属的思考参数。

    - 同步客户端：response = call_llm(...)
    - 异步客户端：response = await call_llm(...)
    - max_tokens=None：不强加统一输出上限，由服务端决定默认值。
    - 其他请求参数（tools、stream、temperature 等）通过 kwargs 透传。
    """
    if max_tokens is not None:
        if max_tokens < 1:
            raise ValueError("max_tokens must be greater than 0.")
        kwargs["max_tokens"] = max_tokens

    # 合并调用方自定义的 extra_body，不覆盖其它专属参数。
    extra_body = dict(kwargs.pop("extra_body", None) or {})

    if config.name == MODEL_NAMES[0]:
        template_kwargs = dict(extra_body.get("chat_template_kwargs") or {})
        template_kwargs["enable_thinking"] = enable_thinking
        extra_body["chat_template_kwargs"] = template_kwargs
    elif config.name == MODEL_NAMES[1]:
        thinking_kwargs = dict(extra_body.get("thinking") or {})
        thinking_kwargs["type"] = "enabled" if enable_thinking else "disabled"
        extra_body["thinking"] = thinking_kwargs
    else:
        raise ValueError(f"Unsupported model for thinking mode: {config.name}")

    kwargs["extra_body"] = extra_body
    return client.chat.completions.create(
        model=config.model,
        messages=messages,
        **kwargs,
    )
