"""Safe git commit operations."""

from pathlib import Path
from git import Repo


class SafeCommit:
    """Creates atomic commits with brownfield prefix."""

    def __init__(self, repo: Repo):
        self.repo = repo

    def commit(self, message: str, files: list[Path]) -> str:
        """Create atomic commit with [brownfield] prefix."""
        # Add files to index
        self.repo.index.add([str(f) for f in files])
        
        # Create commit with prefix
        full_message = f"[brownfield] {message}"
        commit = self.repo.index.commit(full_message)
        
        return commit.hexsha
