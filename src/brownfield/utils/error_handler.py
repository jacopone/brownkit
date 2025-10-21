"""Common error handling utilities for CLI commands."""

import sys
import traceback
from functools import wraps
from typing import Callable

from rich.console import Console

from brownfield.config import BrownfieldConfig
from brownfield.exceptions import BrownfieldError

console = Console()


def handle_errors(func: Callable) -> Callable:
    """Decorator for consistent error handling in CLI commands.

    Wraps CLI command functions to:
    - Catch BrownfieldError and display formatted error + suggestion
    - Catch unexpected errors and show traceback in debug mode
    - Exit with appropriate status code

    Usage:
        @click.command()
        @handle_errors
        def my_command():
            # Your code here
            pass
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BrownfieldError as e:
            # Handle our custom exceptions with formatted output
            console.print(f"\n[red]✗ Error:[/red] {e.message}")
            if e.suggestion:
                console.print(f"\n[yellow]💡 Suggestion:[/yellow] {e.suggestion}")
            sys.exit(1)
        except KeyboardInterrupt:
            console.print("\n\n[yellow]⚠ Interrupted by user[/yellow]")
            console.print("\nRun [cyan]brownfield resume[/cyan] to continue from last checkpoint")
            sys.exit(130)  # Standard exit code for SIGINT
        except Exception as e:
            # Handle unexpected errors
            console.print(f"\n[red]✗ Unexpected Error:[/red] {e}")
            if BrownfieldConfig.is_debug_enabled():
                console.print("\n[dim]Traceback:[/dim]")
                console.print(traceback.format_exc())
            else:
                console.print("\n[dim]Set BROWNFIELD_DEBUG=true for full traceback[/dim]")
            sys.exit(1)

    return wrapper


def validate_prerequisites(project_root, require_git: bool = False, require_state: bool = False):
    """Validate common prerequisites for commands.

    Args:
        project_root: Project root directory
        require_git: Whether git repository is required
        require_state: Whether brownfield state file is required

    Raises:
        GitNotFoundError: If git repository required but not found
        StateNotFoundError: If state file required but not found
    """
    if require_git:
        git_dir = project_root / ".git"
        if not git_dir.exists():
            from brownfield.exceptions import GitNotFoundError

            raise GitNotFoundError(project_root)

    if require_state:
        from brownfield.config import BrownfieldConfig
        from brownfield.exceptions import StateNotFoundError

        state_path = BrownfieldConfig.get_state_path(project_root)
        if not state_path.exists():
            raise StateNotFoundError(state_path)


def check_tool_availability(tool: str, install_instructions: str = None) -> bool:
    """Check if a required tool is available in PATH.

    Args:
        tool: Name of the tool to check
        install_instructions: Optional installation instructions

    Returns:
        True if tool is available, False otherwise

    Raises:
        ToolNotFoundError: If tool is not found and install_instructions provided
    """
    import shutil

    if shutil.which(tool):
        return True

    if install_instructions:
        from brownfield.exceptions import ToolNotFoundError

        raise ToolNotFoundError(tool, install_instructions)

    return False


def safe_file_operation(operation: Callable, error_message: str, suggestion: str = None):
    """Wrap file operations with better error handling.

    Args:
        operation: Function performing the file operation
        error_message: Error message to display on failure
        suggestion: Optional suggestion for fixing the error

    Raises:
        FileSystemError: If operation fails
    """
    try:
        return operation()
    except PermissionError as e:
        from brownfield.exceptions import PermissionError as BrownfieldPermissionError

        raise BrownfieldPermissionError(e.filename, "write") from e
    except OSError as e:
        if e.errno == 28:  # ENOSPC - No space left on device
            from brownfield.exceptions import DiskSpaceError

            raise DiskSpaceError(0, 0) from e  # Actual values would need to be calculated
        from brownfield.exceptions import FileSystemError

        raise FileSystemError(error_message, suggestion) from e
