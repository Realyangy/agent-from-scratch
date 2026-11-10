import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.llm_client import MODEL_NAMES, ModelConfig, get_client, get_model_config, print_token_usage, call_llm


def run_examples(config: ModelConfig) -> None:
    print(f"Current model: {config.name} ({config.model})\n")

    with get_client(config.name) as client:

        # 第一部分：基础的文本生成
        print("===== 1. Basic completion =====")
        messages = [{"role": "user", "content": "What is an AI agent in one sentence?"}]
        response = call_llm(client, config, messages)
        print(response.choices[0].message.content, "\n")


        # 第二部分：使用系统提示词，调用LLM时需要传入消息列表
        print("\n===== 2. System prompt =====")
        messages = [
            {"role": "system", "content": "You are a coding tutor. Answer with a short example."},
            {"role": "user", "content": "Explain Python async/await."},
        ]
        response = call_llm(client, config, messages)
        print(response.choices[0].message.content)


        # 第三部分：用采样参数temperature控制输出的随机性
        print("\n===== 3. Temperature =====")
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "Write a one-line tagline for a coffee shop."},
        ]
        for temp in (0.2, 0.8):
            response = call_llm(client, config, messages, temperature=temp)
            print(f"temp = {temp}:", response.choices[0].message.content)


        # 第四部分：多轮对话
        print("\n===== 4. Multi-turn conversation =====")
        messages = [
            {"role": "system", "content": "You are a helpful Python tutor."},
            {"role": "user", "content": "What is a Python generator?"},
        ]
        first = call_llm(client, config, messages, max_tokens=200)
        answer = first.choices[0].message.content
        print(f"Question 1: {messages[-1]['content']}\nAI: {answer}")

        messages.append({"role": "assistant", "content": answer})
        messages.append({"role": "user", "content": "Show a simple example."})
        second = call_llm(client, config, messages, max_tokens=300)
        answer = second.choices[0].message.content
        print(f"Question 2: {messages[-1]['content']}\nAI: {answer}")

        # 第五部分：流式输出
        print("\n===== 5. Streaming =====")
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "Write a haiku about programming."},
        ]
        stream = call_llm(client, config, messages, stream=True, max_tokens=150)
        print("AI: ", end="", flush=True)
        for chunk in stream:
            if chunk.choices:
                print(chunk.choices[0].delta.content or "", end="", flush=True)

        # 第六部分：统计Token开销
        print("\n===== 6. Token usage =====")
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "Explain recursion in 3 sentences."},
        ]
        response = call_llm(client, config, messages, max_tokens=200)
        print(response.choices[0].message.content)
        print_token_usage(response.usage)


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenAI接口调用LLM")
    parser.add_argument("--model", choices=MODEL_NAMES, default=None)
    args = parser.parse_args()

    model_config = get_model_config(args.model)
    run_examples(model_config)


if __name__ == "__main__":
    main()
