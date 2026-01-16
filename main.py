import json
import random
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

import typer
from faker import Faker

DB_FILE = Path("journal.json")
DB_FILE.touch(exist_ok=True)

TITLE_LENGTH = 30
CONTENT_LENGTH = 70
MAX_ID = 99999
FIRST_ID = "00001"
MAX_ITEMS = 50

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
            raise EntryAlreadyExists("An entry with this title already exists.")
        entry_id = next_entry_id(existing_entries)
        return cls(id=entry_id, title=title, content=content)


def next_entry_id(existing_entries: list[JournalEntry]) -> str:
    """ "
    Add human-friendly, unique and ordered IDs to each entry with no more than 5 digits
    """

    if not existing_entries:
        return FIRST_ID

    max_id = max(int(entry.id) for entry in existing_entries)
    if max_id >= MAX_ID:
        raise MaximumNumberOfEntries(
            "You have already reached the maximum number of entries. Please, delete one before adding this new entry."
        )
    return f"{max_id + 1:05d}"


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


@app.command()
def add(
    title: Annotated[str, typer.Argument(help="Insert a title for this entry.")],
    content: Annotated[str, typer.Argument(help="Insert a content for this entry.")],
    tags: Annotated[str, typer.Argument(help="Insert tags (comma separated).")],
) -> None:
    """
    Create a new journal entry and save it to the JSON file, at the beginning of the list.
    """

    if not title:
        raise ValueError("Please, insert a title for the entry.")
    if not content:
        raise ValueError("Please, intert some content for this entry.")
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
    save(journal_entries)


@app.command()
def display(
    tags: list[str] = typer.Option(
        default=[], help="Match only entries with any of the given tags"
    ),
) -> None:
    """
    Print all journal entries to the console.
    """

    # Load entries
    entries = load_entries()
    # Print a message to the user to let know there's no entry yet
    if not entries:
        print("No entries yet in Dev Journal.")
    if tags:
        # Match an entry from entries if any given 'query_tag' in the given tags list is a tag to that entry
        entries = [
            entry
            for entry in entries
            if any(
                query_tag.lower() in map(str.lower, entry.tags) for query_tag in tags
            )
        ]
    for entry in entries:
        print("\n")
        print("-" * 70)
        print(f"ID {entry.id}:  {entry.title.upper()} - ({entry.timestamp})")
        print("-" * 70)
        print(f"{entry.content}")
        print("-" * 70)
        print(f"tags: {entry.tags}\n")


@app.command()
def edit(
    entry_id: Annotated[str, typer.Argument(help="Entry ID to edit")],
) -> None | str:
    """
    Edit an entry content given its ID.
    """

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
        save(journal_entries)


@app.command()
def delete(
    entry_id: Annotated[str, typer.Argument(help="Entry ID to delete")],
) -> None | str:
    """
    Delete an entry given its ID.
    """

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
        save(journal_entries)


@app.command()
def search(
    query: str,
    titles_only: bool = typer.Option(
        default=False, help="Limit your search results to tile only"
    ),
) -> list[JournalEntry]:
    """
    Search for string matching in entry titles, content and tags.
    """

    journal_entries = load_entries()
    # If the option "titles_ony" is True, limit the search results to titles
    if titles_only:
        search_results = [
            entry for entry in journal_entries if query.lower() in entry.title.lower()
        ]
    # If the option "titles_only" is False, show results from content and tags, as well
    else:
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
def stats() -> None:
    """
    Show some overall stats: total entries, counts by tag, average content length, most common tag.
    """

    entries = load_entries()
    total = len(entries)
    print(f"\nNumber of entries: {total}")
    print("-" * 50)
    tags = []
    for entry in entries:
        tags = tags + [tag for tag in entry.tags]
    by_tag = Counter(tags).most_common()
    if len(by_tag) > 0:
        print("\nCounts by tag: \n")
    for value, count in by_tag:
        print(value, count)
    if by_tag:
        most_common = [value for value, count in by_tag if count == by_tag[0][1]]
        # As by_tag is not empty, we can get the count of occurrences of the most common item
        # by retrieving the second element of the first item.
        higher_freq = by_tag[0][1]
        contents = [len(value) for value, count in by_tag]
        average_content_length = sum(contents) / len(contents)
        print("*" * 50)
        print(f"\nAverage content length: {round(average_content_length)}")
        print(f"\nMost common tag(s): {most_common} that appears {higher_freq} times.")


@app.command()
def populate(num_items: int) -> None:
    """
    Populate the journal with fake content.
    """

    if num_items > MAX_ITEMS:
        print(f"Please, choose a number of items not greater than {MAX_ITEMS}.")
    else:
        random_num = random.randint(0, 20)
        fake = Faker()
        Faker.seed()
        journal_entries = load_entries()
        # Get num_items new entries, randomly, from Faker
        for _ in range(random_num, random_num + num_items):
            new_title = fake.company()
            tags = fake.bs()
            if not any(new_title in entry.title for entry in journal_entries):
                new_journal_entry = JournalEntry.create(
                    fake.company(), fake.catch_phrase()
                )
                new_journal_entry.timestamp = new_journal_entry.timestamp.isoformat(
                    timespec="seconds"
                )
                tags = [tag.strip() for tag in tags.split(" ") if tag.strip()]
                new_journal_entry.tags = tags
                journal_entries = [new_journal_entry] + journal_entries
            save(journal_entries)
        print("\u2705 Journal populated.")


if __name__ == "__main__":
    app()
