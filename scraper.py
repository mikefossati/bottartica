"""Fetch and parse the Antártica product page's per-store stock table."""
import requests
from bs4 import BeautifulSoup

USER_AGENT = "book-stock-watcher/1.0 (personal inventory monitor)"
TARGET_URL = "https://www.antartica.cl/el-cuerpo-quieto-9789560839503.html"


class FetchError(Exception):
    pass


def parse_stock(html: str) -> dict[str, int]:
    soup = BeautifulSoup(html, "lxml")
    rows = soup.select("table.tiendas_stocks tbody tr")
    stock: dict[str, int] = {}
    for row in rows:
        name_cell = row.select_one("td.tiendas_stocks_nombre")
        qty_cell = row.select_one("td.tiendas_stocks_cantidad")
        if name_cell is None or qty_cell is None:
            continue
        name = name_cell.get_text(strip=True)
        qty_text = qty_cell.get_text(strip=True)
        digits = "".join(c for c in qty_text if c.isdigit())
        if not name or not digits:
            continue
        stock[name] = int(digits)

    if not stock:
        raise FetchError("Parsed 0 stores — page structure may have changed")

    return stock


def fetch_stock(url: str = TARGET_URL) -> dict[str, int]:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
    if resp.status_code != 200:
        raise FetchError(f"HTTP {resp.status_code} fetching {url}")
    return parse_stock(resp.text)
