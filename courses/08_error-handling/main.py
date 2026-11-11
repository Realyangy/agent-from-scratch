"""08: Fail-safe agent demo (validation, retries, fallbacks and correlation IDs).

All profile services below are deterministic *simulations*, not real accounts.
Use --all-demos to exercise success, not-found, policy and degraded failures.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from utils.llm_client import MODEL_NAMES, get_client, get_model_config
from utils.tool_loop import function_tool, run_tool_loop


class AppError(Exception):
    def __init__(
        self, code: str, message: str, *, user_message: str = "Something went wrong.",
        retryable: bool = False, details: dict | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.user_message = user_message
        self.retryable = retryable
        self.details = details or {}


class ValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(
            "VALIDATION_ERROR", message,
            user_message="Please provide a request with a user id, such as u_123.",
        )


class LLMCallError(AppError):
    def __init__(self, message: str, *, retryable: bool = True):
        super().__init__(
            "LLM_CALL_FAILED", message, retryable=retryable,
            user_message="The model is unavailable. Trying a deterministic fallback.",
        )


class ToolExecutionError(AppError):
    def __init__(self, tool: str, message: str, *, retryable: bool = False):
        super().__init__(
            "TOOL_EXECUTION_FAILED", message, retryable=retryable,
            user_message=f"Tool {tool} could not complete the request: {message}",
            details={"tool": tool},
        )


class AgentWorkflowError(AppError):
    def __init__(self, step: str, message: str, *, retryable: bool = False):
        super().__init__(
            "AGENT_WORKFLOW_FAILED", message, retryable=retryable,
            user_message="The workflow cannot complete at this time.",
            details={"step": step},
        )
        self.step = step


def with_retries(
    fn: Callable[[], Any], *, retries: int = 1,
    label: str = "operation", base_delay: float = 0.2,
) -> Any:
    """Retry only errors marked retryable, with capped exponential backoff."""
    for attempt in range(retries + 1):
        try:
            return fn()
        except Exception as exc:
            if attempt == retries or not isinstance(exc, AppError) or not exc.retryable:
                raise
            delay = min(3.0, base_delay * (2 ** attempt)) * random.uniform(1.0, 1.25)
            print(f"[retry] {label}: attempt {attempt + 1}/{retries + 1}; {delay:.2f}s")
            time.sleep(delay)
    raise AssertionError("unreachable")


def fetch_user_primary(userId: str) -> dict[str, Any]:
    """A flaky but more detailed *simulated* user service."""
    if userId == "u_999":
        raise ToolExecutionError("fetchUserFromPrimary", "User not found")
    if userId == "u_777" or random.random() < 0.2:
        raise ToolExecutionError(
            "fetchUserFromPrimary", "Temporary primary service outage", retryable=True,
        )
    last_login = datetime.now(timezone.utc) - timedelta(hours=6)
    return {
        "userId": userId, "name": "Alex Developer", "role": "Software Engineer",
        "lastLoginIso": last_login.isoformat(), "source": "primary",
    }


def fetch_user_fallback(userId: str) -> dict[str, Any]:
    """Lower-detail simulated backup; u_777 intentionally fails both paths."""
    if userId == "u_777":
        raise ToolExecutionError("fetchUserFromFallback", "Backup unavailable")
    return {
        "userId": userId, "name": "Alex Developer", "role": "Engineer",
        "lastLoginIso": None, "source": "fallback",
    }


TOOLS = [
    function_tool(
        "fetchUserFromPrimary", "Fetch a user profile from the main service",
        {"userId": {"type": "string", "description": "User ID, e.g. u_123"}},
        ["userId"],
    ),
    function_tool(
        "fetchUserFromFallback", "Fetch profile from a lower-detail backup service",
        {"userId": {"type": "string", "description": "User ID, e.g. u_123"}},
        ["userId"],
    ),
]
HANDLERS = {
    "fetchUserFromPrimary": fetch_user_primary,
    "fetchUserFromFallback": fetch_user_fallback,
}
SYSTEM = (
    "You are an IT assistant. Use the profile tools for user requests. "
    "Call the primary service first. If it reports a temporary failure, "
    "try the fallback tool. Do not invent profiles. Mention the user id "
    "and whether the information came from the fallback."
)


def resolve_without_llm(user_input: str) -> str:
    """Fallback does not need the model; retry primary and then use backup."""
    match = re.search(r"\b(u_\d+)\b", user_input, re.IGNORECASE)
    if match is None:
        raise ValidationError("No user id found for degraded resolution")
    user_id = match.group(1)

    try:
        profile = with_retries(
            lambda: fetch_user_primary(user_id),
            retries=1, label="fetchUserFromPrimary",
        )
    except ToolExecutionError as exc:
        if not exc.retryable:
            raise
        try:
            profile = fetch_user_fallback(user_id)
        except ToolExecutionError as cause:
            raise AgentWorkflowError(
                "resolve_user_profile",
                "Primary retries and fallback both failed",
                retryable=True,
            ) from cause

    return (
        "Model unavailable; returned a simulated profile via fallback workflow.\n"
        f"- User ID: {profile['userId']}\n"
        f"- Name: {profile['name']} ({profile['role']})\n"
        f"- Last login: {profile['lastLoginIso'] or 'unknown'}\n"
        f"- Source: {profile['source']}"
    )


def run_agent(
    prompt: str, client: Any | None, config: Any | None,
    *, enable_thinking: bool = False,
) -> dict[str, Any]:
    correlation_id = str(uuid.uuid4())
    try:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValidationError("Empty input")
        if re.search(r"\bu_demo_workflow\b", prompt, re.IGNORECASE):
            raise AgentWorkflowError("policy_guard", "Demo: blocked workflow branch")

        forced_degraded = bool(re.search(r"SKIP_LLM_DEGRADED\s+u_\d+", prompt, re.I))
        try:
            if forced_degraded:
                raise LLMCallError("LLM deliberately skipped for reproducible test", retryable=False)
            if client is None or config is None:
                raise LLMCallError("Client not provided", retryable=False)

            def ask_model() -> str:
                messages = [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt},
                ]
                try:
                    return run_tool_loop(
                        client, config, messages, TOOLS, HANDLERS,
                        enable_thinking=enable_thinking, max_steps=6, timeout=15.0,
                    )
                except Exception as exc:
                    raise LLMCallError(f"LLM or tool loop failed: {exc}") from exc

            output = with_retries(ask_model, retries=1, label="LLM request")
        except LLMCallError as exc:
            print(f"[degraded_mode] {exc}")
            output = resolve_without_llm(prompt)
        return {"ok": True, "correlation_id": correlation_id, "output": output}
    except AppError as exc:
        if isinstance(exc, AgentWorkflowError):
            print(f"[workflow_error] step={exc.step}; code={exc.code}; id={correlation_id}")
        print(f"[agent_error] {exc.code}: {exc}; details={exc.details}")
        return {
            "ok": False, "correlation_id": correlation_id,
            "output": f"{exc.user_message} (Reference: {correlation_id})",
        }


DEMO_REQUESTS = [
    "Fetch user u_123 and summarize their profile in 2 bullet points.",
    "Fetch user u_999 and tell me when they last logged in.",
    "Please fetch profile for u_demo_workflow.",
    "SKIP_LLM_DEGRADED u_777",
    "",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="08 - Agent error handling and fallback")
    parser.add_argument("--model", choices=MODEL_NAMES, default=None)
    parser.add_argument("--prompt", default=DEMO_REQUESTS[0])
    parser.add_argument("--all-demos", action="store_true")
    parser.add_argument("--enable-thinking", action="store_true")
    args = parser.parse_args()

    prompts = DEMO_REQUESTS if args.all_demos else [args.prompt]
    # Deterministic degraded-mode demonstrations require no LLM client.
    needs_model = any(
        p.strip() and "SKIP_LLM_DEGRADED" not in p and "u_demo_workflow" not in p
        for p in prompts
    )
    if needs_model:
        config = get_model_config(args.model)
        with get_client(config.name) as client:
            for prompt in prompts:
                result = run_agent(prompt, client, config, enable_thinking=args.enable_thinking)
                print(f"User: {prompt!r}\nResult: {json.dumps(result, ensure_ascii=False, indent=2)}\n")
    else:
        for prompt in prompts:
            result = run_agent(prompt, None, None, enable_thinking=args.enable_thinking)
            print(f"User: {prompt!r}\nResult: {json.dumps(result, ensure_ascii=False, indent=2)}\n")


if __name__ == "__main__":
    main()
