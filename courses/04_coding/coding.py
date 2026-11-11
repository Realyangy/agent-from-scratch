"""课程 04：流式输出与最大生成 Token 数量限制。"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.llm_client import MODEL_NAMES, get_client, get_model_config


def main() -> None:
    parser = argparse.ArgumentParser(description="06 - 流式输出")
    parser.add_argument("--model", choices=MODEL_NAMES, default=None)
    parser.add_argument(
        "--prompt", default="What is hoisting in JavaScript? Explain with examples."
    )
    parser.add_argument("--max-tokens", type=int, default=1000)
    args = parser.parse_args()
    if args.max_tokens < 1:
        parser.error("--max-tokens 必须大于 0")

    config = get_model_config(args.model)
    print(f"模型：{config.name}；max_tokens={args.max_tokens}")
    print("Streaming:\n", end="", flush=True)
    chunks = []
    with get_client(config.name) as client:
        stream = client.chat.completions.create(
            model=config.model,
            messages=[{"role": "user", "content": args.prompt}],
            max_tokens=args.max_tokens,
            stream=True,
        )
        for event in stream:
            if not event.choices:
                continue
            text = event.choices[0].delta.content or ""
            print(text, end="", flush=True)
            chunks.append(text)
    print("\n\nFinal answer:\n" + "".join(chunks))


if __name__ == "__main__":
    main()
