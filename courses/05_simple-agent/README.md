# 05 Simple Agent：Tool Calling

## 学习目标
理解 Agent 如何通过 OpenAI 兼容 API 调用真实 Python 函数，区分“模型提出工具调用请求”和“Python 实际执行工具”。

## 示例
用户问当前时间。模型调用 `getCurrentTime`，Python 使用 `datetime.now()` 获取当前本机时间，工具结果作为 `tool` 消息返回模型，最终回答为 24 小时制 HH:MM。

## 核心机制
- 使用 `tools` 提供函数定义及 JSON Schema。
- 模型可能返回 `message.tool_calls`，程序根据名称分发到 Python 函数。
- 把工具结果通过 `tool_call_id` 关联回对话，再请求模型给出最终回答。
- `utils/tool_loop.py` 实现共用的 Tool Calling Loop；它不是第三方 Agent 框架。

## 文件
- `main.py`：本节运行入口
- `../../utils/tool_loop.py`：公共工具定义与循环

注意：工具使用的时间是 **运行 Python 程序所在机器的本地时间**，模型不能自行保证时间正确。