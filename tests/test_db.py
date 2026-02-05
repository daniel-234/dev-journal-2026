from pathlib import Path

import pytest

from journal.cli import add
from journal.db import JournalDatabase

# Instantiate a Path object with a JSON file used only for testing
TEST_DB_FILE = Path("test_journal.json")


@pytest.fixture(scope="function")
def db():
    db = JournalDatabase(TEST_DB_FILE)
    yield db
    db.save([])


def test_empty_journal(db):
    entries = db.load_entries()
    assert entries == []


def test_add_entry(db):
    add("TODO", "Study pytest", "Python, testing", TEST_DB_FILE)
    entries = db.load_entries()
    assert len(entries) == 1
    entry = entries[0]
    assert entry.title == "TODO"
    assert entry.content == "Study pytest"
    assert entry.tags == ["Python", "testing"]
