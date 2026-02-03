from dataclasses import dataclass, field
from datetime import datetime, timezone

import typer

TITLE_LENGTH = 30
CONTENT_LENGTH = 70
MAX_ID = 99999
FIRST_ID = "1"


class EntryAlreadyExists(Exception):
    """An entry with this title already exists"""


class MaximumNumberOfEntries(Exception):
    """Maximum number of journal entries reached"""


# 📝 Define a JournalEntry class with title, content, and date
@dataclass
class JournalEntry:
    """
    Represents an entry to the journal.
    """

    id: str
    title: str
    content: str
    # The 'field' function allows more control over a field definition.
    # The 'default_factory' parameter accepts a function that returns an initial value
    # that needs to be computed dynamically, such as a timestamp.
    # Use an anonymous inline lambda function to compute the timestamp.
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    # Add support for tags in entries
    tags: list[str] = field(default_factory=list)

    # Check if title or content length are too long at construction
    def __post_init__(self):
        if len(self.title) > TITLE_LENGTH:
            self.title = self.title[:TITLE_LENGTH]

        if len(self.content) > CONTENT_LENGTH:
            self.content = self.content[:CONTENT_LENGTH]

    @classmethod
    def create(
        cls, title: str, content: str, existing_entries: list["JournalEntry"]
    ) -> "JournalEntry":
        if any(entry.title.lower() == title.lower() for entry in existing_entries):
            print("An entry with this title already exists.")
            raise typer.Exit()
        entry_id = next_entry_id(existing_entries)
        return cls(id=entry_id, title=title, content=content)

    @property
    def formatted_timestamp(self) -> str:
        return datetime.fromisoformat(self.timestamp).strftime("%Y-%m-%d %H:%M:%S")


def next_entry_id(existing_entries: list[JournalEntry]) -> str:
    """
    Add human-friendly, unique and ordered IDs to each entry with no more than 5 digits
    """

    if not existing_entries:
        return FIRST_ID

    max_id = max(int(entry.id) for entry in existing_entries)
    if max_id >= MAX_ID:
        raise MaximumNumberOfEntries(
            "You have already reached the maximum number of entries. Please, delete one before adding this new entry."
        )
    return f"{max_id + 1}"
