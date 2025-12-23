import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

DB_FILE = Path("journal.json")
DB_FILE.touch(exist_ok=True)


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


def load_entries():
    """Load journal entries from the JSON file."""
    with open(DB_FILE, mode="r") as read_file:
        try:
            journal_entries = json.load(read_file)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            journal_entries = []
    return journal_entries


def save_entries(entry):
    """Save journal entries to the JSON file."""
    journal_entries = load_entries()
    journal_entries.append(
        {
            "Title": entry.title,
            "Content": entry.content,
            "Date": entry.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    with open(DB_FILE, mode="w", encoding="utf-8") as write_file:
        json.dump(journal_entries, write_file)


def add_entry(title, content):
    """Create a new journal entry and save it to the JSON file."""
    # timestamp = datetime.datetime.now()
    new_journal_entry = JournalEntry(title, content)  # , timestamp)
    save_entries(new_journal_entry)


def list_entries(entries):
    """Print all journal entries to the console."""
    for count, entry in enumerate(entries, start=1):
        print(f"{count}. {entry['Title']}  ({entry['Date']})")
        print(f"{entry['Content']}\n")


if __name__ == "__main__":
    # quick interactive program (entry point) to validate the above
    title = input("Title: ")
    content = input("Content: ")
    add_entry(title, content)
    print("✅ Entry saved.")
    print("\n📘 Your Journal:")
    list_entries(load_entries())
