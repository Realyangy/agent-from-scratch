"""Agent 项目的统一 LLM 接口：Qwen（vLLM）与 DeepSeek（API）。

通过 OpenAI 兼容 Chat Completions 接口调用服务。课程中不加载模型，
也不需要在 Agent 环境中安装 vLLM；真实 API Key 从环境变量读取。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MODEL_NAMES = ("Qwen3.5-27b-AWQ-4bit", "DeepSeekV4.1-Flash")


@dataclass(frozen=True)
class ModelConfig:
    """name 是自定义别名，model 是推理服务接收的真实模型 ID。"""

    name: str
    model: str
    base_url: str
    api_key: str


def get_model_config(model_name: str | None = None) -> ModelConfig:
    """读取模型配置。默认选择 Qwen；不在源码中存放真实密钥。"""
    name = model_name or os.getenv("AGENT_MODEL_NAME", MODEL_NAMES[0])

    if name == "Qwen3.5-27b-AWQ-4bit":
        config = ModelConfig(
            name=name,
            model=os.getenv("AGENT_VLLM_MODEL", "").strip(),
            base_url=os.getenv("AGENT_VLLM_BASE_URL", "http://127.0.0.1:8001/v1"),
            api_key=os.getenv("AGENT_VLLM_API_KEY", "EMPTY"),
        )
    elif name == "DeepSeekV4.1-Flash":
        config = ModelConfig(
            name=name,
            model=os.getenv("AGENT_DEEPSEEK_MODEL", "deepseek-flash"),
            base_url=os.getenv("AGENT_DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            api_key=os.getenv("LYY_DEEPSEEK_API_KEY", "").strip(),
        )
    else:
        raise ValueError(f"未知模型：{name}；可选：{', '.join(MODEL_NAMES)}")

    if not config.model:
        raise ValueError(
            f"{name} 缺少模型 ID；请填写 .env 的 AGENT_VLLM_MODEL，"
            "它必须与 vLLM /v1/models 返回的 id 一致。"
        )
    if not config.base_url:
        raise ValueError(f"{name} 缺少 base_url。")
    if not config.api_key:
        raise ValueError(f"{name} 没有 API Key；请设置 LYY_DEEPSEEK_API_KEY。")
    return config


def _options(config: ModelConfig) -> dict:
    return {
        "api_key": config.api_key,
        "base_url": config.base_url,
        "timeout": float(os.getenv("AGENT_API_TIMEOUT", "120")),
        "max_retries": int(os.getenv("AGENT_API_MAX_RETRIES", "2")),
    }


def get_client(model_name: str | None = None) -> OpenAI:
    """同步调用客户端。"""
    return OpenAI(**_options(get_model_config(model_name)))


def get_async_client(model_name: str | None = None) -> AsyncOpenAI:
    """异步调用客户端，适合并发和多工具场景。"""
    return AsyncOpenAI(**_options(get_model_config(model_name)))


def print_token_usage(usage: object | None) -> None:
    """兼容部分服务不返回 usage 的情况。"""
    if usage is None:
        print("Token usage: 当前服务未返回统计信息")
        return
    print(
        f"Prompt: {getattr(usage, 'prompt_tokens', '?')}, "
        f"Completion: {getattr(usage, 'completion_tokens', '?')}, "
        f"Total: {getattr(usage, 'total_tokens', '?')}"
    )
