from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

LOG_PATH = Path(__file__).resolve().parents[2] / "logs" / "agent_run.jsonl"


def log_step(step: int, tool: str, args: dict[str, Any], result: Any) -> None:
    """Escribe un evento del paso del agente en un archivo JSONL."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "ts": datetime.now(UTC).isoformat(),
        "step": step,
        "tool": tool,
        "args": args,
        "result_summary": str(result)[:200],
    }

    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
