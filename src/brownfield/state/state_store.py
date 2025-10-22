"""State persistence for brownfield workflow."""

import json
from pathlib import Path
from typing import Optional

from brownfield.exceptions import InvalidStateError, StateNotFoundError
from brownfield.models.state import BrownfieldState, ReEntryEvent
from brownfield.state.migrations.migrate_state_v1 import migrate_state_file


class StateStore:
    """Manages brownfield state persistence."""

    def __init__(self, state_path: Path):
        """
        Initialize state store.

        Args:
            state_path: Path to .specify/memory directory OR full path to state.json
                       (for backward compatibility)
        """
        # Handle both directory and file paths for backward compatibility
        if state_path.is_dir() or not state_path.suffix:
            # Given a directory, use state.json as filename
            memory_dir = state_path
            self.state_path = memory_dir / "state.json"
        else:
            # Given a full file path (backward compatibility)
            self.state_path = state_path
            memory_dir = state_path.parent

        # Auto-migrate old brownfield-state.json to state.json
        migrate_state_file(memory_dir)

    def load(self) -> BrownfieldState:
        """Load state from file.

        Returns:
            BrownfieldState object

        Raises:
            StateNotFoundError: If state file doesn't exist
            InvalidStateError: If state file is corrupted or has invalid schema
        """
        if not self.state_path.exists():
            raise StateNotFoundError(self.state_path)

        try:
            return BrownfieldState.load(self.state_path)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise InvalidStateError(self.state_path, str(e)) from e

    def save(self, state: BrownfieldState) -> None:
        """
        Save state to file.

        Args:
            state: BrownfieldState object to save
        """
        state.save(self.state_path)

    def exists(self) -> bool:
        """Check if state file exists."""
        return self.state_path.exists()

    def detect_regression(self, state: BrownfieldState) -> Optional[ReEntryEvent]:
        """
        Check current metrics against baseline for regressions.

        Compares current metrics to baseline and detects threshold breaches
        that would require re-entering the brownfield workflow.

        Args:
            state: Current brownfield state

        Returns:
            ReEntryEvent if regression detected, None otherwise
        """
        # Delegate to state's detect_regression method
        regression = state.detect_regression()

        if regression:
            # Add event to state's re_entry_events list
            state.re_entry_events.append(regression)

        return regression

    def record_re_entry(
        self, state: BrownfieldState, event: ReEntryEvent
    ) -> None:
        """
        Record a re-entry event and save state.

        Args:
            state: Current brownfield state
            event: Re-entry event to record
        """
        if event not in state.re_entry_events:
            state.re_entry_events.append(event)

        self.save(state)

    def resolve_re_entry(
        self, state: BrownfieldState, event_index: int
    ) -> None:
        """
        Mark a re-entry event as resolved.

        Args:
            state: Current brownfield state
            event_index: Index of event in re_entry_events list
        """
        from datetime import datetime

        if 0 <= event_index < len(state.re_entry_events):
            state.re_entry_events[event_index].resolved = True
            state.re_entry_events[event_index].resolved_at = datetime.utcnow()
            self.save(state)
