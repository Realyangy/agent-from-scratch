"""06: Tool calling with persistent, deduplicated JSON memory."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from memory_manager import MemoryManager
from utils.llm_client import MODEL_NAMES, get_client, get_model_config
from utils.tool_loop import function_tool, run_tool_loop

MEMORY_TOOL = function_tool(
    "saveMemory", "Save a genuinely new user fact or preference, or update a changed value",
    {
        "type": {"type": "string", "enum": ["fact", "preference"]},
        "key": {"type": "string", "description": "Short identifier, e.g. favorite_food"},
        "value": {"type": "string", "description": "Exact information to remember"},
    },
    ["type", "key", "value"],
)


def main() -> None:
    parser = argparse.ArgumentParser(description="06 - Persistent memory agent")
    parser.add_argument("--model", choices=MODEL_NAMES, default=None)
    parser.add_argument("--memory-file", type=Path, default=ROOT / "output" / "agent-memory.json")
    parser.add_argument("--prompt", action="append", help="User message; repeat to send multiple turns")
    parser.add_argument("--enable-thinking", action="store_true")
    parser.add_argument("--max-steps", type=int, default=6)
    args = parser.parse_args()

    config = get_model_config(args.model)
    memory = MemoryManager(args.memory_file)
    user_messages = args.prompt or [
        "Hi! My name is Alex and I love pizza.",
        "What's my favorite food?",
    ]
    messages = []

    with get_client(config.name) as client:
        for prompt in user_messages:
            # Refresh the summary before each turn, so newly saved facts are visible.
            system = (
                "You are a helpful assistant with long-term memory. "
                "Compare new information with the stored memories. "
                "Use saveMemory only for new or changed facts/preferences; "
                "never save duplicates. Answer questions using the memories.\n\n"
                + memory.summary()
            )
            if not messages:
                messages.append({"role": "system", "content": system})
            else:
                messages[0] = {"role": "system", "content": system}
            messages.append({"role": "user", "content": prompt})
            print(f"User: {prompt}")

            def log_tool(name: str, arguments: dict, result: str) -> None:
                print(f"[memory] {result}")

            answer = run_tool_loop(
                client, config, messages, [MEMORY_TOOL],
                {"saveMemory": memory.add_memory},
                enable_thinking=args.enable_thinking,
                max_steps=args.max_steps, on_tool=log_tool,
            )
            print(f"AI: {answer}\n")
    print(f"Memory file: {memory.path}")


if __name__ == "__main__":
    main()
