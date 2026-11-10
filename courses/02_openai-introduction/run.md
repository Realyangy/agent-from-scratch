# 02 OpenAI API

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

### 5. Streaming
增量消息可能没有文本，因此需要处理空字段。

### 6. Token Usage
使用 print_token_usage(response.usage) 打印输入、输出、总 Token 数；如果服务没返回则给出提示。

## 运行
~~~bash
python courses/02_openai-intro/openai_intro.py
python courses/02_openai-intro/openai_intro.py --model DeepSeekV4.1-Flash
~~~
