import json
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path

from journal.models import JournalEntry

DB_FILE = Path("journal.json")
DB_FILE.touch(exist_ok=True)


def save(entries: list[JournalEntry]) -> None:
    """
    Save entries to the JSON file.
    """

    with open(DB_FILE, mode="w", encoding="utf-8") as write_file:
        # Convert each "entry" object to a dictionary to be serializable
        journal_entries = [asdict(entry) for entry in entries]
        json.dump(journal_entries, write_file, indent=4)


def load_entries() -> list[JournalEntry]:
    """
    Load journal entries from the JSON file.
    """

    with open(DB_FILE, mode="r") as read_file:
        try:
            # Load the entries from the Dev Journal as a list of JournalEntry objects
            journal_entries = [JournalEntry(**entry) for entry in json.load(read_file)]
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            # Create an empty list if the journal is still empty
            journal_entries = []
    return journal_entries


@contextmanager
def journal_repo():
    """
    Abstract loading and saving into a context manager.
    """
    journal_entries = load_entries()
    yield journal_entries
    save(journal_entries)
