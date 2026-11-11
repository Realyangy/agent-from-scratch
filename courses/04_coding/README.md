# 04 Streaming 与响应控制

## 目标
理解流式输出（Streaming）、输出 Token 限制以及它们在交互式 Agent 中的价值。虽然课程目录叫 coding，重点并不是自动写代码。

## 非流式与流式
非流式一次返回完整文本；流式服务会逐步返回增量内容：
~~~text
请求 → 首个 chunk → 后续 chunk → 结束
~~~
这能改善用户感知的响应速度，但不一定降低完整生成的耗时。

## Chunk 与 Token 的区别
API chunk 是传输增量，不必恰好包含一个 Token，有时只携带结束信号或元数据。读取 delta.content 时要考虑字段为空的情况。

## max_tokens
控制生成输出预算；不等于 Context Window 大小。预算过小可能截断答案，预算较大可能提高生成时长和费用。不同模型和服务对参数支持存在差异。

## TTFT 与 Throughput
TTFT 是首个输出到达所需时间；Throughput 衡量单位时间完成多少输出。它们和用户体验、系统容量有关，但不能互相替代。

## Harmony Chat Wrapper
原版为了某个 GGUF 模型使用 HarmonyChatWrapper。Python 版将聊天消息发送到 vLLM 或外部 API，聊天模板在服务端处理，不必在客户端直接模拟包装器。

## Streaming 在 Agent 中的价值
Agent 系统除了文本还会产生工具调用、状态和错误事件。这些内容需要分开处理：用户可见回答可以流式显示，工具执行仍必须等待结构化的调用数据。

## 进阶话题
- 缓冲与批量刷新；
- 用户取消时关闭流；
- 多个消费者分发；
- 输出日志和进度；
- 工具调用的增量参数组装。

## 自查
为什么 stream=True 不意味着生成速度翻倍？何时应该关闭流而不是继续浪费 Token？
