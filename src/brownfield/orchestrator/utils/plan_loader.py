"""Utilities for loading and saving unified remediation plans."""

import json
from pathlib import Path
from typing import Optional

from brownfield.config import BrownfieldConfig
from brownfield.exceptions import StateNotFoundError
from brownfield.models.orchestrator import (
    QualityPlan,
    StructurePlan,
    TestingPlan,
    UnifiedPlan,
)


def save_unified_plan(plan: UnifiedPlan, project_root: Optional[Path] = None) -> Path:
    """
    Save unified plan to .specify/memory/unified-plan.json.

    Args:
        plan: UnifiedPlan to persist
        project_root: Project root directory (uses config default if None)

    Returns:
        Path to saved plan file
    """
    if project_root is None:
        project_root = BrownfieldConfig.get_project_root()

    plan_path = project_root / ".specify/memory/unified-plan.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)

    plan_data = {
        "structure_plan": {
            "files_to_move": plan.structure_plan.files_to_move if plan.structure_plan else {},
            "directories_to_create": plan.structure_plan.directories_to_create if plan.structure_plan else [],
            "compliant": plan.structure_plan.compliant if plan.structure_plan else True,
            "issues_found": plan.structure_plan.issues_found if plan.structure_plan else [],
        } if plan.structure_plan else None,
        "testing_plan": {
            "core_modules": [str(m) for m in plan.testing_plan.core_modules],
            "smoke_tests_needed": plan.testing_plan.smoke_tests_needed,
            "contract_tests_needed": plan.testing_plan.contract_tests_needed,
            "current_coverage": plan.testing_plan.current_coverage,
            "target_coverage": plan.testing_plan.target_coverage,
            "framework": plan.testing_plan.framework,
        },
        "quality_plan": {
            "linter": plan.quality_plan.linter,
            "formatter": plan.quality_plan.formatter,
            "hooks_to_install": plan.quality_plan.hooks_to_install,
            "complexity_violations": plan.quality_plan.complexity_violations,
            "security_issues": plan.quality_plan.security_issues,
        },
        "estimated_duration_hours": plan.estimated_duration_hours,
        "dependencies": plan.dependencies,
        "plan_markdown": plan.plan_markdown,
        "plan_path": str(plan.plan_path),
        "total_tasks": plan.total_tasks,
    }

    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(plan_data, f, indent=2)

    return plan_path


def load_unified_plan(project_root: Optional[Path] = None) -> UnifiedPlan:
    """
    Load unified plan from .specify/memory/unified-plan.json.

    Args:
        project_root: Project root directory (uses config default if None)

    Returns:
        UnifiedPlan loaded from file

    Raises:
        StateNotFoundError: If plan file doesn't exist
    """
    if project_root is None:
        project_root = BrownfieldConfig.get_project_root()

    plan_path = project_root / ".specify/memory/unified-plan.json"

    if not plan_path.exists():
        raise StateNotFoundError(plan_path)

    with open(plan_path, "r", encoding="utf-8") as f:
        plan_data = json.load(f)

    # Reconstruct StructurePlan
    structure_plan = None
    if plan_data.get("structure_plan"):
        sp_data = plan_data["structure_plan"]
        structure_plan = StructurePlan(
            files_to_move=sp_data["files_to_move"],
            directories_to_create=sp_data["directories_to_create"],
            compliant=sp_data["compliant"],
            issues_found=sp_data["issues_found"],
        )

    # Reconstruct TestingPlan
    tp_data = plan_data["testing_plan"]
    testing_plan = TestingPlan(
        core_modules=[Path(m) for m in tp_data["core_modules"]],
        smoke_tests_needed=tp_data["smoke_tests_needed"],
        contract_tests_needed=tp_data["contract_tests_needed"],
        current_coverage=tp_data["current_coverage"],
        target_coverage=tp_data["target_coverage"],
        framework=tp_data["framework"],
    )

    # Reconstruct QualityPlan
    qp_data = plan_data["quality_plan"]
    quality_plan = QualityPlan(
        linter=qp_data["linter"],
        formatter=qp_data["formatter"],
        hooks_to_install=qp_data["hooks_to_install"],
        complexity_violations=qp_data["complexity_violations"],
        security_issues=qp_data["security_issues"],
    )

    return UnifiedPlan(
        structure_plan=structure_plan,
        testing_plan=testing_plan,
        quality_plan=quality_plan,
        estimated_duration_hours=plan_data["estimated_duration_hours"],
        dependencies=plan_data["dependencies"],
        plan_markdown=plan_data["plan_markdown"],
        plan_path=Path(plan_data["plan_path"]),
        total_tasks=plan_data["total_tasks"],
    )
