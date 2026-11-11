# 06 代码说明与运行

```bash
python courses/06_simple-agent-with-memory/main.py
python courses/06_simple-agent-with-memory/main.py --model DeepSeekV4.1-Flash
python courses/06_simple-agent-with-memory/main.py --prompt "My name is Alex." --prompt "What is my name?"
python courses/06_simple-agent-with-memory/main.py --memory-file output/test-memory.json
```

`memory_manager.py` 的 `add_memory(type, key, value)` 执行类型验证、同键去重、更新和持久化。每轮先重建 system prompt，再利用 `run_tool_loop` 处理模型可能发出的 `saveMemory` 请求。

默认演示两轮：介绍个人信息，再追问偏好。连续运行会复用同一 JSON 文件。也支持通过 `--memory-file` 设置不同存储路径，以便测试。

删除记忆请自行检查后删除该 JSON 文件；此教学示例没有隐私治理或多用户权限系统。