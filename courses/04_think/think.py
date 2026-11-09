"""课程 04：只靠模型做复杂的计数与定量推理（不调用工具）。"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.llm_client import MODEL_NAMES, get_client, get_model_config

SYSTEM_PROMPT = """You are an expert logical and quantitative reasoner.
Analyze the quantities, family relations and exceptions carefully.
Return only the final number of whole bags, without explanation.
"""

QUESTION = """My family reunion is this week, and I was assigned the mashed potatoes
to bring. The attendees include my married mother and father, my twin brother
and his family, my aunt and her family, my grandma and her brother, her
brother's daughter, and his daughter's family. All the adults but me have been
married, and no one is divorced or remarried, but my grandpa and my grandma's
sister-in-law passed away last year. All living spouses are attending.
My brother has two children that are still kids, my aunt has one six-year-old,
and my grandma's brother's daughter has three kids under 12. Each adult will
eat about 1.5 potatoes and each kid will eat about 1/2 a potato, except my
second cousins don't eat carbs. The average potato weighs half a pound, and
potatoes are sold in 5-pound bags.

How many whole bags of potatoes do I need?"""


def main() -> None:
    parser = argparse.ArgumentParser(description="04 - LLM 定量推理")
    parser.add_argument("--model", choices=MODEL_NAMES, default=None)
    args = parser.parse_args()
    config = get_model_config(args.model)
    with get_client(config.name) as client:
        response = client.chat.completions.create(
            model=config.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": QUESTION},
            ],
            temperature=0,
            max_tokens=300,
        )
    print("AI:", response.choices[0].message.content)
    print("提示：这个示例不使用计算器；LLM 的数字答案不保证正确。")


if __name__ == "__main__":
    main()
