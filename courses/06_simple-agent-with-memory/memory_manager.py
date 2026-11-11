"""Local JSON long-term memory, with deduplication and legacy-format migration."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class MemoryManager:
    def __init__(self, path: Path | str):
        self.path = Path(path)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"memories": [], "conversationHistory": []}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Memory file must contain a JSON object")
        if "memories" not in data:
            converted = {"memories": [], "conversationHistory": []}
            for item in data.get("facts", []):
                raw = str(item.get("content", ""))
                key, _, value = raw.partition(":")
                converted["memories"].append({
                    "type": "fact", "key": key.strip() or "unknown",
                    "value": (value or raw).strip(), "source": "migration",
                    "timestamp": item.get("timestamp") or self._now(),
                })
            for key, value in data.get("preferences", {}).items():
                converted["memories"].append({
                    "type": "preference", "key": str(key), "value": str(value),
                    "source": "migration", "timestamp": self._now(),
                })
            self.save(converted)
            return converted
        data.setdefault("conversationHistory", [])
        if not isinstance(data["memories"], list):
            raise ValueError("memories must be a list")
        return data

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Replace atomically to avoid corrupting the original file on a partial write.
        temporary = self.path.with_name(self.path.name + ".tmp")
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(self.path)

    def add_memory(self, type: str, key: str, value: str) -> str:
        kind, normalized_key, normalized_value = type.strip().lower(), key.strip().lower(), value.strip()
        if kind not in {"fact", "preference"}:
            raise ValueError("type must be 'fact' or 'preference'")
        if not normalized_key or not normalized_value:
            raise ValueError("key and value cannot be empty")

        data = self.load()
        for item in data["memories"]:
            if item.get("type") == kind and str(item.get("key", "")).lower() == normalized_key:
                if item.get("value") == normalized_value:
                    return f"Skipped duplicate memory: {normalized_key}"
                item.update(value=normalized_value, timestamp=self._now(), source="user")
                self.save(data)
                return f"Updated memory: {normalized_key} = {normalized_value}"

        data["memories"].append({
            "type": kind, "key": normalized_key, "value": normalized_value,
            "source": "user", "timestamp": self._now(),
        })
        self.save(data)
        return f"Saved memory: {normalized_key} = {normalized_value}"

    def summary(self) -> str:
        data = self.load()
        lines = ["=== LONG-TERM MEMORY ==="]
        for kind, heading in (("fact", "Known facts"), ("preference", "Preferences")):
            items = [m for m in data["memories"] if m.get("type") == kind]
            if items:
                lines.append(heading + ":")
                lines.extend(f"- {m['key']}: {m['value']}" for m in items)
        return "\n".join(lines)
