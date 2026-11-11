# 03 并发处理与性能优化

## 学习目标
区分串行、并发、并行与 GPU Batch，理解异步请求为什么有助于 Agent 系统执行独立任务。

## 串行与并发
~~~text
串行：Task A 完成 → Task B 开始
并发：Task A ─────→ 完成
      Task B ───→ 完成
~~~
并发意味着多个任务在时间上重叠，不意味着 GPU 必定同时并行运行两个模型前向传播。

## 原版：多 Context Sequence
原项目的 node-llama-cpp 使用同一个模型的两个独立 Sequence，然后利用 Promise.all 发起两项任务。不同 Session 的上下文彼此隔离。

## Python：asyncio + AsyncOpenAI
新版由异步 HTTP 客户端调用独立的模型服务，用 asyncio.gather 汇总两个独立任务的返回值。两条请求分别建立 messages，不共享对话历史。

## 客户端并发和服务端连续批处理
- **客户端**：决定同时发出多少 HTTP 请求。
- **vLLM 服务端**：决定请求如何入队、调度和执行 GPU 推理，内部可使用 Continuous Batching。

asyncio.gather 不等于设置 vLLM 的 batch_size，也不会保证同时并行计算。

## 性能指标
- Latency：单次调用延迟。
- Throughput：每秒完成的请求数或生成 Token 数。
- Makespan：一组任务全部完成的总耗时。
- TTFT：获得首个输出片段的时间。

并发可能提高吞吐量、缩短总耗时，但服务拥塞时也可能降低性能，不能仅凭一个案例下结论。

## Agent 场景
适用于并行文档检索、多个独立 LLM 子任务、多用户会话和批量评测。后一个任务依赖前一个结果时，不能盲目并发。

## 实践建议
真实服务需要限制并发度、处理超时和 429 限流、加入重试与日志。可使用 asyncio.Semaphore 控制同一时刻请求数。
