# 09 代码说明与运行

本节额外需要 Embedding 库：

```bash
python -m pip install sentence-transformers
```

默认运行六个工具路由案例：

```bash
python courses/09_tool-routing-embeddings/main.py
```

自定义一个任务：

```bash
python courses/09_tool-routing-embeddings/main.py --prompt "My account is locked" --k 2
python courses/09_tool-routing-embeddings/main.py --prompt "VPN is down and my account is locked" --k 1 --always-include getUserAccount
```

可用 `--model` 指定对话 LLM；`--embedding-model` 指定本地路径或 Hugging Face 模型 ID。首次使用 Embedding 模型时通常需要下载权重，离线服务器请提前缓存并指定本地路径。

主要函数：`score_tools`（取每个工具的最高相似度）、`select_tool_keys`（Top-k + pinned）、`run_tool_loop`（实际调用模型和所选工具）。