"""
使用asyncio和AsyncOpenAI并发执行两个独立请求
相关异步操作：
    async def：定义异步函数
    await：定义异步操作，表示在执行这行代码时可能需要等待，在等待时可以挂起该任务，去执行其他的任务
    asyncio.gather()：并发执行多个异步任务，多个协程对象作为参数传入
    async with：管理需要异步初始化，结束时会自动调用资源的清理方法
    asyncio.run()：启动异步执行环境（事件循环），是异步程序的启动入口。参与事件循环的都是不同事件，事件A先开始，等待时开始执行事件B，B等待时继续执行事件A。
"""

import sys
import asyncio
import argparse
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.llm_client import MODEL_NAMES, get_client, get_async_client, get_model_config

QUESTIONS = ["How are you?", "How much is 6+6?"]

# 用async将函数定义成"协程函数"，调用时，不会立刻执行函数体，而是返回一个协程对象
async def main_async(model_name: str | None) -> None:
    config = get_model_config(model_name)
    async with get_async_client(config.name) as client:

        async def ask(question: str) -> str:
            messages = [{"role": "user", "content": question}]
            response = await client.chat.completions.create(model=config.model, messages=messages, max_tokens=200)
            return response.choices[0].message.content or ""

        started = perf_counter()
        # 把每个问题的ask作为一个协程任务
        tasks = [ask(q) for q in QUESTIONS]
        # asyncio.gather并发处理多个协程任务，用*给tasks解包，将其中每个元素作为一个参数传递给asyncio.gather
        answers = await asyncio.gather(*tasks)
        for question, answer in zip(QUESTIONS, answers):
            print(f"User: {question}\nAI: {answer}")
        print(f"Concurrent execution time: {perf_counter() - started:.2f}s")


# 同步调用，作为对比
def main_synch(model_name: str | None) -> None:
    config = get_model_config(model_name)
    with get_client(config.name) as client:

        def ask(question: str) -> str:
            messages = [{"role": "user", "content": question}]
            response = client.chat.completions.create(model=config.model, messages=messages, max_tokens=200)
            return response.choices[0].message.content or ""

        started = perf_counter()
        for question in QUESTIONS:
            answer = ask(question)
            print(f"User: {question}\nAI: {answer}")
        print(f"Concurrent execution time: {perf_counter() - started:.2f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Asynchronous concurrent API requests")
    parser.add_argument("--model", choices=MODEL_NAMES, default=None)
    args = parser.parse_args()

    print("===== Asynchronous execution =====")
    asyncio.run(main_async(args.model))

    print("===== Synchronous execution =====")
    main_synch(args.model)


if __name__ == "__main__":
    main()