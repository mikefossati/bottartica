"""Poll the Antártica product page, diff stock vs last snapshot, alert on drops."""
import sys

from notify import NotifyError, send
from scraper import FetchError, TARGET_URL, fetch_stock
from state import append_history, load_last_state, save_state


def diff_and_alert(old: dict[str, int], new: dict[str, int]) -> list[str]:
    messages = []

    for store, new_qty in new.items():
        old_qty = old.get(store)
        if old_qty is None:
            continue  # first time we see this store — establishes baseline, not a sale
        if new_qty < old_qty:
            sold = old_qty - new_qty
            unit = "libro" if sold == 1 else "libros"
            messages.append(f"📚 Se vendió {sold} {unit} en {store} ({old_qty} → {new_qty})")

    for store in old:
        if store not in new:
            messages.append(f"⚠️ {store} ya no aparece en la página — revisar")

    return messages


def main() -> int:
    try:
        new_stock = fetch_stock(TARGET_URL)
    except FetchError as e:
        print(f"[error] fetch failed: {e}", file=sys.stderr)
        return 1

    old_stock = load_last_state()
    alerts = diff_and_alert(old_stock, new_stock)

    print(f"Fetched {len(new_stock)} stores. {len(alerts)} alert(s).")

    for msg in alerts:
        print(msg)
        try:
            send(msg)
        except NotifyError as e:
            print(f"[error] notify failed: {e}", file=sys.stderr)

    save_state(new_stock)
    append_history(new_stock)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
