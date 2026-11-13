"""
LLM的流式输出，也就是逐个token的输出
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.llm_client import MODEL_NAMES, get_client, get_model_config, call_llm


def main() -> None:
    parser = argparse.ArgumentParser(description="Streaming Output")
    parser.add_argument("--model", choices=MODEL_NAMES, default=None)
    parser.add_argument("--max-tokens", type=int, default=1000)
    args = parser.parse_args()
    if args.max_tokens < 1:
        parser.error("--max-tokens must > 0")

    config = get_model_config(args.model)
    print(f"Current model：{config.name}；max_tokens={args.max_tokens}")
    print("Streaming:\n", end="", flush=True)

    prompt = "How are you?"
    messages=[{"role": "user", "content": prompt}]

    with get_client(config.name) as client:
        stream = call_llm(client, config, messages, args.max_tokens, stream=True)
        for event in stream:
            if not event.choices:
                continue
            
            # 读取LLM流式输出的增量内容
            text = event.choices[0].delta.content or ""
            # 不自动换行，且立刻刷新输出输出缓冲区
            print(text, end="", flush=True)


if __name__ == "__main__":
    main()
