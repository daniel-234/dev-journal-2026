import datetime
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
    timestamp: str


def load_entries():
    """Load journal entries from the JSON file."""
    with open(DB_FILE, mode="r") as read_file:
        try:
            journal_entries = json.load(read_file)
        except json.decoder.JSONDecodeError:
            journal_entries = {"entries": []}
    return journal_entries


def save_entries(entry):
    """Save journal entries to the JSON file."""
    journal_entries = load_entries()
    print("jjj", journal_entries)
    journal_entries["entries"].append(
        {"Title": entry.title, "Content": entry.content, "Date": entry.timestamp}
    )
    with open(DB_FILE, mode="w", encoding="utf-8") as write_file:
        json.dump(journal_entries, write_file)


def add_entry(title, content):
    """Create a new journal entry and save it to the JSON file."""
    dt = datetime.datetime.now()
    timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
    new_journal_entry = JournalEntry(title, content, timestamp)
    save_entries(new_journal_entry)


def list_entries(entries):
    """Print all journal entries to the console."""
    count = 1
    for entry in entries["entries"]:
        print(f"{count}. {entry['Title']}  ({entry['Date']})")
        print(f"{entry['Content']}\n")
        count += 1


if __name__ == "__main__":
    # quick interactive program (entry point) to validate the above
    title = input("Title: ")
    content = input("Content: ")
    add_entry(title, content)
    print("✅ Entry saved.")
    print("\n📘 Your Journal:")
    list_entries(load_entries())
