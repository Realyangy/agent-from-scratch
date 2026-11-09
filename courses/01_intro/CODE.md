# 01 基础调用｜CODE

对应 Python：intro.py；原始参考：intro.js。

## 原代码到 Python 的映射
| node-llama-cpp | Python + API |
| --- | --- |
| getLlama / loadModel | 模型已由独立 vLLM 或 API 服务托管 |
| createContext | 上下文由模型服务管理 |
| LlamaChatSession.prompt | client.chat.completions.create |
| dispose | 关闭 HTTP Client |

## 公共模型客户端
项目将配置放在 utils/llm_client.py 中，只保留 Qwen（vLLM）和 DeepSeek（API）。

~~~python
config = get_model_config(args.model)
with get_client(config.name) as client:
    response = client.chat.completions.create(
        model=config.model,
        messages=[{"role": "user", "content": args.prompt}],
    )
print(response.choices[0].message.content)
~~~

config.name 是方便人类选择的别名；config.model 必须是对应服务认识的真实模型 ID。Qwen 的模型 ID 从 AGENT_VLLM_MODEL 读取。

## 命令行参数
--model 切换后端；--prompt 更换输入问题。省略 --model 时读取 AGENT_MODEL_NAME。

## 运行方法
~~~bash
cp .env.example .env
# 修改 .env 中的服务地址、模型 ID、密钥
python courses/01_intro/intro.py
python courses/01_intro/intro.py --model DeepSeekV4.1-Flash
~~~

## 常见错误
- Connection refused：服务地址不通或 vLLM 未启动。
- 401：API Key 无效或未配置。
- 404 model not found：模型 ID 与服务不符。
- 找不到 utils：确认从仓库目录运行。

## 学习练习
修改 Prompt，分别使用本地 Qwen 和 DeepSeek，观察同一问题的不同回答；注意输出差异不等于准确性差异。
