# 05 代码说明与运行

运行前，请确保项目根目录的 `.env` 配置了本地 vLLM 或 DeepSeek API。

```bash
python courses/05_simple-agent/main.py
python courses/05_simple-agent/main.py --model DeepSeekV4.1-Flash
python courses/05_simple-agent/main.py --enable-thinking
```

主要代码：`TOOLS` 描述模型可以调用的函数；`get_current_time()` 是真正运行的 Python 函数；`run_tool_loop()` 完成模型请求、工具执行、Observation 回传和继续生成。

默认 `--max-steps 5`，防止模型无限循环。可以用 `--prompt` 更换问题。

**兼容性**：模型服务必须支持 Chat Completions Tool Calling；模型端须能处理 `tool_calls` 及 `tool` 角色消息。