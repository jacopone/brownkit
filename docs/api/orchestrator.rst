Orchestrator Module
===================

The orchestrator module manages workflow execution, phase transitions, and checkpoints.

.. currentmodule:: brownfield.orchestrator

Phase Machine
-------------

.. automodule:: brownfield.orchestrator.phase_machine
   :members:
   :undoc-members:
   :show-inheritance:

Workflow Orchestrators
----------------------

Assessment Orchestrator
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: brownfield.orchestrator.assessment
   :members:
   :undoc-members:
   :show-inheritance:

Plan Orchestrator
~~~~~~~~~~~~~~~~~

.. automodule:: brownfield.orchestrator.plan
   :members:
   :undoc-members:
   :show-inheritance:

Remediation Orchestrator
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: brownfield.orchestrator.remediation
   :members:
   :undoc-members:
   :show-inheritance:

Validation Orchestrator
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: brownfield.orchestrator.validation
   :members:
   :undoc-members:
   :show-inheritance:

Graduation Orchestrator
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: brownfield.orchestrator.graduation
   :members:
   :undoc-members:
   :show-inheritance:

Checkpoint Management
---------------------

.. automodule:: brownfield.orchestrator.checkpoint_manager
   :members:
   :undoc-members:
   :show-inheritance:

Gate Validation
---------------

.. automodule:: brownfield.orchestrator.gate_validator
   :members:
   :undoc-members:
   :show-inheritance:

Approval Handler
----------------

.. automodule:: brownfield.orchestrator.approval_handler
   :members:
   :undoc-members:
   :show-inheritance:

Examples
--------

**Phase Transition with Validation:**

.. code-block:: python

    from brownfield.orchestrator.phase_machine import PhaseOrchestrator
    from brownfield.models.state import BrownfieldState, Phase

    state = BrownfieldState(
        project_root=Path("/path/to/project"),
        current_phase=Phase.ASSESSMENT
    )

    orchestrator = PhaseOrchestrator(state)

    # Check if can advance
    can_advance, reason = orchestrator.can_advance_to(Phase.STRUCTURE)

    if can_advance:
        orchestrator.advance_with_validation(Phase.STRUCTURE)
        print(f"Advanced to {state.current_phase}")
    else:
        print(f"Cannot advance: {reason}")

**Creating Checkpoints:**

.. code-block:: python

    from brownfield.orchestrator.checkpoint_manager import CheckpointManager
    from brownfield.models.checkpoint import Checkpoint, Task

    manager = CheckpointManager(project_root)

    checkpoint = Checkpoint(
        phase=Phase.TESTING,
        tasks=[
            Task(
                task_id="install_pytest",
                description="Install pytest framework",
                phase=Phase.TESTING,
                estimated_minutes=5,
                completed=True
            )
        ],
        progress=0.3,
        git_commit_sha="abc123"
    )

    manager.save(checkpoint)

**Validating Readiness Gates:**

.. code-block:: python

    from brownfield.orchestrator.gate_validator import GateValidator
    from brownfield.models.state import BrownfieldState

    validator = GateValidator(state)
    results = validator.validate_all_gates()

    for result in results:
        status = "✅" if result.passed else "❌"
        print(f"{status} {result.gate.name}: {result.message}")
