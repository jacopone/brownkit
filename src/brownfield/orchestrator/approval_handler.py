"""Approval handler for destructive operations."""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class ApprovalHandler:
    """Handles user approval for destructive operations."""

    def __init__(self, auto_approve: bool = False):
        """Initialize approval handler."""
        self.auto_approve = auto_approve
        self.console = Console()

    def request_approval(
        self,
        operation: str,
        details: list[str],
        threshold: int = 5,
        warning: Optional[str] = None,
    ) -> bool:
        """
        Request user approval for destructive operation.

        Args:
            operation: Name of the operation (e.g., "file moves", "deletions")
            details: List of details about what will be changed
            threshold: Number of changes that triggers approval prompt
            warning: Optional warning message to display

        Returns:
            True if approved, False if denied
        """
        # Auto-approve if configured
        if self.auto_approve:
            self.console.print(
                f"[yellow]⚡ Auto-approving {len(details)} {operation}[/yellow]"
            )
            return True

        # Skip approval if below threshold
        if len(details) < threshold:
            return True

        # Display what will be changed
        self.console.print()
        table = Table(title=f"Planned {operation.title()}")
        table.add_column("#", style="cyan", no_wrap=True)
        table.add_column("Item", style="white")

        for i, detail in enumerate(details[:20], 1):  # Show max 20 items
            table.add_row(str(i), detail)

        if len(details) > 20:
            table.add_row("...", f"({len(details) - 20} more)")

        self.console.print(table)
        self.console.print()

        # Display warning if provided
        if warning:
            self.console.print(
                Panel(
                    warning,
                    title="⚠️  Warning",
                    border_style="yellow",
                )
            )
            self.console.print()

        # Prompt for approval
        prompt_text = (
            f"⚠️  About to perform {len(details)} {operation}. "
            f"Each will be a separate git commit.\n   Continue?"
        )

        return click.confirm(prompt_text, default=False)

    def request_file_move_approval(
        self, file_operations: list[tuple[Path, Path]]
    ) -> bool:
        """Request approval for file move operations."""
        details = [
            f"{src.name} → {dest.relative_to(dest.parent.parent)}"
            for src, dest in file_operations
        ]

        warning = (
            "File moves will update import paths across your codebase. "
            "Each move will be committed separately with build verification. "
            "Failed moves will be automatically reverted."
        )

        return self.request_approval(
            operation="file moves",
            details=details,
            threshold=5,
            warning=warning,
        )

    def request_deletion_approval(self, files_to_delete: list[Path]) -> bool:
        """Request approval for file deletion operations."""
        details = [str(f) for f in files_to_delete]

        warning = (
            "⛔ File deletion is PERMANENT and cannot be automatically reverted. "
            "Ensure you have a backup or the files are tracked in git."
        )

        return self.request_approval(
            operation="file deletions",
            details=details,
            threshold=1,  # Always prompt for deletions
            warning=warning,
        )

    def request_config_change_approval(
        self, config_files: list[str], dry_run_preview: Optional[str] = None
    ) -> bool:
        """Request approval for build configuration changes."""
        details = config_files

        warning = (
            "Build configuration changes may affect how your project is built, tested, "
            "and deployed. Review changes carefully before approving."
        )

        if dry_run_preview:
            self.console.print(
                Panel(
                    dry_run_preview,
                    title="📄 Preview of Changes",
                    border_style="blue",
                )
            )
            self.console.print()

        return self.request_approval(
            operation="config file changes",
            details=details,
            threshold=3,
            warning=warning,
        )

    def confirm_continue_after_failure(
        self, failed_operation: str, continue_text: str = "Continue with remaining operations?"
    ) -> bool:
        """Confirm whether to continue after a failure."""
        if self.auto_approve:
            return True

        self.console.print()
        self.console.print(f"[red]✗[/red] {failed_operation}")
        self.console.print()

        return click.confirm(continue_text, default=True)

    def show_dry_run_summary(self, operations: dict[str, list[str]]) -> None:
        """Display dry-run summary of planned operations."""
        self.console.print()
        self.console.print(
            Panel(
                "[yellow]🔍 DRY RUN MODE - No changes will be made[/yellow]",
                border_style="yellow",
            )
        )
        self.console.print()

        for operation_name, items in operations.items():
            if not items:
                continue

            table = Table(title=operation_name)
            table.add_column("Item", style="cyan")

            for item in items:
                table.add_row(item)

            self.console.print(table)
            self.console.print()

        self.console.print(
            "[yellow]Run without --dry-run to execute these changes[/yellow]"
        )
        self.console.print()
