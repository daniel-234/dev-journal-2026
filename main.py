import json
import random
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import typer
from faker import Faker

DB_FILE = Path("journal.json")
DB_FILE.touch(exist_ok=True)

TITLE_LENGTH = 30
CONTENT_LENGTH = 70
MAX_ID = 99999

app = typer.Typer()


class TitleTooLongException(Exception):
    """Title longer than TITLE_LENGTH characters"""


class ContentTooLongException(Exception):
    """Content longer than CONTENT_LENGTH characters"""


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
            raise TitleTooLongException(
                "Title must not exceed TITLE_LENGTH charatcers."
            )
        if len(self.content) > CONTENT_LENGTH:
            raise ContentTooLongException(
                "Content must not exceed CONTENT_LENGTH characters."
            )

    @classmethod
    def create(cls, title: str, content: str):
        existing_entries = load_entries()
        if any(entry.title.lower() == title.lower() for entry in existing_entries):
            raise EntryAlreadyExists
        entry_id = next_entry_id(existing_entries)
        return cls(id=entry_id, title=title, content=content)


def next_entry_id(existing_entries: list[JournalEntry]) -> str:
    """ "
    Add human-friendly, unique and ordered IDs to each entry with no more than 5 digits

    Args:
        existing_entries: list[JournalEntry]: a list of the existing entries.

    Returns:
        str: A unique ID with 5 digits, 0 padded and right aligned, increased
             by 1 regarding to the maximum ID already created.
    """
    if not existing_entries:
        return "00001"

    max_id = max(int(entry.id) for entry in existing_entries)
    if max_id >= MAX_ID:
        raise MaximumNumberOfEntries(
            "You have already reached the maximum number of entries. Please, delete one before adding this new entry."
        )
    return f"{max_id + 1:05d}"


def save_entries(entries: list[JournalEntry]) -> None:
    """
    Save entries to the JSON file.

    Args:
        entries (list[JournalEntry]): A list of entries.

    Returns:
        None
    """
    with open(DB_FILE, mode="w", encoding="utf-8") as write_file:
        # Convert each "entry" object to a dictionary to be serializable
        journal_entries = [asdict(entry) for entry in entries]
        json.dump(journal_entries, write_file, indent=4)


def load_entries() -> list[JournalEntry]:
    """
    Load journal entries from the JSON file.

    Args:
        None

    Returns:
        list[JournalEntry]: a list of JournalEntry objects.

    Raises:
        JSONDecodeError: If the data being deserialized is not valid JSON.
        FileNotFoundError: If a JSON file has not yet been created.
    """
    with open(DB_FILE, mode="r") as read_file:
        try:
            # Load the entries from the Dev Journal as a list of JournalEntry objects
            journal_entries = [JournalEntry(**entry) for entry in json.load(read_file)]
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            # Create an empty list if the journal is still empty
            journal_entries = []
    return journal_entries


@app.command()
def add_entry() -> None:
    """
    Create a new journal entry and save it to the JSON file, at the beginning of the list.

    Args:
        title (str): The title of the entry to add.
        content (str): The content of the entry to add.

    Returns:
        None

    Raises:
        TypeError: If at least one argument is missing.
    """
    title = input("Title: ")
    if not title:
        raise ValueError("Please, insert a title for the entry.")
    content = input("Content: ")
    if not content:
        raise ValueError("Please, intert some content for this entry.")
    tags = input("Tags (comma separated):  ")
    tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
    try:
        new_journal_entry = JournalEntry.create(title, content)
        new_journal_entry.timestamp = new_journal_entry.timestamp.isoformat(
            timespec="seconds"
        )
        new_journal_entry.tags = tags
        print("\u2705 Entry saved.")
    except TypeError:
        print("Please, insert a title and the content in your journal entry.")

    # Load the JSON content as a list of dictionaries
    journal_entries = load_entries()
    # Add the new entry to the beginning of the list, to preserve its cronological order
    journal_entries = [new_journal_entry] + journal_entries
    save_entries(journal_entries)


@app.command()
def list_entries() -> None:
    """
    Print all journal entries to the console.

    Args:
        None

    Returns:
        None
    """
    # Load entries
    entries = load_entries()
    # Print a message to the user to let know there's no entry yet
    if not entries:
        print("No entries yet in Dev Journal.")
    for entry in entries:
        print("\n")
        print("-" * 70)
        print(f"ID {entry.id}:  {entry.title.upper()} - ({entry.timestamp})")
        print("-" * 70)
        print(f"{entry.content}")
        print("-" * 70)
        print(f"tags: {entry.tags}\n")


@app.command()
def edit_entry() -> None | str:
    """
    Edit an entry content given its ID.

    Args:
        None

    Returns:
        None | str: If the ID is not found in the journal, print a message
                    to the user; otherwise don't return anything.
    """
    entry_id = input("Type the ID of the entry you want to edit: ")
    if not entry_id:
        raise ValueError("No ID typed.")
    # Load the entries from the dev journal, if any.
    journal_entries = load_entries()
    # Iterate through the dictionaries in the journal_entries list.
    # Check if the ID passed by the user is found in an entry value.
    if not any(entry_id in entry.id for entry in journal_entries):
        # If there is no entry with this ID, print a message to the screen.
        print("No entry was found with this ID")
    else:
        # Check each entry dictionary in the list.
        for entry in journal_entries:
            # If the ID of the current entry is the same as the one
            # typed by the user, ask the user for the content to update this entry.
            if entry.id == entry_id:
                new_content = input(
                    f"Insert the new content for the entry {entry.title}:  "
                )
                entry.content = new_content
                print("\u2705 New content saved:  ")
                print(f"{new_content}")
        save_entries(journal_entries)


@app.command()
def delete_entry() -> None | str:
    """
    Delete an entry given its ID.

    Args:
        None

    Returns:
        None | str: If the ID is not in the journal, print a message
                    to inform the user; don't return anything otherwise.
    """
    entry_id = input("Type the ID of the entry you want to delete: ")
    if not entry_id:
        raise ValueError("No ID typed.")
    # Load the entries from the dev journal, if any.
    journal_entries = load_entries()
    # Iterate through the dictionaries in the journal_entries list.
    # Check if the ID passed by the user is found in an entry value.
    if not any(entry_id in entry.id for entry in journal_entries):
        # If there is no entry with this ID, print a message to the screen.
        print("No entry was found with this ID.")
    else:
        # Check each entry dictionary in the list.
        for entry in journal_entries:
            # If the ID of the current entry is the same as the one
            # typed by the user, delete this entry from the list.
            if entry.id == entry_id:
                journal_entries.remove(entry)
                print("\u2702 \u27a1 \u274e  Entry removed.")
        save_entries(journal_entries)


@app.command()
def search(query: str) -> list[JournalEntry]:
    """
    Search for string matching in entry titles, content and tags

    Args:
        query (str): The string you have to search

    Returns:
        list[JournalEntry]: The list of matching entries
    """
    journal_entries = load_entries()
    title_results = [
        entry for entry in journal_entries if query.lower() in entry.title.lower()
    ]
    content_results = [
        entry
        for entry in journal_entries
        if query.lower() in entry.content.lower() and entry not in title_results
    ]
    tags_results = [
        entry
        for entry in journal_entries
        if any(query.lower() in tag.lower() for tag in entry.tags)
        and entry not in content_results
    ]
    search_results = title_results + content_results + tags_results
    for entry in search_results:
        print("\n")
        print("-" * 70)
        print(f"ID {entry.id}:  {entry.title.upper()} - ({entry.timestamp})")
        print("-" * 70)
        print(f"{entry.content}")
        print("-" * 70)
        print(f"tags: {entry.tags}\n")


@app.command()
def populate_journal() -> None:
    """
    Populate the journal with fake content.

    Args:
        None

    Returns:
        None
    """
    random_num = random.randint(0, 20)
    fake = Faker()
    Faker.seed()
    journal_entries = load_entries()
    # Get 5 new entries, randomly, from Faker
    for _ in range(random_num, random_num + 5):
        new_title = fake.company()
        tags = fake.bs()
        if not any(new_title in entry.title for entry in journal_entries):
            new_journal_entry = JournalEntry.create(fake.company(), fake.catch_phrase())
            new_journal_entry.timestamp = new_journal_entry.timestamp.isoformat(
                timespec="seconds"
            )
            tags = [tag.strip() for tag in tags.split(" ") if tag.strip()]
            new_journal_entry.tags = tags
            journal_entries = [new_journal_entry] + journal_entries
        save_entries(journal_entries)
    print("\u2705 Journal populated.")


if __name__ == "__main__":
    app()
