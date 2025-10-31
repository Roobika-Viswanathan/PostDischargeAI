import json
import os
from datetime import datetime
from typing import Any, Dict
from .config import settings


def _ensure_file(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("")


def log_agent_event(event: Dict[str, Any]) -> None:
    _ensure_file(settings.agent_audit_log_path)
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **event,
    }
    with open(settings.agent_audit_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def log_error(message: str, extra: Dict[str, Any] | None = None) -> None:
    _ensure_file(settings.error_log_path)
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": "ERROR",
        "message": message,
        "extra": extra or {},
    }
    with open(settings.error_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


