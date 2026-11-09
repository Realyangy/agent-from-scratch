"""课程 02：API 基础、System Prompt、采样参数、历史、流式和 Token 用量。

默认使用一个已配置模型；只有显式传入 --compare-model 才执行跨模型比较。
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.llm_client import (
    MODEL_NAMES,
    get_client,
    get_model_config,
    print_token_usage,
)


def complete(client, model, messages, **kwargs):
    return client.chat.completions.create(model=model, messages=messages, **kwargs)


def run_examples(model_name: str, compare_model: str | None = None) -> None:
    config = get_model_config(model_name)
    print(f"当前模型: {config.name} ({config.model})\n")

    with get_client(config.name) as client:
        print("=== 1. Basic completion ===")
        response = complete(client, config.model, [
            {"role": "user", "content": "What is an AI agent in one sentence?"}
        ])
        print(response.choices[0].message.content, "\n")

        print("=== 2. System prompt ===")
        response = complete(client, config.model, [
            {"role": "system", "content": "You are a coding tutor. Answer with a short example."},
            {"role": "user", "content": "Explain Python async/await."},
        ])
        print(response.choices[0].message.content, "\n")

        print("=== 3. Temperature ===")
        prompt = [{"role": "user", "content": "Write a one-line tagline for a coffee shop."}]
        for temp in (0.2, 0.8):
            response = complete(client, config.model, prompt, temperature=temp)
            print(f"temperature={temp}:", response.choices[0].message.content)
        print()

        print("=== 4. Multi-turn conversation ===")
        messages = [
            {"role": "system", "content": "You are a helpful Python tutor."},
            {"role": "user", "content": "What is a Python generator?"},
        ]
        first = complete(client, config.model, messages, max_tokens=200)
        answer = first.choices[0].message.content or ""
        print("Question 1:", messages[-1]["content"], "\nAI:", answer)
        messages.append({"role": "assistant", "content": answer})
        messages.append({"role": "user", "content": "Show a simple example."})
        second = complete(client, config.model, messages, max_tokens=300)
        print("Question 2:", messages[-1]["content"])
        print("AI:", second.choices[0].message.content, "\n")

        print("=== 5. Streaming ===")
        stream = complete(
            client, config.model,
            [{"role": "user", "content": "Write a haiku about programming."}],
            stream=True, max_tokens=150,
        )
        print("AI: ", end="", flush=True)
        for chunk in stream:
            if chunk.choices:
                print(chunk.choices[0].delta.content or "", end="", flush=True)
        print("\n")

        print("=== 6. Token usage ===")
        response = complete(
            client, config.model,
            [{"role": "user", "content": "Explain recursion in 3 sentences."}],
            max_tokens=200,
        )
        print(response.choices[0].message.content)
        print_token_usage(response.usage)

    print("\n=== 7. Optional model comparison ===")
    if not compare_model:
        print("未指定 --compare-model，跳过跨模型比较。")
        return
    other = get_model_config(compare_model)
    messages = [{"role": "user", "content": "What's 25 * 47?"}]
    for selected in (config, other):
        with get_client(selected.name) as client:
            response = complete(client, selected.model, messages)
        print(f"{selected.name}: {response.choices[0].message.content}")


def main() -> None:
    parser = argparse.ArgumentParser(description="02 - OpenAI 兼容 API 基础")
    parser.add_argument("--model", choices=MODEL_NAMES, default=None)
    parser.add_argument("--compare-model", choices=MODEL_NAMES, default=None)
    args = parser.parse_args()
    run_examples(get_model_config(args.model).name, args.compare_model)


if __name__ == "__main__":
    main()
