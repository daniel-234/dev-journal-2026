from pathlib import Path

import pytest
from typer.testing import CliRunner

from journal.cli import MAX_ITEMS, add, app
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


def test_edit_no_entries(db):
    entries = db.load_entries()
    result = runner.invoke(app, ["edit", "1", "--file", str(TEST_DB_FILE)])
    assert len(entries) == 0
    assert result.exit_code == 0
    assert "No entry was found with this ID" in result.stdout


def test_edit(db):
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


def test_delete_no_entries(db):
    entries = db.load_entries()
    result = runner.invoke(app, ["delete", "5", "--file", str(TEST_DB_FILE)])
    assert len(entries) == 0
    assert result.exit_code == 0
    assert "No entry was found with this ID" in result.stdout


def test_delete(db):
    add("TODO", "Study pytest", "Python, testing", TEST_DB_FILE)
    result = runner.invoke(app, ["delete", "00001", "--file", str(TEST_DB_FILE)])
    assert "\u2702 \u27a1 \u274e  Entry removed." in result.stdout


def test_search_no_match(db):
    query = "Java"
    add("TODO", "Study pytest", "Python, testing", TEST_DB_FILE)
    add("Database", "Exercised with SQL", "database, SQL, query", TEST_DB_FILE)
    result = runner.invoke(app, ["search", "Java", "--file", str(TEST_DB_FILE)])
    assert f"No match for {query} in journal." in result.stdout


def test_search_titles_only_no_match(db):
    query = "Python"
    add("TODO", "Study pytest", "Python, testing", TEST_DB_FILE)
    add("Database", "Exercised with SQL", "database, SQL, query", TEST_DB_FILE)
    result = runner.invoke(
        app, ["search", "--titles-only", query, "--file", str(TEST_DB_FILE)]
    )
    assert (
        f"No match for {query} with option --titles-only in journal." in result.stdout
    )


def test_stats(db):
    add("TODO", "Study pytest", "Python, testing", TEST_DB_FILE)
    add("Database", "Exercised with SQL", "database, SQL, query", TEST_DB_FILE)
    add("Rust", "Learn new language", "object-oriented, performance", TEST_DB_FILE)
    add("Exercise", "Complete a Pybite", "Python, exercise", TEST_DB_FILE)
    result = runner.invoke(app, ["stats", "--file", str(TEST_DB_FILE)])
    assert "\nNumber of entries: 4" in result.stdout


def test_populate_max_items(db):
    num_items = MAX_ITEMS + 1
    result = runner.invoke(
        app, ["populate", str(num_items), "--file", str(TEST_DB_FILE)]
    )
    assert (
        f"Please, choose a number of items not greater than {MAX_ITEMS}."
        in result.stdout
    )


def test_populate(db):
    result = runner.invoke(app, ["populate", "20", "--file", str(TEST_DB_FILE)])
    assert "\u2705 Journal populated with 20 new entries." in result.stdout
