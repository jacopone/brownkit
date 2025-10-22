"""Phase state machine orchestrator."""

from typing import Optional

from brownfield.models.state import BrownfieldState, Phase, ReEntryEvent


class PhaseOrchestrator:
    """Orchestrates phase transitions."""

    # Define allowed phase transitions as adjacency list
    PHASE_TRANSITIONS: dict[Phase, list[Phase]] = {
        Phase.ASSESSMENT: [Phase.STRUCTURE],
        Phase.STRUCTURE: [Phase.TESTING],
        Phase.TESTING: [Phase.QUALITY],
        Phase.QUALITY: [Phase.VALIDATION],
        Phase.VALIDATION: [Phase.GRADUATED],
        Phase.GRADUATED: [Phase.STRUCTURE, Phase.TESTING, Phase.QUALITY],  # Re-entry
    }

    # Define requirements for each phase transition
    PHASE_REQUIREMENTS: dict[Phase, list[str]] = {
        Phase.STRUCTURE: ["baseline_metrics_captured"],
        Phase.TESTING: ["structure_phase_completed"],
        Phase.QUALITY: ["testing_phase_completed", "test_coverage_min_60"],
        Phase.VALIDATION: ["quality_phase_completed"],
        Phase.GRADUATED: ["all_gates_passed"],
    }

    def __init__(self, state: BrownfieldState):
        self.state = state

    def can_advance_to(self, next_phase: Phase) -> tuple[bool, Optional[str]]:
        """Check if can advance to next phase.

        Returns:
            (can_advance, reason): Tuple of boolean and optional reason string.
                                  If can_advance is False, reason explains why.
        """
        current_phase = self.state.current_phase

        # Check if transition is allowed
        allowed_transitions = self.PHASE_TRANSITIONS.get(current_phase, [])
        if next_phase not in allowed_transitions:
            allowed_names = ", ".join(p.value for p in allowed_transitions)
            return False, (
                f"Cannot transition from {current_phase.value} to {next_phase.value}. "
                f"Allowed transitions: {allowed_names or 'none'}"
            )

        # Check if requirements are met
        requirements = self.PHASE_REQUIREMENTS.get(next_phase, [])
        unmet_requirements = self._check_requirements(requirements)

        if unmet_requirements:
            return False, (
                f"Cannot advance to {next_phase.value}. "
                f"Unmet requirements: {', '.join(unmet_requirements)}"
            )

        return True, None

    def _check_requirements(self, requirements: list[str]) -> list[str]:
        """Check which requirements are not met.

        Returns:
            List of unmet requirement names
        """
        unmet = []

        for req in requirements:
            if req == "baseline_metrics_captured":
                # Check if baseline metrics exist and are valid
                if not self.state.baseline_metrics:
                    unmet.append(req)

            elif req == "structure_phase_completed":
                # Check if structure phase has a completion timestamp
                complete_key = f"{Phase.STRUCTURE.value}_complete"
                if complete_key not in self.state.phase_timestamps:
                    unmet.append(req)

            elif req == "testing_phase_completed":
                # Check if testing phase has a completion timestamp
                complete_key = f"{Phase.TESTING.value}_complete"
                if complete_key not in self.state.phase_timestamps:
                    unmet.append(req)

            elif req == "test_coverage_min_60":
                # Check if test coverage meets minimum threshold
                metrics = self.state.current_metrics or self.state.baseline_metrics
                if not metrics or metrics.test_coverage < 0.6:
                    unmet.append(req)

            elif req == "quality_phase_completed":
                # Check if quality phase has a completion timestamp
                complete_key = f"{Phase.QUALITY.value}_complete"
                if complete_key not in self.state.phase_timestamps:
                    unmet.append(req)

            elif req == "all_gates_passed":
                # Check if all validation gates passed
                # This would be set by ValidationOrchestrator
                validation_key = "validation_passed"
                if validation_key not in self.state.phase_timestamps:
                    unmet.append(req)

        return unmet

    def advance(self, next_phase: Phase) -> None:
        """Advance to next phase without validation.

        Use advance_with_validation() for safer transitions.
        """
        self.state.advance_phase(next_phase)

    def advance_with_validation(self, next_phase: Phase) -> None:
        """Advance to next phase with validation.

        Raises:
            ValueError: If transition is not allowed or requirements are not met.
        """
        can_advance, reason = self.can_advance_to(next_phase)

        if not can_advance:
            raise ValueError(reason)

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
