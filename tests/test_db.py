from pathlib import Path

import pytest
from typer.testing import CliRunner

from journal.cli import add, app
from journal.db import JournalDatabase

# Instantiate a Path object with a JSON file used only for testing
TEST_DB_FILE = Path("test_journal.json")

runner = CliRunner()


@pytest.fixture(scope="function")
def db():
    # Instantiate a Database object
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


def test_edit_no_entry(db):
    entries = db.load_entries()
    result = runner.invoke(app, ["edit", "1", "--file", str(TEST_DB_FILE)])
    assert len(entries) == 0
    assert result.exit_code == 0
    assert "No entry was found with this ID" in result.stdout


def test_edit_entry(db):
    add("TODO", "Study pytest", "Python, testing", TEST_DB_FILE)
    result = runner.invoke(
        app,
        ["edit", "00001", "--file", str(TEST_DB_FILE)],
        input="Applying tests with Pytest\n",
    )
    assert (
        "Insert the new content for the entry TODO:  \u2705 New content saved:  \nApplying tests with Pytest\n"
        in result.output
    )
