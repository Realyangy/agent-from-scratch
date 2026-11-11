# 09 Tool Routing：Embedding 工具检索

## 学习目标
当 Agent 有大量工具时，不要每次都把所有工具的描述发给模型，而是在调用 LLM 前基于语义相关性选出少量工具。

## 工作流程
1. 为 12 个模拟 IT 帮助台工具定义 Schema 和多个短句 Exemplars。
2. 使用 `sentence-transformers` 本地 Embedding 模型预计算 Exemplars 向量。
3. 对用户请求生成向量，计算与所有示例的余弦相似度。
4. 每个工具使用旗下 Exemplars 的最大相似度作为工具评分。
5. 选择 Top-k 工具，并叠加 `always_include` 固定工具。
6. 把筛选出的工具交给 `run_tool_loop`，由 LLM 决定是否调用及填写参数。

## 教学重点
- Embedding 预筛选和 LLM Tool Calling 是两个不同阶段。
- k 太小会造成工具召回不足；可以用 pinned tools 兜底。
- 此实现用 `sentence-transformers/all-MiniLM-L6-v2`，与原教程的 GGUF bge 模型不同，但保留了同样的余弦相似度和最大分聚合策略。
- 工具返回的是模拟数据，不会真正重置用户密码、重启系统服务或操作账户。