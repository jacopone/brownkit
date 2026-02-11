"""Structure remediation - plan generation for manual refactoring with IDE tools."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from brownfield.models.assessment import LanguageDetection
from brownfield.plugins.registry import get_handler
from brownfield.utils.output_formatter import OutputFormatter


@dataclass
class FileMoveOperation:
    """Represents a single file move operation."""

    source: Path
    destination: Path
    reason: str
    import_references: int = 0  # Number of files that import this module


@dataclass
class StructureAnalysis:
    """Analysis of current project structure."""

    missing_directories: list[Path]
    files_to_move: list[FileMoveOperation]
    config_files_to_create: dict[str, str]  # filename -> content
    stray_files_count: int
    compliant: bool


class StructurePlanGenerator:
    """Generates refactoring plans for reorganizing project structure."""

    def __init__(self, project_root: Path, language_detection: LanguageDetection):
        """Initialize plan generator."""
        self.project_root = project_root
        self.language_detection = language_detection
        self.formatter = OutputFormatter()
        self.handler = get_handler(language_detection.language)

    def analyze_structure(self) -> StructureAnalysis:
        """Analyze current structure and identify issues."""
        self.formatter.info("Analyzing project structure...")

        # Get standard structure from language handler
        standard_structure = self.handler.get_standard_structure()

        # Find missing directories
        missing_dirs = []
        for dir_name in standard_structure:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_path)

        # Identify files that need to be moved
        files_to_move = self._identify_files_to_move(standard_structure)

        # Identify configuration files to create
        config_files = self._identify_missing_configs()

        # Check if structure is compliant
        compliant = len(missing_dirs) == 0 and len(files_to_move) == 0

        return StructureAnalysis(
            missing_directories=missing_dirs,
            files_to_move=files_to_move,
            config_files_to_create=config_files,
            stray_files_count=len(files_to_move),
            compliant=compliant,
        )

    def _identify_files_to_move(self, standard_structure: dict[str, list[str]]) -> list[FileMoveOperation]:
        """Identify which files should be moved."""
        files_to_move = []

        if self.language_detection.language == "python":
            files_to_move.extend(self._identify_python_moves(standard_structure))
        elif self.language_detection.language == "javascript":
            files_to_move.extend(self._identify_javascript_moves(standard_structure))
        elif self.language_detection.language == "go":
            files_to_move.extend(self._identify_go_moves(standard_structure))
        # Rust typically follows standard structure from cargo init

        return files_to_move

    def _identify_python_moves(self, standard_structure: dict[str, list[str]]) -> list[FileMoveOperation]:
        """Identify Python files that need to be moved."""
        moves = []

        # Find .py files in root directory
        for py_file in self.project_root.glob("*.py"):
            # Skip special files
            if py_file.name in ["setup.py", "conftest.py", "manage.py", "__init__.py"]:
                continue

            # Determine destination
            project_name = self._get_project_name() or "project"
            dest = self.project_root / "src" / project_name / py_file.name

            # Count import references (simplified)
            import_count = self._count_import_references(py_file)

            moves.append(
                FileMoveOperation(
                    source=py_file,
                    destination=dest,
                    reason=f"Move to standard src/{project_name}/ structure (PEP 518)",
                    import_references=import_count,
                )
            )

        return moves

    def _identify_javascript_moves(self, standard_structure: dict[str, list[str]]) -> list[FileMoveOperation]:
        """Identify JavaScript files that need to be moved."""
        moves = []

        for js_file in self.project_root.glob("*.js"):
            # Skip config files
            if js_file.name.endswith("config.js") or js_file.name.endswith(".config.js"):
                continue

            dest = self.project_root / "src" / js_file.name
            import_count = self._count_import_references(js_file)

            moves.append(
                FileMoveOperation(
                    source=js_file,
                    destination=dest,
                    reason="Move to standard src/ structure",
                    import_references=import_count,
                )
            )

        return moves

    def _identify_go_moves(self, standard_structure: dict[str, list[str]]) -> list[FileMoveOperation]:
        """Identify Go files that need to be moved."""
        moves = []

        for go_file in self.project_root.glob("*.go"):
            if go_file.name == "main.go":
                dest = self.project_root / "cmd" / "app" / go_file.name
                reason = "Move main.go to cmd/app/ (Go conventions)"
            else:
                dest = self.project_root / "pkg" / go_file.stem / go_file.name
                reason = "Move to pkg/ structure (Go conventions)"

            import_count = self._count_import_references(go_file)

            moves.append(
                FileMoveOperation(
                    source=go_file,
                    destination=dest,
                    reason=reason,
                    import_references=import_count,
                )
            )

        return moves

    def _count_import_references(self, file_path: Path) -> int:
        """Count how many files import this module (simplified)."""
        module_name = file_path.stem
        count = 0

        # Search for imports of this module
        if self.language_detection.language == "python":
            pattern = "**/*.py"
        elif self.language_detection.language == "javascript":
            pattern = "**/*.js"
        elif self.language_detection.language == "go":
            pattern = "**/*.go"
        else:
            return 0

        for source_file in self.project_root.rglob(pattern):
            if source_file == file_path:
                continue

            try:
                content = source_file.read_text(encoding="utf-8")
                if module_name in content:
                    count += 1
            except (UnicodeDecodeError, PermissionError):
                pass

        return count

    def _identify_missing_configs(self) -> dict[str, str]:
        """Identify configuration files that should be created."""
        configs = {}

        if self.language_detection.language == "python":
            pyproject_path = self.project_root / "pyproject.toml"
            if not pyproject_path.exists():
                project_name = self._get_project_name() or "project"
                configs["pyproject.toml"] = self._generate_python_pyproject(project_name)

        return configs

    def _get_project_name(self) -> str | None:
        """Extract project name from existing configuration or directory name."""
        # Try pyproject.toml
        pyproject_path = self.project_root / "pyproject.toml"
        if pyproject_path.exists():
            try:
                content = pyproject_path.read_text(encoding="utf-8")
                for line in content.split("\n"):
                    if line.strip().startswith("name"):
                        parts = line.split("=")
                        if len(parts) > 1:
                            return parts[1].strip().strip('"').strip("'")
            except Exception:
                pass

        # Try package.json
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                import json

                data = json.loads(package_json.read_text(encoding="utf-8"))
                return data.get("name")
            except Exception:
                pass

        # Fallback to directory name
        return self.project_root.name

    def _generate_python_pyproject(self, project_name: str) -> str:
        """Generate basic pyproject.toml content."""
        return f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "Refactored brownfield project"
requires-python = ">=3.8"

[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"
"""

    def generate_markdown_plan(self, analysis: StructureAnalysis) -> str:
        """Generate detailed markdown refactoring plan."""
        project_name = self._get_project_name() or "project"
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        plan = f"""# Structure Refactoring Plan

**Generated**: {timestamp}
**Language**: {self.language_detection.language}
**Project**: {project_name}

## Overview

"""

        if analysis.compliant:
            plan += "✅ Project structure already follows ecosystem conventions!\n\n"
            plan += "No refactoring needed.\n"
            return plan

        plan += f"""Moving {len(analysis.files_to_move)} files to standard {self.language_detection.language} structure.

⚠️  **IMPORTANT**: Use your IDE's refactoring tools to ensure imports are updated correctly!

## Step 1: Create Directories

"""

        for directory in analysis.missing_directories:
            rel_path = directory.relative_to(self.project_root)
            plan += f"- [ ] Create `{rel_path}/`\n"

        plan += f"""
```bash
# Create all directories at once:
mkdir -p {" ".join(str(d.relative_to(self.project_root)) for d in analysis.missing_directories)}
```

## Step 2: Move Files (Use IDE Refactoring!)

### ⚠️ CRITICAL: Use IDE Refactoring for Correct Import Updates

BrownKit does NOT move files automatically to avoid breaking your code with
naive import updates. Your IDE has proper AST parsing and will update imports correctly.

"""

        if self.language_detection.language == "python":
            plan += """**PyCharm Users:**
1. Right-click file → **Refactor** → **Move File**
2. Select destination directory (e.g., `src/{project}`)
3. ✅ Enable "**Search for references**" (updates imports automatically)
4. Review changes in diff view
5. Click "Refactor" to apply

**VSCode Users:**
1. Install "**Python Refactor**" extension (if not installed)
2. Drag file to destination in Explorer pane
3. When prompted, click "**Update imports**"
4. Review changes
5. Save all modified files

**Vim/Emacs/Other:**
- Use LSP refactoring commands if available
- OR use shell script below + manual import fixes

"""
        elif self.language_detection.language == "javascript":
            plan += """**VSCode Users:**
1. Drag file to `src/` in Explorer
2. Confirm "**Update imports**" prompt
3. Review and save changes

**WebStorm/IntelliJ Users:**
1. Right-click file → **Refactor** → **Move**
2. Select `src/` as destination
3. Enable "Search for references"
4. Apply changes

"""

        plan += "### Files to Move:\n\n"

        for move_op in analysis.files_to_move:
            rel_dest = move_op.destination.relative_to(self.project_root)
            ref_note = f" (imported in {move_op.import_references} files)" if move_op.import_references > 0 else ""
            plan += f"- [ ] `{move_op.source.name}` → `{rel_dest}`{ref_note}\n"
            plan += f"     *Reason*: {move_op.reason}\n"

        plan += "\n## Step 3: Configuration Files\n\n"

        if analysis.config_files_to_create:
            for filename, _content in analysis.config_files_to_create.items():
                plan += f"- [ ] Create `{filename}`\n"
            plan += "\n"
        else:
            plan += "No configuration files need to be created.\n\n"

        # Add package __init__.py for Python
        if self.language_detection.language == "python" and analysis.files_to_move:
            plan += f"""- [ ] Create `src/{project_name}/__init__.py`

```python
# src/{project_name}/__init__.py
\"\"\"{project_name} package.\"\"\"

__version__ = "0.1.0"
```

"""

        plan += """## Step 4: Verify Structure

After completing the manual refactoring:

```bash
brownfield structure --verify
```

This will check:
- ✓ Directory structure compliance
- ✓ Build integrity (no syntax errors)
- ✓ Import integrity (all imports resolve)
- ✓ No stray files in root

## Alternative: Shell Script (Advanced)

⚠️  **WARNING**: This script only moves files. It does NOT update imports!

You will need to manually fix all import statements after running this.

See: `.specify/memory/structure-moves.sh`

Only use this if you're comfortable manually updating imports or using find-replace.

## Need Help?

- **Import errors after moving?** Use IDE's "Optimize Imports" or "Fix All" features
- **Build failures?** Check that all import paths match new file locations
- **Circular dependencies?** Review import structure and refactor if needed

## Next Steps

1. ✅ Complete file moves using IDE refactoring
2. ✅ Verify all imports work: `brownfield structure --verify`
3. ✅ Commit changes: `git add . && git commit -m "refactor: reorganize project structure"`
4. ✅ Continue to testing phase: `brownfield testing`
"""

        return plan

    def generate_shell_script(self, analysis: StructureAnalysis) -> str:
        """Generate shell script for file moves only (no import updates)."""
        script = """#!/bin/bash
# Structure Refactoring Script
# Generated by BrownKit
#
# ⚠️  WARNING: This script only moves files!
# ⚠️  You MUST update imports manually after running this!
#
# Recommended: Use IDE refactoring instead of this script.

set -e  # Exit on error

echo "🏗️  Moving files to standard structure..."
echo ""
echo "⚠️  WARNING: Imports will NOT be updated automatically!"
echo "⚠️  You must fix import statements manually after this script completes."
echo ""
read -p "Continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

"""

        # Create directories
        if analysis.missing_directories:
            script += "\n# Create missing directories\n"
            for directory in analysis.missing_directories:
                rel_path = directory.relative_to(self.project_root)
                script += f'echo "Creating {rel_path}/..."\n'
                script += f"mkdir -p {rel_path}\n"

        # Move files
        if analysis.files_to_move:
            script += "\n# Move files\n"
            for i, move_op in enumerate(analysis.files_to_move, 1):
                rel_dest = move_op.destination.relative_to(self.project_root)
                script += f'\necho "[{i}/{len(analysis.files_to_move)}] Moving {move_op.source.name} → {rel_dest}..."\n'
                script += f"mkdir -p {rel_dest.parent}\n"
                script += f"mv {move_op.source.name} {rel_dest}\n"

        # Create __init__.py for Python packages
        if self.language_detection.language == "python" and analysis.files_to_move:
            project_name = self._get_project_name() or "project"
            script += "\n# Create package __init__.py\n"
            script += f'echo "Creating src/{project_name}/__init__.py..."\n'
            script += f'echo \'"""{project_name} package."""\' > src/{project_name}/__init__.py\n'

        script += """
echo ""
echo "✓ File moves complete!"
echo ""
echo "⚠️  IMPORTANT: You must now update import statements manually!"
echo "   Or use your IDE's refactoring tools to fix imports."
echo ""
echo "Verify structure after fixing imports:"
echo "  brownfield structure --verify"
"""

        return script
