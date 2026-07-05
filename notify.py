"""Send alert messages via Telegram."""
import os

import requests

API_BASE = "https://api.telegram.org"


class NotifyError(Exception):
    pass


def send(message: str) -> None:
    """Send `message` to every chat id in TELEGRAM_CHAT_ID (comma-separated)."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_ids_raw = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_ids_raw:
        raise NotifyError("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set")

    chat_ids = [c.strip() for c in chat_ids_raw.split(",") if c.strip()]
    errors = []
    for chat_id in chat_ids:
        resp = requests.post(
            f"{API_BASE}/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message},
            timeout=15,
        )
        if resp.status_code != 200:
            errors.append(f"chat_id {chat_id}: HTTP {resp.status_code} {resp.text}")

    if errors:
        raise NotifyError("; ".join(errors))
