import json
import sys
from pathlib import Path
from typing import TypeAlias

# MonitorID -> {"name": str, "status": bool, "page_base_url": str}
MonitorRecord = dict[str, str | bool]
StateDict: TypeAlias = dict[str, MonitorRecord]

STATE_PATH = Path.home() / ".uptime__state.json"

def load() -> StateDict:
    # Load and return the previous state from disk."""
    if not STATE_PATH.exists():
        return {}

    try:
        text = STATE_PATH.read_text(encoding="utf-8")
        return json.loads(text)
    except json.JSONDecodeError as exc:
        print(
            f"[uptimerobot4discord] Warning: state file is corrupt and will be "
            f"reset ({exc}).",
            file=sys.stderr,
        )
        return {}

def save(state: StateDict) -> None:
    # Overwrite the state file with the current live state dict.
    STATE_PATH.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
