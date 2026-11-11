# 07 ReAct Agent：推理—行动—观察循环

## 学习目标
掌握 Agent 最关键的循环：模型决定下一步工具调用（Action），Python 执行工具并生成 Observation，再让模型判断是否继续或回答。

## 示例
用户提出多步销售计算题；模型使用加法、减法、乘法、除法工具逐步计算。工具结果都是确定性的 Python 运算，不允许模型伪造计算结果。

## 核心机制
- `TOOLS` 里提供 `add`、`subtract`、`multiply`、`divide`。
- `run_tool_loop` 在收到 `tool_calls` 后执行对应 Python 函数，并把结果写入 `messages`。
- 模型根据已返回结果继续决定工具或输出最终回答。
- `max_steps` 提供执行预算，避免无限循环。

此实现通过结构化 Tool Calling 表示 Action/Observation，并不强制模型显式输出完整的 Thought 文本。ReAct 是一种 Agent 策略，不等于必须暴露模型内部推理。