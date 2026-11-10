# 02 OpenAI API

## 学习目标
掌握 API 调用、消息角色、多轮对话、Temperature、Streaming、Token 统计以及模型比较。本项目使用 OpenAI 兼容接口，但不要求使用 OpenAI 官方模型。

## API 请求与响应
一次请求至少包括模型 ID 和 messages。模型通常回复 choices[0].message.content，某些服务同时返回 usage；不同供应商并不保证所有请求参数完全兼容。

## Message Roles（消息角色）
- system：长期适用于当前请求的任务规则与角色要求。
- user：本轮问题或输入数据。
- assistant：模型生成的回答，可在后续请求中加入历史。
- tool：工具执行结果，在第 07 节使用。

## Stateless（无状态）
服务一般不会自动帮每次独立请求保留历史。要实现多轮对话，应在 messages 中保存以前的用户消息、模型回答，再附加新的提问。历史越长，Token 消耗与上下文压力通常越大。

## Temperature（温度）
温度控制输出分布的随机性：低温通常较稳定，高温通常增加多样性，但不会保证更正确。不同服务可能对温度范围或推理模型参数有特殊要求。

## Streaming
默认调用返回完整回复。打开 stream=True 后客户端可以增量获取 delta.content，改善交互的首字延迟；它并不保证降低生成完整回答所需的总时间。

## Token Usage 与输出预算
prompt_tokens 为输入使用量，completion_tokens 为输出使用量，total_tokens 通常为两者之和。max_tokens 限制生成预算，不是模型上下文窗口长度。API 可能按 Token 收费，本地模型则消耗计算资源。usage 可能为空，尤其在某些流式响应中。
