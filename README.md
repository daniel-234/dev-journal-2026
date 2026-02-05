# Dev Journal app

Save and retrieve entries in a JSON file.

`dev-journal-2026` is a command-line tool that saves entries and lets you display them and see some satistics.

Entries must have a title, some content and comma-separated tags. Users can edit or even delete a saved tag, based on its ID. There is also the possibility to add some fake data to the journal, for example if you want to quickly demo it.

# Installation

The project is managed with [uv](https://github.com/astral-sh/uv). To install the dependencies, use the instruction

`uv sync`

# Usage

To run the application and visualize the commands, type

`uv run journal --help`

## Features

- `add`: Add an entry to the journal (args: `--title`, `--content`, `--tags` [comma separated]).
- `display`: Visualize all the journal entries.
- `stats`: Show some overall statistics.
- `search`: Search for string matching in titles, content and tags (option: `--titles-only` to restrict the search by title).
- `edit`: Edit an entry content given its ID.
- `delete`: Delete an entry given its ID.
- `populate`: Populate the journal with random content.


# Acknowledgment

Thanks to the wonderful people at [Pybites](https://pybit.es) and especially to @bbelderbos.
