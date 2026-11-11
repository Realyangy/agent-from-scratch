# 08 代码说明与运行

单条任务：

```bash
python courses/08_error-handling/main.py
python courses/08_error-handling/main.py --prompt "Fetch user u_123"
```

依次体验正常、Not Found、策略阻断、主备故障、空输入：

```bash
python courses/08_error-handling/main.py --all-demos
```

不需要模型的故障演示：

```bash
python courses/08_error-handling/main.py --prompt "SKIP_LLM_DEGRADED u_777"
```

主要调用链：`run_agent` 做输入校验与错误分类 → 尝试 `run_tool_loop` 调用模拟工具 → 模型出错时 `resolve_without_llm` 触发主服务重试与备用服务兜底 → 返回带 correlation_id 的结构化结果。

**限制**：为简化教学，这里使用同步 SDK、`timeout=15` 和同步退避；演示数据是假的。真正的工具异常从模型循环到故障策略的传播可根据生产场景进一步细化。