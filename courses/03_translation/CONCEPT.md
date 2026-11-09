# 03 System Prompt 与专门化｜CONCEPT

## 目标
用 System Prompt 将通用模型配置为一个专业英译德助手，而不是训练新模型。

## System Prompt 是什么？
系统提示词对当前请求给出角色、目标、约束、风格与格式。它通常比 User Prompt 更稳定地表达全局任务，但自然语言规则不能保证被模型绝对遵循。

## 翻译任务中的五个要素
1. Role：专业科学与工程翻译人员。
2. Goal：将英文技术文本译成自然、准确的德语。
3. Constraint：保留事实、数字、单位及专业术语。
4. Style：符合科研写作语气，避免机械逐词翻译。
5. Output：只返回翻译结果，不加入解释。

## 原例为什么用德语系统提示词？
原作者希望模型遵循目标语言的风格要求，例如正确使用德语复合词、科学表达以及数字排版。本 Python 版继续保留德语 Prompt 的核心指令，解释文档用中文。

## 角色、任务和格式
~~~text
System: You are a professional technical translator.
User: Translate this text into German: ...
Assistant: <德语译文>
~~~
system 适合放稳定的任务规则，user 放本次输入材料。

## Prompt 设计模式
- Role-based：指定助手身份。
- Rule-based：列出必须遵循的约束。
- Format-constrained：要求纯译文或 JSON。
- Context-aware：加入术语表、上下文和领域信息。

## Chat Template
原版 node-llama-cpp 负责对模型包装消息；在 API 架构下，客户端发送 role/content，具体聊天模板由服务端管理。不同模型对系统消息的支持程度可能不同。

## 与 Agent 的关系
仅有 System Prompt 的专业助手通常还是一个单轮 LLM 应用。Agent 的工具调用、长期记忆及迭代决策将在后续章节学习。

## 练习
去掉“仅输出译文”的要求，观察模型是否添加解释。为翻译任务增加术语表，检查译文专业词汇是否更加一致。
