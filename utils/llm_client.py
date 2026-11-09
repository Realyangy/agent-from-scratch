import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass
from openai import OpenAI, AsyncOpenAI

# 加载环境配置
ENVIRONMENT_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENVIRONMENT_PATH)

# 可选模型名称列表
MODEL_NAMES = ("Qwen3.5-27b-AWQ-4bit", "DeepSeekV4.1-Flash")


@dataclass(frozen=True)
class ModelConfig:
    name: str # 模型的自定义名称
    model: str # 模型调用名称，本地模型的路径或者API模型的名称
    base_url: str
    api_key: str


# 读取模型配置
def get_model_config(model_name: str | None = None) -> ModelConfig:
    name = model_name or os.getenv("AGENT_MODEL_NAME", MODEL_NAMES[0])
    if name == "Qwen3.5-27b-AWQ-4bit":
        config = ModelConfig(
            name=name,
            model=os.getenv("VLLM_MODEL").strip(),
            base_url=os.getenv("VLLM_BASE_URL").strip(),
            api_key=os.getenv("VLLM_API_KEY").strip(),
        )
    elif name == "DeepSeekV4.1-Flash":
        config = ModelConfig(
            name=name,
            model=os.getenv("DEEPSEEK_MODEL").strip(),
            base_url=os.getenv("DEEPSEEK_BASE_URL").strip(),
            api_key=os.getenv("DEEPSEEK_API_KEY").strip(),
        )
    else:
        raise ValueError(f"Unknown model: {name}, please select from [{', '.join(MODEL_NAMES)}]")

    if not config.model:
        raise ValueError(f"{name} is missing a model ID.")
    if not config.base_url:
        raise ValueError(f"{name} is missing a base_url.")
    if not config.api_key:
        raise ValueError(f"{name} is missing an API key.")
    return config


# 返回模型客户端配置参数
def _options(config: ModelConfig) -> dict:
    return {
        "api_key": config.api_key,
        "base_url": config.base_url,
        "timeout": float(os.getenv("AGENT_API_TIMEOUT")),
        "max_retries": int(os.getenv("AGENT_API_MAX_RETRIES")),
    }


# 同步调用模型客户端
def get_client(model_name: str | None = None) -> OpenAI:
    return OpenAI(**_options(get_model_config(model_name)))


# 异步调用模型客户端
def get_async_client(model_name: str | None = None) -> AsyncOpenAI:
    return AsyncOpenAI(**_options(get_model_config(model_name)))


# 统计并输出一次LLM调用的Token开销
def print_token_usage(usage: object | None) -> None:
    if usage is None:
        print("No token usage info received.")
        return

    input_tokens = getattr(usage, 'prompt_tokens', '?')
    output_tokens = getattr(usage, 'completion_tokens', '?')
    total_tokens = getattr(usage, 'total_tokens', '?')
    print(f"Input: {input_tokens}\nOutput: {output_tokens}\nTotal: {total_tokens}")
