# 02 API 基础示例｜CODE

对应当前课程的 `openai_intro.py`。原项目的 `openai-intro.js` 已从本仓库删除，历史版本仍可通过 Git 查看；下面介绍 Python 实现。

## 初始化
公共工具 get_model_config() 返回模型参数，get_client() 创建同步 OpenAI SDK 客户端。所有服务使用兼容的 Chat Completions 接口。

## 七个示例
### 1. Basic Completion
发送单条 user 消息，读取第一个 choice 的 message.content。

### 2. System Prompt
加入 system 消息，让模型成为 Python 编程导师；user 消息询问 async/await。

### 3. Temperature
对相同咖啡店广告请求分别使用 0.2 和 0.8，观察采样变化。需要注意高温未必更好。

### 4. Multi-turn Conversation
先问 Python generator，然后将 assistant 的回答追加到 messages，再提出追问。
~~~python
messages.append({"role": "assistant", "content": answer})
messages.append({"role": "user", "content": "Show a simple example."})
~~~

### 5. Streaming
~~~python
stream = client.chat.completions.create(
    model=config.model, messages=messages,
    stream=True, max_tokens=150,
)
for chunk in stream:
    if chunk.choices:
        print(chunk.choices[0].delta.content or "", end="", flush=True)
~~~
增量消息可能没有文本，因此需要处理空字段。

### 6. Token Usage
使用 print_token_usage(response.usage) 打印输入、输出、总 Token 数；如果服务没返回则给出提示。

### 7. Model Comparison
原 JS 比较 GPT-4o 与 GPT-3.5。Python 版本比较 Qwen 与 DeepSeek，但只在显式传入 --compare-model 时进行，避免不必要的外部 API 调用。

## 运行
~~~bash
python courses/02_openai-intro/openai_intro.py
python courses/02_openai-intro/openai_intro.py --model DeepSeekV4.1-Flash
python courses/02_openai-intro/openai_intro.py --model Qwen3.5-27b-AWQ-4bit --compare-model DeepSeekV4.1-Flash
~~~

## 与原版的差异
原版使用 OpenAI 官方 API；现统一封装模型后端并将 API Key 存入环境变量。错误会正常抛出，后续第 11 节学习重试与恢复。

## 练习
观察多轮历史对 Token 用量的影响，比较 Streaming 与非 Streaming 的返回结构。
