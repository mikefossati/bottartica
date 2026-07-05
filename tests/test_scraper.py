from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from scraper import FetchError, fetch_stock, parse_stock

FIXTURE_HTML = (Path(__file__).parent / "fixtures" / "sample_page.html").read_text(encoding="utf-8")


def test_parse_stock_extracts_store_quantities():
    assert parse_stock(FIXTURE_HTML) == {"Bodega Internet": 2, "Alto Las Condes": 3}


def test_parse_stock_raises_when_table_missing():
    with pytest.raises(FetchError):
        parse_stock("<html><body>no stock table here</body></html>")


def test_fetch_stock_parses_response_body():
    mock_resp = Mock(status_code=200, text=FIXTURE_HTML)
    with patch("scraper.requests.get", return_value=mock_resp) as mock_get:
        stock = fetch_stock("https://example.com/book.html")

    assert stock == {"Bodega Internet": 2, "Alto Las Condes": 3}
    mock_get.assert_called_once()
    _, kwargs = mock_get.call_args
    assert kwargs["headers"]["User-Agent"]
    assert kwargs["timeout"] == 20


def test_fetch_stock_raises_on_non_200():
    mock_resp = Mock(status_code=503, text="Service Unavailable")
    with patch("scraper.requests.get", return_value=mock_resp):
        with pytest.raises(FetchError):
            fetch_stock("https://example.com/book.html")
