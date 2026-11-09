"""课程 01：最基本的 LLM 请求。运行：python courses/01_intro/intro.py"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.llm_client import MODEL_NAMES, get_client, get_model_config


def main() -> None:
    parser = argparse.ArgumentParser(description="01 - 基础 Chat Completion")
    parser.add_argument("--model", choices=MODEL_NAMES, default=None)
    parser.add_argument("--prompt", default="What is an AI agent? Explain briefly.")
    args = parser.parse_args()

    config = get_model_config(args.model)
    with get_client(config.name) as client:
        response = client.chat.completions.create(
            model=config.model,
            messages=[{"role": "user", "content": args.prompt}],
        )
    print("AI:", response.choices[0].message.content)


if __name__ == "__main__":
    main()
