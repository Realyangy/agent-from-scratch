"""
使用asyncio和AsyncOpenAI并发执行两个独立请求
"""

import sys
import argparse
import asyncio
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.llm_client import MODEL_NAMES, get_async_client, get_model_config


QUESTIONS = ["Hi there, how are you?", "How much is 6+6?"]

async def main_async(model_name: str | None) -> None:
    config = get_model_config(model_name)
    async with get_async_client(config.name) as client:
        async def ask(question: str) -> str:
            response = await client.chat.completions.create(
                model=config.model,
                messages=[{"role": "user", "content": question}],
                max_tokens=150,
            )
            return response.choices[0].message.content or ""

        started = perf_counter()
        answers = await asyncio.gather(*(ask(q) for q in QUESTIONS))
        print(f"并发执行耗时：{perf_counter() - started:.2f}s")

    for question, answer in zip(QUESTIONS, answers):
        print(f"User: {question}\nAI: {answer}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="05 - 异步并发 API 请求")
    parser.add_argument("--model", choices=MODEL_NAMES, default=None)
    args = parser.parse_args()
    asyncio.run(main_async(args.model))


if __name__ == "__main__":
    main()
