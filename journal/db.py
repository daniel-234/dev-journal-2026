import json
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path

from journal.models import JournalEntry


class JournalDatabase:
    def __init__(self, db_file: Path):
        self.db_file = db_file
        self.db_file.touch()

    def save(self, entries: list[JournalEntry]) -> None:
        """
        Save entries to the JSON file.
        """

        with open(self.db_file, mode="w", encoding="utf-8") as write_file:
            # Convert each "entry" object to a dictionary to be serializable
            journal_entries = [asdict(entry) for entry in entries]
            json.dump(journal_entries, write_file, indent=4)

    def load_entries(self) -> list[JournalEntry]:
        """
        Load journal entries from the JSON file.
        """

        with open(self.db_file, mode="r") as read_file:
            try:
                # Load the entries from the Dev Journal as a list of JournalEntry objects
                journal_entries = [
                    JournalEntry(**entry) for entry in json.load(read_file)
                ]
            except (json.decoder.JSONDecodeError, FileNotFoundError):
                # Create an empty list if the journal is still empty
                journal_entries = []
        return journal_entries

    @contextmanager
    def session(self):
        """
        Abstract loading and saving into a context manager.
        """
        journal_entries = self.load_entries()
        yield journal_entries
        self.save(journal_entries)
