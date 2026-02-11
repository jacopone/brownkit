"""Branch protection guard."""

from git import Repo


class BranchGuard:
    """Prevents force push to main/master."""

    PROTECTED_BRANCHES = ["main", "master"]

    def __init__(self, repo: Repo):
        self.repo = repo

    def check_protected(self) -> bool:
        """Check if current branch is protected."""
        current_branch = self.repo.active_branch.name
        return current_branch in self.PROTECTED_BRANCHES
