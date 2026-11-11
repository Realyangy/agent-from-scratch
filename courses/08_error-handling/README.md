# 08 Error Handling：Agent 的错误处理与降级

## 学习目标
区分用户输入错误、模型调用错误、工具执行错误和 Agent 工作流失败，并学习 Retry、Backoff、Fallback 与 Correlation ID。

## 核心内容
- `ValidationError`：用户输入为空或不符合要求；通常不重试。
- `LLMCallError`：模型请求失败；可以进行受限重试。
- `ToolExecutionError`：工具获取数据失败；按错误是否可重试处理。
- `AgentWorkflowError`：执行计划无法继续，如主服务和备用服务都失败。
- `with_retries`：有限次数的指数退避加随机抖动。
- `resolve_without_llm`：当 LLM 不可用时，通过确定性 Python 工作流兜底。

## 演示性质
这里的用户资料接口 **全部是模拟工具**，没有连接真实的用户服务。用户 `u_999` 用于模拟不存在；`u_777` 用于模拟主、备服务故障；`u_demo_workflow` 用于触发策略阻断。

实际工程还需要日志脱敏、监控、请求取消、权限和外部服务故障分类。