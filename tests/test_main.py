from unittest.mock import patch

from main import diff_and_alert, main
from notify import NotifyError
from scraper import FetchError


def test_cold_start_produces_no_alerts():
    assert diff_and_alert({}, {"A": 3, "B": 2}) == []


def test_decrease_triggers_sale_alert_singular():
    assert diff_and_alert({"A": 3}, {"A": 2}) == ["📚 Se vendió 1 libro en A (3 → 2)"]


def test_decrease_triggers_sale_alert_plural():
    assert diff_and_alert({"A": 5}, {"A": 2}) == ["📚 Se vendió 3 libros en A (5 → 2)"]


def test_increase_triggers_restock_alert():
    assert diff_and_alert({"A": 1}, {"A": 3}) == ["📦 Se repuso stock en A: +2 libros (1 → 3)"]


def test_new_store_triggers_alert_outside_cold_start():
    assert diff_and_alert({"A": 1}, {"A": 1, "B": 2}) == ["🏬 Nueva tienda con stock: B (2 libros)"]


def test_vanished_store_triggers_warning_not_sale():
    assert diff_and_alert({"A": 1, "B": 2}, {"A": 1}) == ["⚠️ B ya no aparece en la página — revisar"]


def test_unchanged_store_produces_no_alert():
    assert diff_and_alert({"A": 2}, {"A": 2}) == []


def test_main_happy_path_sends_alert_and_persists():
    with patch("main.fetch_stock", return_value={"A": 2}) as mock_fetch, \
         patch("main.load_last_state", return_value={"A": 3}), \
         patch("main.save_state") as mock_save, \
         patch("main.append_history") as mock_history, \
         patch("main.send") as mock_send:
        rc = main()

    assert rc == 0
    mock_fetch.assert_called_once()
    mock_send.assert_called_once_with("📚 Se vendió 1 libro en A (3 → 2)")
    mock_save.assert_called_once_with({"A": 2})
    mock_history.assert_called_once_with({"A": 2})


def test_main_returns_error_code_on_fetch_failure():
    with patch("main.fetch_stock", side_effect=FetchError("boom")), \
         patch("main.load_last_state") as mock_load, \
         patch("main.save_state") as mock_save, \
         patch("main.send") as mock_send:
        rc = main()

    assert rc == 1
    mock_load.assert_not_called()
    mock_save.assert_not_called()
    mock_send.assert_not_called()


def test_main_still_persists_state_when_notify_fails():
    with patch("main.fetch_stock", return_value={"A": 2, "B": 1}), \
         patch("main.load_last_state", return_value={"A": 3, "B": 2}), \
         patch("main.save_state") as mock_save, \
         patch("main.append_history") as mock_history, \
         patch("main.send", side_effect=NotifyError("telegram down")) as mock_send:
        rc = main()

    assert rc == 0  # a notify failure shouldn't fail the whole run
    assert mock_send.call_count == 2  # both alerts still attempted
    mock_save.assert_called_once_with({"A": 2, "B": 1})
    mock_history.assert_called_once_with({"A": 2, "B": 1})
