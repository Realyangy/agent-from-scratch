# 04 流式输出

对应当前课程的 `coding.py`。原项目的 `coding.js` 已从本仓库删除，历史版本仍可通过 Git 查看；下面介绍 Python 实现。

## 1. 输入
默认保留英文问题：
~~~text
What is hoisting in JavaScript? Explain with examples.
~~~
也可以通过 --prompt 替换为 Python 问题。

## 2. 创建流
~~~python
stream = client.chat.completions.create(
    model=config.model,
    messages=[{"role": "user", "content": args.prompt}],
    max_tokens=args.max_tokens,
    stream=True,
)
~~~
stream=True 返回可以迭代的响应块，不是已经拼好的完整回答。

## 3. 逐块显示
~~~python
chunks = []
for event in stream:
    if not event.choices:
        continue
    text = event.choices[0].delta.content or ""
    print(text, end="", flush=True)
    chunks.append(text)
~~~
对于空文本增量采取兼容处理，flush=True 促使终端即时显示，chunks 则保存所有文本片段。

## 4. 重建最终答案
~~~python
print("\n\nFinal answer:\n" + "".join(chunks))
~~~
这样会显示一次流式过程和一次完整文本，是故意用于教学的重复输出，并非发起两次模型调用。

## 5. 对照 JavaScript
| JS | Python |
| --- | --- |
| onTextChunk | 遍历 stream 的 delta.content |
| process.stdout.write | print(..., end="", flush=True) |
| maxTokens | max_tokens |
| HarmonyChatWrapper | 服务端负责 Chat Template |

## 运行
~~~bash
python courses/04_coding/coding.py
python courses/04_coding/coding.py --model DeepSeekV4.1-Flash --max-tokens 500
~~~

## 练习
分别设置较短和较长输出预算；对比非流式返回对象。若想在 Web 页面实时显示，需要通过 SSE 或 WebSocket 等方式继续转发增量内容。
