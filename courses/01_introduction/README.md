# 01 基础 LLM 交互

## 学习目标
理解 LLM 的输入、推理服务、上下文窗口、逐 Token 生成与输出。本 Python 版使用独立 vLLM 服务或者 DeepSeek API，不在 Agent 环境加载模型。

## 什么是本地 LLM？
Local LLM 指模型运行在自有机器上。其优势是可控制部署、避免按次向外部模型服务付费，并能自行管理数据；代价是需要计算资源。使用 vLLM 时，Python 客户端和模型服务可位于不同进程或机器，仍通过 HTTP 通信。

## 核心组件
1. **Model**：权重和架构。由 vLLM 或第三方服务加载。
2. **Tokenizer**：将输入编码成 Token。Token 既不等于字符，也不固定等于英文单词。
3. **Context Window**：一次请求能容纳的输入、历史与生成预算，受模型和部署配置限制。
4. **Chat Template**：将 system、user、assistant 等角色格式化为模型可处理的输入。
5. **Sampling**：根据生成概率选择下一 Token，可调整温度与输出上限。

## 推理流程
~~~text
Python messages
    ↓ HTTP 请求（OpenAI 兼容格式）
vLLM / DeepSeek API
    ↓ 模板、Tokenization、推理
Chat Completion 返回内容
    ↓
response.choices[0].message.content
~~~

模型通常逐 Token 生成回答。一次 Chat Completion 本身不自动保存跨调用历史；多轮会话需要应用管理并重新提供历史消息。

## 资源管理
模型由推理服务负责管理，Python 的 with 语句用于关闭 HTTP 客户端，不会卸载 vLLM 模型。

## 为什么与 Agent 有关？
LLM 是 Agent 决策的一部分，但只问一次模型还不是完整 Agent。后续课程会引入 Tool Calling、Memory、ReAct 及任务规划。
