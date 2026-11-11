# 04 复杂数量题｜CODE

对应当前课程的 `think.py`。原项目的 `think.js` 已从本仓库删除，历史版本仍可通过 Git 查看；下面介绍 Python 实现。

## 1. System Prompt
~~~python
SYSTEM_PROMPT = """You are an expert logical and quantitative reasoner.
Analyze the quantities, family relations and exceptions carefully.
Return only the final number of whole bags, without explanation.
"""
~~~
要求模型处理逻辑与数量问题，并限制输出内容。

## 2. 问题
QUESTION 保留原示例中家庭成员数量、婚姻与存活、孩子、土豆摄入量和每袋五磅的条件；最终问题为：How many whole bags of potatoes do I need?

## 3. 推理调用
~~~python
response = client.chat.completions.create(
    model=config.model,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": QUESTION},
    ],
    temperature=0,
    max_tokens=300,
)
~~~
温度为 0 有助于减小随机性，但不保证算术正确。max_tokens 限制输出预算；某些推理模型可能需要调整。

## 4. 打印结果
返回字段是 response.choices[0].message.content。此课程不假设必然可以直接转换为整数；若用于自动评测应增加解析和验证。

## 运行
~~~bash
python courses/04_think/think.py
python courses/04_think/think.py --model DeepSeekV4.1-Flash
~~~

## 原版与 Python 版的区别
原版在本地加载 Qwen3 GGUF；新版通过独立 vLLM 或 API 调用，任务思想仍是“单次调用解决复杂推理题”。

## 练习
使用纸笔或独立 Python 代码验证袋数，记录 LLM 漏算或误算的情况。第 07 节以后可通过计算器工具改进。
