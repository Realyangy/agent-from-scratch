# 05 并发调用｜CODE

对应 batch.py；原始 batch.js。

## 1. 异步函数
~~~python
async def ask(question: str) -> str:
    response = await client.chat.completions.create(
        model=config.model,
        messages=[{"role": "user", "content": question}],
        max_tokens=150,
    )
    return response.choices[0].message.content or ""
~~~
async/await 使程序在网络等待时能继续调度其他协程。

## 2. AsyncOpenAI 客户端
~~~python
async with get_async_client(config.name) as client:
    ...
~~~
异步客户端由 utils/llm_client.py 提供，与同步客户端使用同一套模型配置。

## 3. asyncio.gather
~~~python
answers = await asyncio.gather(*(ask(q) for q in QUESTIONS))
~~~
gather 并发执行两个独立请求，并按传入顺序返回结果，即使第二个先完成，结果仍与对应问题配对。

## 4. 启动事件循环
~~~python
asyncio.run(main_async(args.model))
~~~
适用于直接从终端运行的 Python 脚本；在已经运行事件循环的 Notebook 中调用方式有所不同。

## 5. 与 JavaScript 的对照
| JS | Python |
| --- | --- |
| Promise.all | asyncio.gather |
| session.prompt | await client.chat.completions.create |
| 独立 Sequence | 独立请求 messages |
| context.batchSize | 服务端独立管理模型调度 |

## 运行
~~~bash
python courses/05_batch/batch.py
python courses/05_batch/batch.py --model DeepSeekV4.1-Flash
~~~

## 练习
把 gather 临时换成 for 循环中的顺序 await，比对总耗时；重复测试多次并考虑模型负载与长度影响。若未来扩展大量请求，请引入并发上限与错误处理。
