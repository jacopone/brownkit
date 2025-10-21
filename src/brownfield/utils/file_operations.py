"""File operations utilities."""

import shutil
from pathlib import Path


class FileOperations:
    """Safe file operations."""

    @staticmethod
    def safe_move(src: Path, dst: Path) -> None:
        """Safely move file."""
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

    @staticmethod
    def safe_copy(src: Path, dst: Path) -> None:
        """Safely copy file."""
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dst))
