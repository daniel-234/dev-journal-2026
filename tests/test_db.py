from journal.db import load_entries


def test_load_entries():
    entries = load_entries()
    assert entries == []
