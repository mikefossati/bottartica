# bottartica

Polls a single Antártica (antartica.cl) book product page hourly, tracks per-store
physical stock, and sends a Telegram alert whenever it changes: a copy sold, a
restock, or a store newly listing the book.

## Setup

1. Create a Telegram bot: message [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token.
2. Get your chat id: send your new bot any message, then open
   `https://api.telegram.org/bot<TOKEN>/getUpdates` and read `message.chat.id`.
3. Copy `.env.example` to `.env` and fill in `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`
   (for local runs), or add them as GitHub repo secrets (Settings → Secrets and
   variables → Actions) for the scheduled workflow.
4. `pip install -r requirements.txt`
5. `python main.py` to run once locally.

The GitHub Actions workflow (`.github/workflows/poll.yml`) runs this hourly and
commits the updated `data/last_state.json` / `data/history.csv` back to the repo.

## How it works

- `scraper.py` fetches the product page and parses the `table.tiendas_stocks`
  store-inventory table (store name + exact quantity per store).
- `state.py` persists the last-seen quantity per store (`data/last_state.json`)
  and an append-only log (`data/history.csv`).
- `main.py` diffs the new fetch against the last snapshot and alerts on:
  - **quantity decreased** → 📚 a copy sold
  - **quantity increased** → 📦 restocked
  - **new store appears** in the table → 🏬 newly listed (skipped on the very
    first-ever run, since there's no baseline yet to compare against)
  - **store disappears** from the table → ⚠️ check-the-page warning, kept
    separate from a sale since it more likely means a scrape/page issue

## Adding more subscribers

`TELEGRAM_CHAT_ID` accepts a comma-separated list, so anyone can subscribe to alerts:

1. They message the bot (search its @username on Telegram, or share the
   `t.me/<botname>` link from BotFather) with anything, e.g. `Hola`.
2. Open `https://api.telegram.org/bot<TOKEN>/getUpdates` and read their
   `message.chat.id` from the latest entry.
3. Update the `TELEGRAM_CHAT_ID` secret to include both ids, comma-separated
   (e.g. `1694018511,987654321`): `gh secret set TELEGRAM_CHAT_ID`.

If sending to one chat id fails (e.g. someone blocked the bot), the others
still get their alert — failures are collected and reported together, not
short-circuited.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

All external calls (the page fetch and the Telegram API) are mocked — tests
never hit the real site or send real Telegram messages.

## Known unknown

All 23 stores currently show a quantity of only 2 or 3. It's not yet confirmed
whether this is the true live count or a capped "critical stock" display —
watch `data/history.csv` over the first few days to see if values ever exceed 3.

## Note on scope

Only tracks a single hardcoded book (`scraper.py: TARGET_URL`). Not designed for
multiple titles — that would need config restructuring if it comes up later.
