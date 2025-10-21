"""Git history tracking."""

from git import Repo


class HistoryTracker:
    """Tracks commit history for rollback."""

    def __init__(self, repo: Repo):
        self.repo = repo

    def get_brownfield_commits(self) -> list[str]:
        """Get all brownfield commits."""
        commits = []
        for commit in self.repo.iter_commits():
            if commit.message.startswith("[brownfield]"):
                commits.append(commit.hexsha)
        return commits
