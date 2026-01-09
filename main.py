import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import typer
from faker import Faker

DB_FILE = Path("journal.json")
DB_FILE.touch(exist_ok=True)

TITLE_LENGTH = 30
CONTENT_LENGTH = 70

app = typer.Typer()


class TitleTooLongException(Exception):
    """Title longer than TITLE_LENGTH characters"""


class ContentTooLongException(Exception):
    """Content longer than CONTENT_LENGTH characters"""


# 📝 Define a JournalEntry class with title, content, and date
@dataclass
class JournalEntry:
    """
    Represents an entry to the journal.
    """

    title: str
    content: str
    # The 'field' function allows more control over a field definition.
    # The 'default_factory' parameter accepts a function that returns an initial value
    # that needs to be computed dynamically, such as a timestamp.
    # Use an anonymous inline lambda function to compute the timestamp.
    timestamp: datetime = field(
        default_factory=lambda: f"{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}"
    )

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


def save_entries(entries: list[JournalEntry]) -> None:
    """
    Save entries to the JSON file.

    Args:
        entries (JournalEntries): A list of entries

    Returns:
        None
    """
    with open(DB_FILE, mode="w", encoding="utf-8") as write_file:
        # Convert each "entry" object to a dictionary to be serializable
        journal_entries = [asdict(entry) for entry in entries]
        json.dump(journal_entries, write_file)


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
def add_entry(title: str, content: str) -> None:
    """
    Create a new journal entry and save it to the JSON file.

    Args:
        title (str): The title of the entry to add.
        content (str): The content of the entry to add.

    Returns:
        None

    Raises:
        TypeError: If at least one argument is missing.
    """
    if not title or not content:
        raise ValueError("Please, intert a title and the content.")
    try:
        new_journal_entry = JournalEntry(title, content)
    except TypeError:
        print("Please, insert a title and the content in your journal entry.")
    # Load the JSON content as a list of dictionaries
    journal_entries = load_entries()
    # Append the entry object to the list, after converting it to a dictionary
    journal_entries.append(new_journal_entry)
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
    for count, entry in enumerate(entries, start=1):
        print(f"{count}. {entry.title}  ({entry.timestamp})")
        print(f"{entry.content}\n")


@app.command()
def edit_entry(title: str, new_content: str) -> None | str:
    """
    Edit an entry content given its title.

    Args:
        title (str): The title of the entry the user wants to edit.
        new_content (str): The content to edit.

    Returns:
        None | str: If title is not found in the journal, print a message
                    to the user; otherwise don't return anything.
    """
    # Load the entries from the dev journal, if any.
    journal_entries = load_entries()
    # Iterate through the dictionaries in the journal_entries list.
    # Check if the title passed by the user is found in an entry value.
    if not any(title in entry.title for entry in journal_entries):
        # If title is not part of an entry, print a message to the screen.
        print("No entry was found with this title")
    else:
        # Check each entry dictionary in the list.
        for entry in journal_entries:
            # If the title of the current entry is the same as the one
            # typed by the user, update the content of this entry.
            if entry.title == title:
                entry.content = new_content
        save_entries(journal_entries)


@app.command()
def delete_entry(title: str) -> None | str:
    """
    Delete an entry given its title.

    Args:
        title (str): The title of the entry to delete.

    Returns:
        None | str: If title is not in the journal, print a message
                    to inform the user; don't return anything otherwise.
    """
    # Load the entries from the dev journal, if any.
    journal_entries = load_entries()
    # Iterate through the dictionaries in the journal_entries list.
    # Check if the title passed by the user is found in an entry value.
    if not any(title in entry.title for entry in journal_entries):
        # If title is not part of an entry, print a message to the screen.
        print("No entry was found with this title")
    else:
        # Check each entry dictionary in the list.
        for entry in journal_entries:
            # If the title of the current entry is the same as the one
            # typed by the user, delete this entry from the list.
            if entry.title == title:
                journal_entries.remove(entry)
        save_entries(journal_entries)


@app.command()
def populate_journal() -> None:
    """
    Populate the journal with fake content.

    Args:
        None

    Returns:
        None
    """
    fake = Faker()
    Faker.seed(0)
    for _ in range(5):
        add_entry(fake.company(), fake.catch_phrase())


if __name__ == "__main__":
    app()
