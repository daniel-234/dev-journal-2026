import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import typer
from faker import Faker

DB_FILE = Path("journal.json")
DB_FILE.touch(exist_ok=True)

app = typer.Typer()


# Define a custom exception to handle char limit on title
class TitleTooLongException(Exception):
    """Title longer than 20 characters"""


# Define a custom exception to handle char limit on content
class ContentTooLongException(Exception):
    """Content longer than 50 characters"""


# 📝 Define a JournalEntry class with title, content, and date
@dataclass
class JournalEntry:
    title: str
    content: str
    # The 'field' function allows more control over a field definition.
    # The 'default_factory' parameter accepts a function that returns an initial value
    # that needs to be computed dynamically, such as a timestamp.
    # Use an anonymous inline lambda function to compute the timestamp.
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Check if title or content length are too long at construction
    def __post_init__(self):
        if len(self.title) > 30:
            raise TitleTooLongException("Title must not exceed 30 charatcers.")
        if len(self.content) > 70:
            raise ContentTooLongException("Content must not exceed 70 characters.")


JournalEntries = list[dict]


def journalEntryToJSON(entry: JournalEntry) -> dict:
    """Convert a JournalEntry object to JSON"""
    return {
        "Title": entry.title,
        "Content": entry.content,
        "Date": entry.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
    }


def load_entries() -> JournalEntries:
    """Load journal entries from the JSON file."""
    with open(DB_FILE, mode="r") as read_file:
        try:
            # Load the entries from the Dev Journal
            journal_entries = json.load(read_file)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            # Create an empty list if the journal is still empty
            journal_entries = []
    return journal_entries


def save_entries(entry: JournalEntry) -> None:
    """Save journal entries to the JSON file."""
    # Load the JSON content as a list of dictionaries
    journal_entries = load_entries()
    # Append the entry object to the list, after converting
    # it to a dictionary
    journal_entries.append(journalEntryToJSON(entry))
    with open(DB_FILE, mode="w", encoding="utf-8") as write_file:
        json.dump(journal_entries, write_file)


@app.command()
def add_entry(title: str, content: str) -> None:
    """Create a new journal entry and save it to the JSON file."""
    try:
        new_journal_entry = JournalEntry(title, content)
    except TypeError:
        if not title or content:
            raise ValueError("Please, intert a title and the content.")
    save_entries(new_journal_entry)


@app.command()
def list_entries() -> None:
    """Print all journal entries to the console."""
    # Load entries
    entries = load_entries()
    # Print a message to the user to let know there's no entry yet
    if entries == []:
        print("No entries yet in Dev Journal.")
    for count, entry in enumerate(entries, start=1):
        print(f"{count}. {entry.get("Title")}  ({entry.get("Date")})")
        print(f"{entry.get("Content")}\n")


@app.command()
def edit_entry(title: str, new_content: str) -> None | str:
    """Edit an entry content given its title. If title is not found,
    print a message to the user."""
    # Load the entries from the dev journal, if any.
    journal_entries = load_entries()
    # Iterate through the dictionaries in the journal_entries list.
    # Check if the title passed by the user is found in an entry value.
    if not any(title in entry.get("Title") for entry in journal_entries):
        # If title is not part of an entry, print a message to the screen.
        print("No entry was found with this title")
    else:
        # Check each entry dictionary in the list.
        for entry in journal_entries:
            # If the title of the current entry is the same as the one
            # typed by the user, update the content of this entry.
            if entry["Title"] == title:
                entry["Content"] = new_content
        # Open the JSON file and save the updated content.
        with open(DB_FILE, mode="w", encoding="utf-8") as write_file:
            json.dump(journal_entries, write_file)


@app.command()
def populate_journal() -> None:
    fake = Faker()
    Faker.seed(0)
    for _ in range(5):
        add_entry(fake.company(), fake.catch_phrase())


if __name__ == "__main__":
    app()
