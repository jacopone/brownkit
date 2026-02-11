"""Decision tracking models."""

from dataclasses import dataclass, field
from datetime import datetime

from brownfield.models.assessment import ConfidenceLevel
from brownfield.models.state import Phase


@dataclass
class Alternative:
    """Alternative solution that was considered."""

    description: str
    pros: list[str]
    cons: list[str]
    rejected_reason: str


@dataclass
class Risk:
    """Identified risk with mitigation strategy."""

    description: str
    likelihood: str
    impact: str
    mitigation: str
    rollback_procedure: str | None = None


@dataclass
class DecisionEntry:
    """Documented decision with rationale."""

    timestamp: datetime
    phase: Phase
    decision_id: str
    problem: str
    evidence: list[str]
    solution: str
    rationale: str
    confidence: ConfidenceLevel
    alternatives: list[Alternative] = field(default_factory=list)
    risks: list[Risk] = field(default_factory=list)
    requires_human_approval: bool = False
    approved: bool = False
    approved_by: str | None = None

    def to_markdown(self) -> str:
        """Format decision as Markdown section."""
        md = f"## Decision {self.decision_id} - {self.phase.value}\n\n"
        md += f"**Timestamp**: {self.timestamp.isoformat()}\n"
        md += f"**Confidence**: {self.confidence.name}\n\n"

        md += f"### Problem\n{self.problem}\n\n"
        md += "**Evidence**:\n"
        md += "\n".join(f"- {e}" for e in self.evidence) + "\n\n"

        md += f"### Solution\n{self.solution}\n\n"
        md += f"**Rationale**: {self.rationale}\n\n"

        if self.alternatives:
            md += "### Alternatives Considered\n"
            for alt in self.alternatives:
                md += f"- **{alt.description}**: {alt.rejected_reason}\n"
            md += "\n"

        if self.risks:
            md += "### Risks\n"
            for risk in self.risks:
                md += f"- **{risk.description}** ({risk.likelihood} likelihood, "
                md += f"{risk.impact} impact)\n"
                md += f"  - Mitigation: {risk.mitigation}\n"
                if risk.rollback_procedure:
                    md += f"  - Rollback: {risk.rollback_procedure}\n"
            md += "\n"

        if self.requires_human_approval:
            approval_status = "✓ Approved" if self.approved else "⏳ Pending"
            md += f"**Approval Status**: {approval_status}"
            if self.approved_by:
                md += f" by {self.approved_by}"
            md += "\n\n"

        return md
