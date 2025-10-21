"""Phase state machine orchestrator."""

from brownfield.models.state import BrownfieldState, Phase, ReEntryEvent


class PhaseOrchestrator:
    """Orchestrates phase transitions."""

    def __init__(self, state: BrownfieldState):
        self.state = state

    def can_advance_to(self, next_phase: Phase) -> bool:
        """Check if can advance to next phase."""
        # TODO: Implement phase transition validation
        return True

    def advance(self, next_phase: Phase) -> None:
        """Advance to next phase."""
        self.state.advance_phase(next_phase)

    def handle_re_entry(self, regression: ReEntryEvent) -> Phase:
        """
        Handle re-entry workflow after quality regression detected.

        When a graduated project experiences metric regression below thresholds,
        this method transitions back to the appropriate remediation phase.

        Args:
            regression: Detected regression event

        Returns:
            Phase to re-enter
        """
        # Determine which phase to return to based on regression trigger
        re_entry_phase = regression.re_entry_phase

        # Reset current phase to the re-entry phase
        self.state.current_phase = re_entry_phase

        # Record phase timestamp for re-entry
        from datetime import datetime

        timestamp_key = f"{re_entry_phase.value}_re_entry"
        self.state.phase_timestamps[timestamp_key] = datetime.utcnow()

        return re_entry_phase

    def can_re_enter(self) -> bool:
        """
        Check if project can re-enter brownfield workflow.

        Projects can re-enter if:
        - They have graduated (current_phase == GRADUATED)
        - A quality regression has been detected

        Returns:
            True if re-entry is allowed
        """
        return self.state.graduated or self.state.current_phase == Phase.GRADUATED

    def get_re_entry_phase_for_trigger(self, trigger: str) -> Phase:
        """
        Determine which phase to enter based on regression trigger.

        Args:
            trigger: Regression trigger type (e.g., "coverage_drop", "complexity_increase")

        Returns:
            Phase to re-enter
        """
        # Map triggers to phases
        trigger_phase_map = {
            "coverage_drop": Phase.TESTING,
            "complexity_increase": Phase.QUALITY,
            "security_breach": Phase.QUALITY,
            "structure_degradation": Phase.STRUCTURE,
        }

        return trigger_phase_map.get(trigger, Phase.ASSESSMENT)
