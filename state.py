"""Persist last-known stock snapshot and append-only history to disk."""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
STATE_PATH = DATA_DIR / "last_state.json"
HISTORY_PATH = DATA_DIR / "history.csv"


def load_last_state() -> dict[str, int]:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {}


def save_state(stock: dict[str, int]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(stock, ensure_ascii=False, indent=2, sort_keys=True))


def append_history(stock: dict[str, int], fetched_at: str | None = None) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fetched_at = fetched_at or datetime.now(timezone.utc).isoformat()
    is_new = not HISTORY_PATH.exists()
    with HISTORY_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["fetched_at", "store", "quantity"])
        for store, qty in sorted(stock.items()):
            writer.writerow([fetched_at, store, qty])
