# 03 专业翻译｜CODE

对应当前课程的 `translation.py`。原项目的 `translation.js` 已从本仓库删除，历史版本仍可通过 Git 查看；下面介绍 Python 实现。

## 1. 模型切换
~~~python
config = get_model_config(args.model)
with get_client(config.name) as client:
    response = client.chat.completions.create(
        model=config.model,
        messages=messages,
        temperature=0.2,
    )
~~~
模型由外部 vLLM 或 API 服务托管，当前环境只运行 Python 代码。

## 2. 德语 System Prompt
原版的长提示词强调专业性、忠实性、自然德语和禁止额外解释。新版保留完整的德语任务指令，例如：
~~~text
Du bist ein erfahrener wissenschaftlicher Übersetzer ...
Gib ausschließlich den übersetzten Text aus.
~~~
中文含义：你是一位有经验的科学翻译人员；忠实保留事实与专业术语；采用自然科研写作风格；仅输出译文。

## 3. User Prompt
~~~python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": f"Translate this text into German:\n\n{SOURCE_TEXT}"},
]
~~~
SOURCE_TEXT 与原 JS 的 HexMachina 英文摘要对应，包含长时规划、Settlers of Catan、环境探索与策略优化、54 % 胜率等内容。示例保留了原文中的跨行断词；实际翻译系统建议先清理 PDF 提取产生的断词。

## 4. 输出
直接打印 response.choices[0].message.content。返回纯文本并非强制保证，专业翻译任务应额外核对数字和术语。

## 运行
~~~bash
python courses/03_translation/translation.py
python courses/03_translation/translation.py --model DeepSeekV4.1-Flash
~~~

## 练习
将 system 指令改为英译中、摘要润色或技术术语规范化，并比较结果。不要把 Prompt 约束误认为形式化的正确性验证。
