"""Speckit templates generator."""

from pathlib import Path

from brownfield.models.state import BrownfieldState


class TemplatesGenerator:
    """Generates Speckit spec/plan/tasks templates."""

    def __init__(self, project_root: Path, state: BrownfieldState):
        self.project_root = project_root
        self.state = state

    def generate_spec_template(self) -> str:
        """Generate spec-template.md for new features."""
        return f"""# Feature Specification Template

## Overview

**Feature Name**: [Short descriptive name]

**Priority**: [P0/P1/P2/P3]

**Status**: Draft

**Language**: {self.state.language}

## Problem Statement

[Describe the problem this feature solves. Include user pain points and business context.]

## User Stories

### User Story 1 - [Title] (Priority: P1)

[As a [user type], I want [goal] so that [benefit]]

**Why this priority**: [Explain importance]

**Acceptance Scenarios**:

1. **Given** [context], **When** [action], **Then** [expected outcome]
2. **Given** [context], **When** [action], **Then** [expected outcome]

**Independent Test**: [How to verify this story works standalone]

## Functional Requirements

- **FR-001**: [MUST/SHOULD/MAY] [requirement description]
- **FR-002**: [MUST/SHOULD/MAY] [requirement description]

## Non-Functional Requirements

- **NFR-001**: [Performance/Security/Scalability requirement]
- **NFR-002**: [Performance/Security/Scalability requirement]

## Data Models

[Describe key data structures, schemas, or database changes]

## Success Criteria

- **SC-001**: [Measurable criterion with specific threshold]
- **SC-002**: [Measurable criterion with specific threshold]

## Out of Scope

[Explicitly list what this feature will NOT include]

## Dependencies

[List dependencies on other features, services, or teams]

## Security Considerations

[List security requirements, threat model, authentication/authorization needs]

## Testing Strategy

[Describe testing approach: unit, integration, e2e, performance tests]

## Rollout Plan

[Describe feature flags, gradual rollout, rollback procedures]
"""

    def generate_plan_template(self) -> str:
        """Generate plan-template.md for implementation plans."""
        return f"""# Implementation Plan Template

## Overview

**Feature**: [Feature name from spec.md]

**Status**: Draft

**Language**: {self.state.language}

**Estimated Complexity**: [Low/Medium/High]

## Architecture Decisions

### Decision 1: [Topic]

**Problem**: [What needs to be decided]

**Options Considered**:
1. **Option A**: [Description] - Pros: [...] Cons: [...]
2. **Option B**: [Description] - Pros: [...] Cons: [...]

**Decision**: [Chosen option]

**Rationale**: [Why this option was chosen]

**Risks**: [Potential issues and mitigation strategies]

## Component Design

### Component 1: [Name]

**Location**: `[file path]`

**Purpose**: [What this component does]

**Interface**:
```{self.state.language}
[Function signatures or class definitions]
```

**Dependencies**: [What this component depends on]

**Testing Strategy**: [How to test this component]

## Data Flow

[Describe how data flows through the system for this feature]

```
[ASCII diagram or description]
User → Controller → Service → Repository → Database
```

## File Changes

### New Files

- `[path/to/new/file.py]` - [Purpose]
- `[path/to/test_file.py]` - [Purpose]

### Modified Files

- `[path/to/existing/file.py]` - [What changes]
- `[path/to/config.yaml]` - [What changes]

## Database Changes

[If applicable, describe schema changes, migrations needed]

## API Changes

[If applicable, describe new endpoints, request/response formats]

## Configuration Changes

[Environment variables, config files that need updates]

## Testing Plan

### Unit Tests

- Test [component] with [scenarios]
- Test [component] with [edge cases]

### Integration Tests

- Test [end-to-end flow]
- Test [error conditions]

### Performance Tests

[If applicable, describe performance testing approach]

## Deployment Considerations

- **Feature Flags**: [If using feature flags]
- **Database Migrations**: [Migration strategy]
- **Rollback Plan**: [How to rollback if needed]

## Dependencies

[External libraries, services, or features this depends on]

## Risk Assessment

### High Risk

- [Risk 1 and mitigation]

### Medium Risk

- [Risk 2 and mitigation]

## Timeline Estimate

- **Research/Design**: [X hours/days]
- **Implementation**: [X hours/days]
- **Testing**: [X hours/days]
- **Review/QA**: [X hours/days]

**Total**: [X hours/days]
"""

    def generate_tasks_template(self) -> str:
        """Generate tasks-template.md for task breakdown."""
        return """# Tasks Template

## Task Format

Each task follows this format:

```
- [ ] T### [P?] [Story] Description (source: artifact.md)
```

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup

**Goal**: [Phase goal]

**Independent Test**: [How to verify this phase is complete]

### Implementation

- [ ] T001 [P] [Setup] Create project structure
- [ ] T002 [P] [Setup] Add dependencies to requirements.txt
- [ ] T003 [Setup] Create configuration files

**Checkpoint**: [What should work at this point]

---

## Phase 2: Core Implementation

**Goal**: [Phase goal]

**Independent Test**: [How to verify this phase is complete]

### Implementation for User Story 1

- [ ] T004 [P] [US1] Create data model in [path/to/file.py]
- [ ] T005 [US1] Implement business logic in [path/to/service.py]
- [ ] T006 [US1] Add unit tests in [path/to/test_file.py]

**Checkpoint**: [What should work at this point]

---

## Phase 3: Integration

**Goal**: [Phase goal]

**Independent Test**: [How to verify this phase is complete]

### Implementation

- [ ] T007 [P] [Integration] Wire up components
- [ ] T008 [Integration] Add integration tests

**Checkpoint**: [What should work at this point]

---

## User Story Dependencies

- **User Story 1**: Can start after Setup - No dependencies
- **User Story 2**: Requires US1 for data models

## Parallel Execution Strategy

Tasks marked [P] can run in parallel. Suggested workflow:

1. Complete Setup phase together
2. Once Setup is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
3. Integrate and test

## Definition of Done

Each task is considered complete when:

- [ ] Code implemented and passes linter
- [ ] Unit tests written and passing
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Integration tests passing (if applicable)
"""

    def save_all(self, output_dir: Path | None = None) -> dict[str, Path]:
        """
        Save all three template files.

        Args:
            output_dir: Directory to save templates, defaults to .specify/templates/

        Returns:
            Dictionary mapping template type to saved path
        """
        if output_dir is None:
            output_dir = self.project_root / ".specify" / "templates"

        output_dir.mkdir(parents=True, exist_ok=True)

        saved_paths = {}

        # Save spec template
        spec_path = output_dir / "spec-template.md"
        spec_path.write_text(self.generate_spec_template(), encoding="utf-8")
        saved_paths["spec"] = spec_path

        # Save plan template
        plan_path = output_dir / "plan-template.md"
        plan_path.write_text(self.generate_plan_template(), encoding="utf-8")
        saved_paths["plan"] = plan_path

        # Save tasks template
        tasks_path = output_dir / "tasks-template.md"
        tasks_path.write_text(self.generate_tasks_template(), encoding="utf-8")
        saved_paths["tasks"] = tasks_path

        return saved_paths
