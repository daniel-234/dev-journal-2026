import json
from dataclasses import dataclass
from pathlib import Path

DB_FILE = Path("journal.json")
DB_FILE.touch(exist_ok=True)


# 📝 Define a JournalEntry class with title, content, and date
@dataclass
class JournalEntry:
    title: str
    content: str
    # date: str


def load_entries():
    """Load journal entries from the JSON file."""
    with open(DB_FILE, mode="r") as read_file:
        try:
            entries = json.load(read_file)
        except json.decoder.JSONDecodeError:
            entries = {}
    return entries
    # print(f'Title: {entry["title"]}')


def save_entries(entries):
    """Save journal entries to the JSON file."""
    journal_entries = load_entries()
    for entry in entries:
        journal_entries.update(entry)
    with open(DB_FILE, mode="w", encoding="utf-8") as write_file:
        json.dump(journal_entries, write_file)


def add_entry(title, content):
    """Create a new journal entry and save it to the JSON file."""

    # TODO
    """
    new_journal_entry = JournalEntry(title, content)
    entries = load_entries()
    entries.update(vars(new_journal_entry))
    print(entries)
    save_entries(entries)
    """
    pass


def list_entries(entries):
    """Print all journal entries to the console."""
    pass


if __name__ == "__main__":
    # quick interactive program (entry point) to validate the above
    title = input("Title: ")
    content = input("Content: ")
    # add_entry(title, content)
    print("✅ Entry saved.")
    print("\n📘 Your Journal:")
    # list_entries(load_entries())

    # Hardcode values to test the 'save_entries' and 'load_entries' functions
    save_entries([{"c": "d"}, {"e": "f"}])
    print(load_entries())
