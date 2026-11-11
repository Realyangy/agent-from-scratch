# 06 Agent with Memory：持久化记忆

## 学习目标
在 Tool Calling 之上增加跨进程持久化的长期记忆，理解会话历史（messages）和长期事实存储（JSON）的区别。

## 工作原理
1. 从磁盘读取 JSON 记忆文件，整理已有 fact 和 preference。
2. 将已有记忆放入当前系统提示词。
3. 模型遇到新事实或修改的偏好时，调用 `saveMemory`。
4. `MemoryManager` 以 type + key 去重；值变化时更新原记忆。
5. 后续轮次重新读取记忆，重新构造 system 消息；即使程序重新启动，JSON 仍会保留。

## 文件
- `main.py`：模型调用、工具定义、多轮演示
- `memory_manager.py`：JSON 读写、迁移、去重与摘要
- `../../utils/tool_loop.py`：统一工具调用循环

## 边界
这不是向量数据库或 RAG，也不代表模型参数真正记住了信息；事实保存在本地 JSON 中。为防止提交个人数据，默认数据文件放在 `output/agent-memory.json`（该目录被 gitignore 忽略）。