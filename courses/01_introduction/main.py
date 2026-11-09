import sys
import argparse
from pathlib import Path

# 根目录的获取：__file__是当前文件的路径，resolve()获取绝对路径，parents[2]获取上两级目录
ROOT_DIR = Path(__file__).resolve().parents[2]

# 将根目录加入查找模块时的路径列表，这里的0表示插入第一个位置
sys.path.insert(0, str(ROOT_DIR))

from utils.llm_client import MODEL_NAMES, get_client, get_model_config


def main() -> None:
    parser = argparse.ArgumentParser(description="调用模型完成对话")
    parser.add_argument("--model", choices=MODEL_NAMES, default=None)
    parser.add_argument("--prompt", default="What is an AI agent? Explain briefly.")
    args = parser.parse_args()

    config = get_model_config(args.model)
    with get_client(config.name) as client:
        response = client.chat.completions.create(
            model=config.model,
            messages=[{
                "role": "user",
                "content": args.prompt
            }],
        )
    print("AI:", response.choices[0].message.content)


if __name__ == "__main__":
    main()
