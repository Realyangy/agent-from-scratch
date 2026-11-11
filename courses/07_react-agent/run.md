# 07 代码说明与运行

```bash
python courses/07_react-agent/main.py
python courses/07_react-agent/main.py --model DeepSeekV4.1-Flash
python courses/07_react-agent/main.py --prompt "Calculate (15 + 7) * 3 - 10"
python courses/07_react-agent/main.py --max-steps 15
```

本节的 `main.py` 先声明四个计算工具；`log_action()` 显示每一次 Action 及对应 Observation；`run_tool_loop()` 负责继续把 Observation 发送给模型。

除零错误会作为工具错误信息返回模型，由模型决定如何处理。默认最大 12 轮。输出最终答案前应检查实际的工具调用日志，不能只看模型给出的数字。

注意模型服务需支持 OpenAI 兼容工具调用。