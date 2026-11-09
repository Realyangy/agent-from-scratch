## 命令行参数
`--model` 是使用的模型， 缺失时读取 AGENT_MODEL_NAME；
`--prompt` 是输入的提示词。

## 运行方法
~~~bash
# 修改 .env 中的服务地址、模型 ID、密钥
python courses/01_intro/intro.py
python courses/01_intro/intro.py --model DeepSeekV4.1-Flash
~~~
