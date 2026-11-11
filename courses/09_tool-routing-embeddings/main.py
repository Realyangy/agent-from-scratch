"""09: Embedding-based tool routing before a Chat Completions tool loop.

Twelve simulated helpdesk tools are defined, but only the top-k semantically
relevant tool schemas are sent to the LLM on each request.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from utils.llm_client import MODEL_NAMES, get_client, get_model_config
from utils.tool_loop import function_tool, run_tool_loop


def check_network_connectivity(target: str = "8.8.8.8") -> dict:
    return {"target": target, "ping_ms": 24, "packet_loss_pct": 0,
            "dns_resolution": "ok", "status": "connected", "simulated": True}


def check_vpn_status(username: str = "current_user") -> dict:
    return {"username": username, "vpn_client": "Cisco AnyConnect 4.10",
            "connected": False, "profile": "Corp-HQ",
            "error": "Authentication timeout: check MFA token", "simulated": True}


def get_system_logs(severity: str = "error", last_hours: float = 24) -> dict:
    return {"severity": severity, "last_hours": last_hours, "log_count": 7,
            "top_events": ["Unexpected reboot", "GPU driver crash", "Disk I/O error"],
            "simulated": True}


def check_disk_space() -> dict:
    return {"drives": [{"drive": "C:", "total_gb": 256, "free_gb": 18, "pct_used": 93},
                       {"drive": "D:", "total_gb": 1024, "free_gb": 714, "pct_used": 30}],
            "warning": "C: drive is critically full", "simulated": True}


def get_installed_software(filter: str = "") -> dict:
    apps = [{"name": "Microsoft 365", "version": "16.0.17231"},
            {"name": "Google Chrome", "version": "124.0.6367"},
            {"name": "Zoom", "version": "5.17.6"}]
    return {"apps": [a for a in apps if filter.lower() in a["name"].lower()],
            "simulated": True}


def get_user_account(username: str) -> dict:
    return {"username": username, "status": "locked",
            "reason": "Too many failed login attempts", "mfa_enabled": True,
            "simulated": True}


def reset_password(username: str, method: str = "email") -> dict:
    return {"username": username, "reset_initiated": True,
            "method": method, "simulated": True}


def run_diagnostic(test: str) -> dict:
    results = {
        "memory": {"passed": True, "errors": 0},
        "gpu": {"passed": False, "recommendation": "Update GPU driver"},
        "startup": {"passed": True, "boot_time_s": 38},
        "storage": {"passed": False, "bad_sectors": 3},
    }
    return {"test": test, "result": results.get(test, {"error": "Unknown test"}),
            "simulated": True}


def get_hardware_info() -> dict:
    return {"cpu": "Intel Core i7-12700H", "ram_gb": 16,
            "gpu": "NVIDIA RTX 3060", "os": "Windows 11 Pro", "simulated": True}


def restart_service(service_name: str) -> dict:
    return {"service_name": service_name, "restarted": True, "simulated": True}


def create_support_ticket(summary: str, priority: str, category: str) -> dict:
    return {"ticket_id": f"INC-{random.randint(100000, 999999)}",
            "summary": summary, "priority": priority, "category": category,
            "status": "open", "simulated": True}


def escalate_to_specialist(team: str, reason: str) -> dict:
    return {"escalated": True, "team": team, "reason": reason, "simulated": True}


STRING = {"type": "string"}
TOOL_SPECS: list[tuple[str, str, dict, list[str], Callable[..., Any]]] = [
    ("checkNetworkConnectivity", "Check Internet or network connectivity and packet loss",
     {"target": STRING}, [], check_network_connectivity),
    ("checkVPNStatus", "Check VPN tunnel connection, client and authentication status",
     {"username": STRING}, [], check_vpn_status),
    ("getSystemLogs", "Fetch recent system event logs and crash reports",
     {"severity": STRING, "last_hours": {"type": "number"}}, [], get_system_logs),
    ("checkDiskSpace", "Check free disk space and storage usage", {}, [], check_disk_space),
    ("getInstalledSoftware", "List installed software versions",
     {"filter": STRING}, [], get_installed_software),
    ("getUserAccount", "Check if an Active Directory account is locked",
     {"username": STRING}, ["username"], get_user_account),
    ("resetPassword", "Start a password reset process for an account",
     {"username": STRING, "method": STRING}, ["username"], reset_password),
    ("runDiagnostic", "Run GPU, memory, storage or startup diagnostics",
     {"test": STRING}, ["test"], run_diagnostic),
    ("getHardwareInfo", "Inspect computer CPU, RAM and GPU specifications",
     {}, [], get_hardware_info),
    ("restartService", "Restart a Windows background service",
     {"service_name": STRING}, ["service_name"], restart_service),
    ("createSupportTicket", "Create a helpdesk support incident ticket",
     {"summary": STRING, "priority": STRING, "category": STRING},
     ["summary", "priority", "category"], create_support_ticket),
    ("escalateToSpecialist", "Escalate an incident to specialist team",
     {"team": STRING, "reason": STRING}, ["team", "reason"], escalate_to_specialist),
]

ALL_TOOLS = {name: function_tool(name, description, properties, required)
             for name, description, properties, required, _ in TOOL_SPECS}
ALL_HANDLERS = {name: fn for name, _, _, _, fn in TOOL_SPECS}

# Each tool has several short semantic exemplars. The model uses embeddings,
# not exact keyword matches, to measure user intent similarity.
EXEMPLARS: dict[str, list[str]] = {
    "checkNetworkConnectivity": [
        "internet disconnected, browser cannot load websites",
        "network ping test and packet loss to server",
        "wifi connection is broken",
    ],
    "checkVPNStatus": [
        "corporate remote VPN tunnel cannot connect",
        "Cisco AnyConnect authenticating forever then timing out",
        "VPN client disconnected while working remotely",
    ],
    "getSystemLogs": [
        "windows blue screen crash event viewer",
        "fetch application error and system logs",
        "computer unexpectedly restarted, inspect crash events",
    ],
    "checkDiskSpace": [
        "disk almost full and not enough free storage",
        "C drive shows low space warning",
        "check volume capacity and disk usage",
    ],
    "getInstalledSoftware": [
        "find software build number and version",
        "which office applications are installed",
        "list installed programs and updates",
    ],
    "getUserAccount": [
        "account locked after too many invalid passwords",
        "check login user permissions and directory status",
        "verify disabled account and group membership",
    ],
    "resetPassword": [
        "forgot password and cannot sign in",
        "send password reset email link",
        "user credentials expired and need to be reset",
    ],
    "runDiagnostic": [
        "run hardware diagnostic for GPU crash",
        "memory stress test to find faulty ram",
        "test disk and storage hardware for faults",
    ],
    "getHardwareInfo": [
        "what are the RAM CPU and GPU specifications",
        "hardware serial number and component inventory",
        "computer specs for compatibility",
    ],
    "restartService": [
        "restart frozen windows print spooler",
        "reboot a background service that stopped responding",
        "cycle Windows Update service",
    ],
    "createSupportTicket": [
        "open a new helpdesk ticket for incident",
        "log formal support request and follow up",
        "create incident record with severity",
    ],
    "escalateToSpecialist": [
        "ask security specialists to investigate intrusion",
        "escalate issue to networking engineer",
        "send unresolved incident to expert team",
    ],
}

DEMO_CASES = [
    ("VPN failure", "Working from a cafe, the Cisco client times out while connecting.", 1, []),
    ("Locked account", "I entered my Windows password incorrectly too many times, now my account is blocked.", 1, []),
    ("Crash investigation", "My laptop blue-screened twice. Check crash logs AND run hardware diagnostics.", 2, []),
    ("Disk and software", "Storage is full and I need to know which version of Office is installed.", 2, []),
    ("Two intents with k=1", "VPN sign-in failed, and also my Windows account is locked.", 1, []),
    ("Pinned account tool", "VPN sign-in failed, and also my Windows account is locked.", 1, ["getUserAccount"]),
]


def score_tools(query_embedding: Any, exemplar_embeddings: Any) -> dict[str, float]:
    """Max cosine similarity over every exemplar belonging to each tool.

    sentence-transformers.encode(normalize_embeddings=True) produces unit
    vectors, so dot product equals cosine similarity.
    """
    scores: dict[str, float] = {}
    index = 0
    for key, examples in EXEMPLARS.items():
        for _ in examples:
            score = float(query_embedding @ exemplar_embeddings[index])
            scores[key] = max(scores.get(key, -1.0), score)
            index += 1
    return scores


def select_tool_keys(scores: dict[str, float], k: int,
                     always_include: list[str] | None = None) -> list[str]:
    if k < 1:
        raise ValueError("k must be >= 1")
    pinned = always_include or []
    unknown = set(pinned) - set(ALL_TOOLS)
    if unknown:
        raise ValueError(f"Unknown pinned tools: {sorted(unknown)}")
    ranked = sorted(scores, key=scores.__getitem__, reverse=True)
    # Pinning is additive: expose top k plus always-include tools.
    return list(dict.fromkeys(ranked[:k] + pinned))


def main() -> None:
    parser = argparse.ArgumentParser(description="09 - Embedding tool router")
    parser.add_argument("--model", choices=MODEL_NAMES, default=None)
    parser.add_argument("--embedding-model", default="sentence-transformers/all-MiniLM-L6-v2",
                        help="Local or cached sentence-transformers model")
    parser.add_argument("--prompt", help="One request; otherwise run six demo cases")
    parser.add_argument("--k", type=int, default=2, help="Top-k tools sent to the LLM")
    parser.add_argument("--always-include", action="append", default=[],
                        choices=list(ALL_TOOLS), help="Tool pinned alongside top-k")
    parser.add_argument("--max-steps", type=int, default=6)
    parser.add_argument("--enable-thinking", action="store_true")
    args = parser.parse_args()

    # Imported lazily so other Agent lessons don't require an embedding model.
    from sentence_transformers import SentenceTransformer

    embedder = SentenceTransformer(args.embedding_model)
    texts = [example for examples in EXEMPLARS.values() for example in examples]
    exemplar_embeddings = embedder.encode(texts, normalize_embeddings=True)
    config = get_model_config(args.model)
    cases = [("Custom request", args.prompt, args.k, args.always_include)] if args.prompt else DEMO_CASES

    with get_client(config.name) as client:
        for label, prompt, k, pinned in cases:
            query_embedding = embedder.encode(prompt, normalize_embeddings=True)
            scores = score_tools(query_embedding, exemplar_embeddings)
            selected = select_tool_keys(scores, k, pinned)
            print(f"\n=== {label} ===")
            print(f"User: {prompt}")
            for name in sorted(scores, key=scores.__getitem__, reverse=True)[:6]:
                tick = "*" if name in selected else " "
                print(f"[{tick}] {name}: {scores[name]:.4f}")
            print(f"Exposed {len(selected)}/{len(ALL_TOOLS)} tools: {selected}")

            messages = [
                {"role": "system", "content": (
                    "You are a helpful IT helpdesk agent. The tools provide SIMULATED "
                    "sample results, not real account, hardware or service operations. "
                    "Call relevant tools where available. Never fabricate a tool result; "
                    "acknowledge unavailable tools if a request cannot be completed."
                )},
                {"role": "user", "content": prompt},
            ]
            tools = [ALL_TOOLS[name] for name in selected]
            handlers = {name: ALL_HANDLERS[name] for name in selected}

            def log_tool(name: str, args: dict, result: str) -> None:
                print(f"[tool] {name}({json.dumps(args, ensure_ascii=False)}) -> {result}")

            answer = run_tool_loop(
                client, config, messages, tools, handlers,
                enable_thinking=args.enable_thinking,
                max_steps=args.max_steps,
                on_tool=log_tool,
            )
            print("AI:", answer)


if __name__ == "__main__":
    main()
