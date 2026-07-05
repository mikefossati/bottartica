"""Send alert messages via Telegram."""
import os

import requests

API_BASE = "https://api.telegram.org"


class NotifyError(Exception):
    pass


def send(message: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise NotifyError("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set")

    resp = requests.post(
        f"{API_BASE}/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": message},
        timeout=15,
    )
    if resp.status_code != 200:
        raise NotifyError(f"Telegram API error {resp.status_code}: {resp.text}")
