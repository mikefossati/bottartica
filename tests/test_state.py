import state as state_module
from state import append_history, load_last_state, save_state


def test_load_last_state_returns_empty_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(state_module, "STATE_PATH", tmp_path / "missing.json")
    assert load_last_state() == {}


def test_save_and_load_state_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(state_module, "STATE_PATH", tmp_path / "last_state.json")
    save_state({"Alto Las Condes": 3, "Bodega Internet": 2})
    assert load_last_state() == {"Alto Las Condes": 3, "Bodega Internet": 2}


def test_save_state_creates_parent_directory(tmp_path, monkeypatch):
    nested_path = tmp_path / "nested" / "last_state.json"
    monkeypatch.setattr(state_module, "STATE_PATH", nested_path)
    save_state({"A": 1})
    assert nested_path.exists()


def test_append_history_writes_header_once_then_appends_rows(tmp_path, monkeypatch):
    history_path = tmp_path / "history.csv"
    monkeypatch.setattr(state_module, "HISTORY_PATH", history_path)

    append_history({"A": 3}, fetched_at="2026-01-01T00:00:00+00:00")
    append_history({"A": 2, "B": 1}, fetched_at="2026-01-01T01:00:00+00:00")

    lines = history_path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "fetched_at,store,quantity"
    assert lines[1] == "2026-01-01T00:00:00+00:00,A,3"
    assert lines[2] == "2026-01-01T01:00:00+00:00,A,2"
    assert lines[3] == "2026-01-01T01:00:00+00:00,B,1"
    assert len(lines) == 4
