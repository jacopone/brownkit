"""Decision logging for transparent reasoning."""

from pathlib import Path

from brownfield.models.decision import DecisionEntry


class DecisionLogger:
    """Manages decision log persistence."""

    def __init__(self, log_path: Path):
        self.log_path = log_path

    def log_decision(self, decision: DecisionEntry) -> None:
        """Append decision to log file."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(decision.to_markdown())
            f.write("\n---\n\n")
