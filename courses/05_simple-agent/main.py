"""05: First agent—call a real Python function through LLM tool calling."""
import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from utils.llm_client import MODEL_NAMES, get_client, get_model_config
from utils.tool_loop import function_tool, run_tool_loop

SYSTEM_PROMPT = (
    "You are a professional chronologist. When the user asks for the current "
    "time, use the getCurrentTime tool. Convert the tool's 12-hour clock into "
    "24-hour HH:MM format without seconds. Never invent the current time."
)
TOOLS = [function_tool("getCurrentTime", "Get the current local time as a 12-hour clock string")]


def get_current_time() -> str:
    return datetime.now().strftime("%I:%M:%S %p")


def main() -> None:
    parser = argparse.ArgumentParser(description="05 - First tool-calling agent")
    parser.add_argument("--model", choices=MODEL_NAMES, default=None)
    parser.add_argument("--prompt", default="What time is it right now?")
    parser.add_argument("--enable-thinking", action="store_true")
    parser.add_argument("--max-steps", type=int, default=5)
    args = parser.parse_args()

    config = get_model_config(args.model)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": args.prompt},
    ]

    def log_tool(name: str, arguments: dict, result: str) -> None:
        print(f"[tool] {name}({arguments}) => {result}")

    with get_client(config.name) as client:
        answer = run_tool_loop(
            client, config, messages, TOOLS, {"getCurrentTime": get_current_time},
            enable_thinking=args.enable_thinking, max_steps=args.max_steps,
            on_tool=log_tool,
        )
    print("AI:", answer)


if __name__ == "__main__":
    main()
