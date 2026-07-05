from unittest.mock import Mock, patch

import pytest

from notify import NotifyError, send


def test_send_posts_to_telegram_api_for_single_chat(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "111")
    mock_resp = Mock(status_code=200)

    with patch("notify.requests.post", return_value=mock_resp) as mock_post:
        send("hello")

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://api.telegram.org/bottok/sendMessage"
    assert kwargs["json"] == {"chat_id": "111", "text": "hello"}


def test_send_broadcasts_to_every_chat_id(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "111, 222")
    mock_resp = Mock(status_code=200)

    with patch("notify.requests.post", return_value=mock_resp) as mock_post:
        send("hello")

    assert mock_post.call_count == 2
    sent_to = {call.kwargs["json"]["chat_id"] for call in mock_post.call_args_list}
    assert sent_to == {"111", "222"}


def test_send_raises_when_credentials_missing(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

    with pytest.raises(NotifyError):
        send("hello")


def test_send_attempts_all_chat_ids_even_if_one_fails(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "111,222")
    responses = [Mock(status_code=403, text="Forbidden"), Mock(status_code=200)]

    with patch("notify.requests.post", side_effect=responses) as mock_post:
        with pytest.raises(NotifyError) as exc_info:
            send("hello")

    assert mock_post.call_count == 2  # second chat id still attempted
    assert "111" in str(exc_info.value)
