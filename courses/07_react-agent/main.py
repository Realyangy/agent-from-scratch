"""07: ReAct-style iterative calculator agent using real tool-call observations."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from utils.llm_client import MODEL_NAMES, get_client, get_model_config
from utils.tool_loop import function_tool, run_tool_loop

SYSTEM_PROMPT = (
    "You are a mathematical assistant using Reasoning + Acting (ReAct). "
    "For any arithmetic operation, call one calculator tool and use its returned "
    "result as the next observation. Do not fabricate tool results. "
    "Continue until every requested quantity is calculated; then answer concisely."
)
DEFAULT_PROMPT = (
    "A store sells 15 items on Monday at $8 each, 20 items on Tuesday at $8 each, "
    "and 10 items on Wednesday at $8 each. What's the average number of items "
    "sold per day, and what's the total revenue?"
)
NUMBER_PROPERTIES = {"a": {"type": "number"}, "b": {"type": "number"}}
TOOLS = [
    function_tool("add", "Add two numbers", NUMBER_PROPERTIES, ["a", "b"]),
    function_tool("multiply", "Multiply two numbers", NUMBER_PROPERTIES, ["a", "b"]),
    function_tool("subtract", "Subtract b from a", NUMBER_PROPERTIES, ["a", "b"]),
    function_tool("divide", "Divide a by b", NUMBER_PROPERTIES, ["a", "b"]),
]


def add(a: float, b: float) -> float:
    return a + b


def multiply(a: float, b: float) -> float:
    return a * b


def subtract(a: float, b: float) -> float:
    return a - b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


HANDLERS = {"add": add, "multiply": multiply, "subtract": subtract, "divide": divide}


def main() -> None:
    parser = argparse.ArgumentParser(description="07 - ReAct with calculator tools")
    parser.add_argument("--model", choices=MODEL_NAMES, default=None)
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--enable-thinking", action="store_true")
    parser.add_argument("--max-steps", type=int, default=12)
    args = parser.parse_args()

    config = get_model_config(args.model)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": args.prompt},
    ]

    def log_action(name: str, params: dict, result: str) -> None:
        print(f"Action: {name}({params})")
        print(f"Observation: {result}")

    with get_client(config.name) as client:
        answer = run_tool_loop(
            client, config, messages, TOOLS, HANDLERS,
            enable_thinking=args.enable_thinking, max_steps=args.max_steps,
            on_tool=log_action,
        )
    print("Answer:", answer)


if __name__ == "__main__":
    main()
