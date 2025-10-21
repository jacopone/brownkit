"""Rich console output formatting."""

from rich.console import Console


class OutputFormatter:
    """Rich UI formatting."""

    def __init__(self):
        self.console = Console()

    def success(self, message: str) -> None:
        """Print success message."""
        self.console.print(f"[green]✓[/green] {message}")

    def error(self, message: str) -> None:
        """Print error message."""
        self.console.print(f"[red]✗[/red] {message}")

    def warning(self, message: str) -> None:
        """Print warning message."""
        self.console.print(f"[yellow]⚠[/yellow] {message}")

    def info(self, message: str) -> None:
        """Print info message."""
        self.console.print(f"[blue]ℹ[/blue] {message}")
