from rich.console import Console
from rich.table import Table

console = Console()


def make_table() -> Table:
    """
    Construct a Table object
    """

    table = Table(title="Dev Journal Entries", title_style="blue")

    table.add_column("Id", justify="right", style="yellow")
    table.add_column("Title", justify="right", style="red")
    table.add_column("Content", justify="right", style="cyan")
    table.add_column("Tags", justify="right", style="green")
    table.add_column("Date", justify="right", style="magenta")

    return table
