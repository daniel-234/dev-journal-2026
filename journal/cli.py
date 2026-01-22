from collections import Counter
from pathlib import Path
from typing import Annotated

import typer
from faker import Faker

from journal.db import JournalDatabase
from journal.models import EntryAlreadyExists, JournalEntry

MAX_ITEMS = 50

# Default database file path
DEFAULT_DB_FILE = Path("journal.json")

app = typer.Typer()


@app.command()
def add(
    title: Annotated[str, typer.Argument(help="Insert a title for this entry.")],
    content: Annotated[str, typer.Argument(help="Insert a content for this entry.")],
    tags: Annotated[str, typer.Argument(help="Insert tags (comma separated).")],
    file: Path = DEFAULT_DB_FILE,
) -> None:
    """
    Create a new journal entry and save it to the JSON file, at the beginning of the list.
    """

    if not title:
        typer.echo("Please, insert a title for the entry.")
        raise typer.Exit()
    if not content:
        typer.echo("Please, intert some content for this entry.")
        raise typer.Exit()
    tags = [tag.strip() for tag in tags.split(",") if tag.strip()]

    # Instantiate a Database object
    db = JournalDatabase(file)
    # Use the context manager to load and save the entries
    with db.session() as journal_entries:
        try:
            new_journal_entry = JournalEntry.create(title, content, journal_entries)
            new_journal_entry.timestamp = new_journal_entry.timestamp.isoformat(
                timespec="seconds"
            )
            new_journal_entry.tags = tags
            # Mutate the list in place with "insert" to persist the object yielded
            journal_entries.append(new_journal_entry)
            print("\u2705 Entry saved.")
        except TypeError:
            print("Please, insert a title and the content in your journal entry.")


@app.command()
def edit(
    entry_id: Annotated[str, typer.Argument(help="Entry ID to edit")],
    file: Path = DEFAULT_DB_FILE,
) -> None | str:
    """
    Edit an entry content given its ID.
    """

    if not entry_id:
        typer.echo("No ID typed.")
        raise typer.Exit("No")
    # Instantiate a Database object
    db = JournalDatabase(file)
    # Load the entries from the dev journal, if any.
    with db.session() as journal_entries:
        if not any(entry_id == entry.id for entry in journal_entries):
            # If there is no entry with this ID, print a message to the screen.
            print("No entry was found with this ID")
        else:
            # Iterate through the dictionaries in the journal_entries list.
            # Check if the ID passed by the user is found in an entry value.
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
                    break


@app.command()
def delete(
    entry_id: Annotated[str, typer.Argument(help="Entry ID to delete")],
    file: Path = DEFAULT_DB_FILE,
) -> None | str:
    """
    Delete an entry given its ID.
    """

    if not entry_id:
        raise ValueError("No ID typed.")
    # Instantiate a Database object
    db = JournalDatabase(file)
    # Load the entries from the dev journal, if any.
    with db.session() as journal_entries:
        if not any(entry_id in entry.id for entry in journal_entries):
            # If there is no entry with this ID, print a message to the screen.
            print("No entry was found with this ID")
        else:
            # Iterate through the dictionaries in the journal_entries list.
            # Check if the ID passed by the user is found in an entry value.
            for entry in journal_entries:
                # If the ID of the current entry is the same as the one
                # typed by the user, delete this entry from the list.
                if entry.id == entry_id:
                    journal_entries.remove(entry)
                    print("\u2702 \u27a1 \u274e  Entry removed.")
                    break


@app.command()
def display(
    tags: list[str] = typer.Option(
        default=[], help="Match only entries with any of the given tags"
    ),
    file: Path = DEFAULT_DB_FILE,
) -> None:
    """
    Print all journal entries to the console.
    """

    # Instantiate a Database object
    db = JournalDatabase(file)
    # Load entries
    with db.session() as journal_entries:
        # Print a message to the user to let know there's no entry yet
        if not journal_entries:
            print("No entries yet in Dev Journal.")
            raise typer.Exit()
        journal_entries = sorted(
            journal_entries, key=lambda entry: entry.id, reverse=True
        )
        if tags:
            # Match an entry from entries if any given 'query_tag' in the given tags list is a tag to that entry
            journal_entries = [
                entry
                for entry in journal_entries
                if any(
                    query_tag.lower() in map(str.lower, entry.tags)
                    for query_tag in tags
                )
            ]
        for entry in journal_entries:
            print("\n")
            print("-" * 70)
            print(f"ID {entry.id}:  {entry.title.upper()} - ({entry.timestamp})")
            print("-" * 70)
            print(f"{entry.content}")
            print("-" * 70)
            print(f"tags: {entry.tags}\n")


@app.command()
def search(
    query: str,
    titles_only: bool = typer.Option(
        default=False, help="Limit your search results to tile only"
    ),
    file: Path = DEFAULT_DB_FILE,
) -> list[JournalEntry]:
    """
    Search for string matching in entry titles, content and tags.
    """

    # Instantiate a Database object
    db = JournalDatabase(file)
    with db.session() as journal_entries:
        # If the option "titles_ony" is True, limit the search results to titles
        if titles_only:
            search_results = [
                entry
                for entry in journal_entries
                if query.lower() in entry.title.lower()
            ]
        # If the option "titles_only" is False, show results from content and tags, as well
        else:
            title_results = [
                entry
                for entry in journal_entries
                if query.lower() in entry.title.lower()
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
def stats(file: Path = DEFAULT_DB_FILE) -> None:
    """
    Show some overall stats: total entries, counts by tag, average content length, most common tag.
    """

    # Instantiate a Database object
    db = JournalDatabase(file)
    with db.session() as journal_entries:
        total = len(journal_entries)
        print(f"\nNumber of entries: {total}")
        print("-" * 50)
        tags = []
        for entry in journal_entries:
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
            print(
                f"\nMost common tag(s): {most_common} that appears {higher_freq} times."
            )


@app.command()
def populate(num_items: int, file: Path = DEFAULT_DB_FILE) -> None:
    """
    Populate the journal with fake content.
    """

    if num_items > MAX_ITEMS:
        print(f"Please, choose a number of items not greater than {MAX_ITEMS}.")
    else:
        db = JournalDatabase(file)
        fake = Faker()
        Faker.seed()
        with db.session() as journal_entries:
            counter = 0
            while counter < num_items:
                new_title = fake.company()
                new_company = fake.catch_phrase()
                new_tags = fake.bs()

                try:
                    new_journal_entry = JournalEntry.create(
                        new_title, new_company, journal_entries
                    )
                except EntryAlreadyExists:
                    print("Entry already exists. Skipping...")
                    continue
                new_journal_entry.timestamp = new_journal_entry.timestamp.isoformat(
                    timespec="seconds"
                )
                tags = [tag.strip() for tag in new_tags.split(" ") if tag.strip()]
                new_journal_entry.tags = tags
                journal_entries.append(new_journal_entry)
                counter += 1

            if counter != num_items:
                print(
                    f"\u2705 Journal populated with {counter} new entries (requested {num_items}; some duplicates were skipped)."
                )
            else:
                print(f"\u2705 Journal populated with {counter} new entries.")
