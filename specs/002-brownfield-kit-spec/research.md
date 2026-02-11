---
status: active
created: 2025-10-20
updated: 2025-10-20
type: research
lifecycle: ephemeral
---

# Phase 0: Research for Brownfield Kit Bash Implementation

This document contains research findings for implementing the Brownfield Kit bash-based assessment tool.

## Research Tasks

### Task A: Bash JSON Generation Patterns

**Goal**: Identify reliable patterns for generating valid JSON from bash scripts

**Research Questions**:
- What are the most robust methods for generating JSON in bash?
- How to handle escaping of special characters (quotes, newlines, etc.)?
- What tools/approaches work best: `jq`, `printf`, heredocs?
- How to build complex nested JSON structures?

**Findings**:

#### Method 1: Using `jq` for JSON Construction
```bash
# Recommended approach - safest and most reliable
jq -n \
  --arg name "$project_name" \
  --argjson files "$file_count" \
  --arg path "$project_path" \
  '{
    name: $name,
    files: $files,
    path: $path,
    timestamp: now | todate
  }'
```

**Pros**:
- Automatic escaping of special characters
- Type safety (--argjson for numbers/booleans)
- Built-in functions (now, todate, etc.)
- Validates JSON structure

**Cons**:
- Requires jq to be installed
- Learning curve for jq syntax

#### Method 2: Using `printf` with Manual Escaping
```bash
# Less safe - requires careful escaping
printf '{"name":"%s","files":%d,"path":"%s"}\n' \
  "${name//\"/\\\"}" \
  "$file_count" \
  "${path//\"/\\\"}"
```

**Pros**:
- No external dependencies
- Simple for flat structures

**Cons**:
- Manual escaping required
- Error-prone for complex structures
- No validation

#### Method 3: Heredoc with Variable Interpolation
```bash
# Avoid - very fragile
cat <<EOF
{
  "name": "$name",
  "files": $file_count
}
EOF
```

**Cons**:
- No automatic escaping
- Vulnerable to injection
- Easy to create invalid JSON

**Recommendation**: Use `jq` for all JSON generation. It's available in the NixOS environment and provides the best balance of safety and maintainability.

---

### Task B: Quality Tool Integration (lizard, pytest, bandit CLI flags)

**Goal**: Understand CLI interfaces for quality tools to integrate them into assessment scripts

**Research Questions**:
- What CLI flags does each tool support?
- What output formats are available (JSON, XML, etc.)?
- How to set thresholds and fail conditions?
- What metrics does each tool provide?

**Findings**:

#### Lizard (Code Complexity Analysis)
```bash
# Basic usage with JSON output
lizard --json /path/to/code

# Output structure:
# {
#   "ccn": 5,              # Cyclomatic complexity
#   "function_name": "foo",
#   "file": "module.py",
#   "line_number": 10,
#   "nloc": 25,            # Lines of code
#   "token_count": 120
# }

# Set complexity threshold
lizard --CCN 10 /path/to/code  # Warn if CCN > 10

# Exclude patterns
lizard --exclude "*/tests/*" --exclude "*/migrations/*"

# Multiple languages
lizard --languages python,javascript
```

**Available Flags**:
- `--json`: JSON output format
- `--CCN N`: Cyclomatic complexity threshold
- `--length N`: Function length threshold
- `--arguments N`: Parameter count threshold
- `--exclude PATTERN`: Exclude files/directories
- `--verbose`: Detailed output

#### Pytest (Test Execution)
```bash
# Run with JSON report
pytest --json-report --json-report-file=report.json

# Coverage with JSON
pytest --cov=src --cov-report=json

# Output structure (pytest-json-report plugin):
# {
#   "summary": {
#     "total": 50,
#     "passed": 45,
#     "failed": 3,
#     "skipped": 2
#   },
#   "tests": [...]
# }

# Set exit codes
pytest --maxfail=1  # Stop after first failure

# Quiet/verbose modes
pytest -q  # Quiet
pytest -v  # Verbose
```

**Available Flags**:
- `--json-report`: Generate JSON report (requires plugin)
- `--cov=PATH`: Coverage analysis
- `--cov-report=json`: JSON coverage report
- `--maxfail=N`: Stop after N failures
- `-k EXPRESSION`: Run tests matching expression
- `--tb=short`: Shorter traceback format

#### Bandit (Security Analysis)
```bash
# JSON output
bandit -r /path/to/code -f json -o bandit-report.json

# Output structure:
# {
#   "metrics": {
#     "high": 2,
#     "medium": 5,
#     "low": 10
#   },
#   "results": [
#     {
#       "issue_severity": "HIGH",
#       "issue_confidence": "HIGH",
#       "issue_text": "Use of exec detected",
#       "line_number": 42,
#       "filename": "script.py"
#     }
#   ]
# }

# Set severity threshold
bandit -r . -ll  # Only low severity and above

# Exclude paths
bandit -r . --exclude /tests/,/venv/

# Specific tests
bandit -r . --skip B101,B601
```

**Available Flags**:
- `-f json`: JSON output format
- `-o FILE`: Output file
- `-r PATH`: Recursive scan
- `-ll`, `-l`, `-m`, `-h`: Severity levels (low, medium, high)
- `--exclude PATH`: Exclude directories
- `--skip TEST_ID`: Skip specific tests

**Integration Pattern**:
```bash
run_quality_checks() {
  local project_path="$1"

  # Combine all tool outputs into single JSON
  jq -n \
    --argjson lizard "$(lizard --json "$project_path" 2>/dev/null || echo '{}')" \
    --argjson bandit "$(bandit -r "$project_path" -f json 2>/dev/null || echo '{}')" \
    --argjson pytest "$(pytest --json-report --json-report-file=/dev/stdout 2>/dev/null || echo '{}')" \
    '{
      complexity: $lizard,
      security: $bandit,
      tests: $pytest,
      timestamp: now | todate
    }'
}
```

---

### Task C: Numbered Directory Management

**Goal**: Establish patterns for creating and managing numbered spec directories (001-, 002-, etc.)

**Research Questions**:
- How to find the next available number?
- How to validate directory naming conventions?
- How to list directories in order?
- What metadata should be tracked?

**Findings**:

#### Pattern: Finding Next Number
```bash
get_next_spec_number() {
  local specs_dir="${1:-specs}"

  # Find highest numbered directory
  local max_num=0

  while IFS= read -r dir; do
    # Extract number from directory name (e.g., "001-feature" -> "001")
    if [[ $(basename "$dir") =~ ^([0-9]{3})- ]]; then
      local num="${BASH_REMATCH[1]}"
      # Remove leading zeros for arithmetic
      num=$((10#$num))
      if ((num > max_num)); then
        max_num=$num
      fi
    fi
  done < <(fd --type d --max-depth 1 . "$specs_dir")

  # Next number with leading zeros
  printf "%03d" $((max_num + 1))
}

# Usage
next_num=$(get_next_spec_number)
echo "Next spec: $next_num"  # Output: 003
```

#### Pattern: Creating Numbered Directory
```bash
create_spec_directory() {
  local spec_name="$1"
  local specs_dir="${2:-specs}"

  # Get next number
  local num=$(get_next_spec_number "$specs_dir")

  # Sanitize name (lowercase, hyphens)
  local safe_name=$(echo "$spec_name" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')

  # Create directory
  local dir_name="${num}-${safe_name}"
  local full_path="${specs_dir}/${dir_name}"

  mkdir -p "$full_path"/{checklists,contracts}

  # Create metadata file
  cat > "$full_path/metadata.json" <<EOF
{
  "number": "$num",
  "name": "$spec_name",
  "slug": "$safe_name",
  "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "draft"
}
EOF

  echo "$full_path"
}

# Usage
new_spec=$(create_spec_directory "User Authentication Feature")
echo "Created: $new_spec"
```

#### Pattern: Listing Specs in Order
```bash
list_specs() {
  local specs_dir="${1:-specs}"

  # List directories, sort numerically
  fd --type d --max-depth 1 '^[0-9]{3}-' "$specs_dir" \
    | sort -V \
    | while read -r spec_dir; do
        local name=$(basename "$spec_dir")
        local status="unknown"

        # Read status from metadata if available
        if [ -f "$spec_dir/metadata.json" ]; then
          status=$(jq -r '.status // "unknown"' "$spec_dir/metadata.json")
        fi

        printf "%-40s %s\n" "$name" "$status"
      done
}

# Usage
list_specs
# Output:
# 001-brownkit-implementation       active
# 002-brownkit-spec                 draft
```

#### Pattern: Validating Directory Structure
```bash
validate_spec_directory() {
  local spec_dir="$1"
  local errors=()

  # Check naming convention
  if [[ ! $(basename "$spec_dir") =~ ^[0-9]{3}-[a-z0-9-]+$ ]]; then
    errors+=("Invalid directory name format")
  fi

  # Check required subdirectories
  for subdir in checklists contracts; do
    if [ ! -d "$spec_dir/$subdir" ]; then
      errors+=("Missing subdirectory: $subdir")
    fi
  done

  # Check metadata file
  if [ ! -f "$spec_dir/metadata.json" ]; then
    errors+=("Missing metadata.json")
  else
    # Validate JSON
    if ! jq empty "$spec_dir/metadata.json" 2>/dev/null; then
      errors+=("Invalid JSON in metadata.json")
    fi
  fi

  # Report results
  if [ ${#errors[@]} -eq 0 ]; then
    echo "✓ Valid spec directory"
    return 0
  else
    echo "✗ Validation errors:"
    printf "  - %s\n" "${errors[@]}"
    return 1
  fi
}
```

**Recommendation**: Use zero-padded 3-digit prefixes (001-, 002-) for sortability. Always include metadata.json for tracking status and creation date.

---

### Task D: Template Rendering in Bash

**Goal**: Identify patterns for generating files from templates with variable substitution

**Research Questions**:
- What are safe variable substitution methods?
- How to handle multi-line templates?
- How to avoid shell injection vulnerabilities?
- What about conditional sections in templates?

**Findings**:

#### Method 1: Heredoc with Variable Substitution
```bash
render_template_heredoc() {
  local project_name="$1"
  local author="$2"

  cat <<EOF
# ${project_name}

Author: ${author}
Created: $(date +%Y-%m-%d)

## Overview
This project provides...
EOF
}

# Usage
render_template_heredoc "My Project" "John Doe" > README.md
```

**Pros**:
- Simple and readable
- Direct variable interpolation
- No external dependencies

**Cons**:
- Variables are expanded immediately (potential injection)
- No conditional logic
- Hard to escape special characters

#### Method 2: External Template Files with envsubst
```bash
# template.md.tmpl
# Project: ${PROJECT_NAME}
# Author: ${AUTHOR}

render_template_envsubst() {
  local template_file="$1"
  local output_file="$2"

  # Export variables for envsubst
  export PROJECT_NAME="My Project"
  export AUTHOR="John Doe"
  export CREATED_DATE=$(date +%Y-%m-%d)

  envsubst < "$template_file" > "$output_file"

  # Clean up
  unset PROJECT_NAME AUTHOR CREATED_DATE
}

# Usage
render_template_envsubst "template.md.tmpl" "output.md"
```

**Pros**:
- Separates template from logic
- Only substitutes defined variables
- Standard tool (GNU gettext)

**Cons**:
- Requires envsubst
- Limited to simple variable substitution
- No conditional logic

#### Method 3: sed-based Substitution (Safer)
```bash
render_template_sed() {
  local template_file="$1"
  local output_file="$2"
  local project_name="$3"
  local author="$4"

  # Escape special characters for sed
  local safe_name=$(printf '%s' "$project_name" | sed 's/[[\.*^$/]/\\&/g')
  local safe_author=$(printf '%s' "$author" | sed 's/[[\.*^$/]/\\&/g')

  sed -e "s/{{PROJECT_NAME}}/$safe_name/g" \
      -e "s/{{AUTHOR}}/$safe_author/g" \
      -e "s/{{DATE}}/$(date +%Y-%m-%d)/g" \
      "$template_file" > "$output_file"
}

# Template file uses {{VAR}} syntax
# # Project: {{PROJECT_NAME}}
# Author: {{AUTHOR}}
# Created: {{DATE}}
```

**Pros**:
- Explicit placeholders ({{VAR}})
- Safer than direct interpolation
- Can escape special characters

**Cons**:
- Requires escaping
- Multiple sed commands needed
- No conditional logic

#### Method 4: Function-based Template Generation
```bash
generate_readme() {
  local project_name="$1"
  local has_tests="$2"  # boolean flag

  cat <<'EOF'
# ${project_name}

## Overview
This is the ${project_name} project.

EOF

  # Conditional section
  if [ "$has_tests" = "true" ]; then
    cat <<'EOF'
## Running Tests
```bash
pytest
```

EOF
  fi

  cat <<'EOF'
## License
MIT
EOF
}

# Evaluate the function to expand variables
eval "$(declare -f generate_readme)"
generate_readme "My Project" "true"
```

**Pros**:
- Supports conditional logic
- Clean function-based approach
- Can include complex logic

**Cons**:
- More complex for simple templates
- Need to be careful with quoting

#### Recommended Pattern for Brownfield Kit
```bash
# Template directory structure:
# templates/
#   spec.md.tmpl
#   quickstart.md.tmpl
#   data-model.md.tmpl

render_spec_template() {
  local template_name="$1"
  local output_path="$2"
  shift 2

  # Parse key=value arguments
  declare -A vars
  for arg in "$@"; do
    if [[ $arg =~ ^([A-Z_]+)=(.+)$ ]]; then
      vars["${BASH_REMATCH[1]}"]="${BASH_REMATCH[2]}"
    fi
  done

  # Read template and substitute
  local template_content
  template_content=$(<"templates/${template_name}.tmpl")

  # Use jq to safely build the substitution
  local json_vars=$(printf '%s\n' "${!vars[@]}" | jq -R . | jq -s 'map({key: ., value: ""}) | from_entries')

  # Substitute placeholders
  for key in "${!vars[@]}"; do
    local value="${vars[$key]}"
    # Safe substitution using parameter expansion
    template_content="${template_content//\{\{${key}\}\}/${value}}"
  done

  echo "$template_content" > "$output_path"
}

# Usage
render_spec_template "spec" "output/spec.md" \
  SPEC_NAME="Brownfield Kit" \
  SPEC_NUMBER="001" \
  AUTHOR="System" \
  DATE="$(date +%Y-%m-%d)"
```

**Recommendation**: Use heredocs for simple inline templates, and function-based generation with placeholders for complex templates that need conditional logic.

---

### Task E: Checkpoint Validation Pattern

**Goal**: Design a pattern for validating that prerequisites are met before proceeding with script phases

**Research Questions**:
- How to define checkpoints?
- How to validate prerequisites (files, tools, states)?
- How to report validation results?
- How to allow skipping checks in development?

**Findings**:

#### Pattern: Checkpoint Definition
```bash
# Define checkpoints as associative array
declare -A CHECKPOINTS=(
  ["git_repo"]="validate_git_repo"
  ["python_venv"]="validate_python_venv"
  ["config_file"]="validate_config_file"
  ["quality_tools"]="validate_quality_tools"
)

# Checkpoint order (for dependencies)
CHECKPOINT_ORDER=(
  "git_repo"
  "config_file"
  "quality_tools"
  "python_venv"
)
```

#### Pattern: Validation Functions
```bash
validate_git_repo() {
  if [ -d .git ]; then
    echo "✓ Git repository detected"
    return 0
  else
    echo "✗ Not a git repository"
    echo "  Run: git init"
    return 1
  fi
}

validate_python_venv() {
  if [ -n "$VIRTUAL_ENV" ] || [ -d .venv ]; then
    echo "✓ Python virtual environment detected"
    return 0
  else
    echo "✗ No virtual environment active"
    echo "  Run: python -m venv .venv && source .venv/bin/activate"
    return 1
  fi
}

validate_quality_tools() {
  local missing=()

  for tool in lizard pytest bandit; do
    if ! command -v "$tool" &>/dev/null; then
      missing+=("$tool")
    fi
  done

  if [ ${#missing[@]} -eq 0 ]; then
    echo "✓ All quality tools available"
    return 0
  else
    echo "✗ Missing quality tools: ${missing[*]}"
    echo "  Run: pip install lizard pytest bandit"
    return 1
  fi
}

validate_config_file() {
  local config_file=".brownfield/config.json"

  if [ ! -f "$config_file" ]; then
    echo "✗ Config file not found: $config_file"
    echo "  Run: brownfield init"
    return 1
  fi

  if ! jq empty "$config_file" 2>/dev/null; then
    echo "✗ Invalid JSON in config file"
    return 1
  fi

  echo "✓ Config file valid"
  return 0
}
```

#### Pattern: Checkpoint Execution
```bash
run_checkpoints() {
  local skip_checks="${SKIP_CHECKS:-false}"
  local failed_checks=()

  echo "=== Running Checkpoints ==="
  echo

  # Allow skipping in development
  if [ "$skip_checks" = "true" ]; then
    echo "⚠ Skipping checks (SKIP_CHECKS=true)"
    return 0
  fi

  # Run checkpoints in order
  for checkpoint_name in "${CHECKPOINT_ORDER[@]}"; do
    local validate_func="${CHECKPOINTS[$checkpoint_name]}"

    echo "Checkpoint: $checkpoint_name"

    if $validate_func; then
      echo
    else
      failed_checks+=("$checkpoint_name")
      echo
    fi
  done

  # Report results
  if [ ${#failed_checks[@]} -eq 0 ]; then
    echo "✓ All checkpoints passed"
    return 0
  else
    echo "✗ Failed checkpoints: ${failed_checks[*]}"
    echo
    echo "Fix the issues above or run with SKIP_CHECKS=true to bypass"
    return 1
  fi
}

# Usage in main script
main() {
  if ! run_checkpoints; then
    exit 1
  fi

  # Proceed with main logic
  echo "Starting assessment..."
}
```

#### Pattern: JSON Checkpoint Report
```bash
run_checkpoints_json() {
  local results=()

  for checkpoint_name in "${CHECKPOINT_ORDER[@]}"; do
    local validate_func="${CHECKPOINTS[$checkpoint_name]}"
    local output
    local exit_code

    # Capture output and exit code
    output=$($validate_func 2>&1)
    exit_code=$?

    # Build JSON entry
    results+=($(jq -n \
      --arg name "$checkpoint_name" \
      --argjson passed "$([ $exit_code -eq 0 ] && echo true || echo false)" \
      --arg output "$output" \
      '{
        name: $name,
        passed: $passed,
        output: $output,
        timestamp: now | todate
      }'
    ))
  done

  # Combine into single JSON array
  jq -n --argjson results "$(printf '%s\n' "${results[@]}" | jq -s .)" \
    '{
      checkpoints: $results,
      all_passed: ($results | map(.passed) | all)
    }'
}

# Usage
checkpoint_report=$(run_checkpoints_json)
echo "$checkpoint_report" > .brownfield/checkpoints.json

if [ "$(echo "$checkpoint_report" | jq -r .all_passed)" = "false" ]; then
  echo "Checkpoint validation failed"
  exit 1
fi
```

#### Pattern: Graceful Degradation
```bash
validate_optional_tool() {
  local tool_name="$1"
  local feature_name="$2"

  if command -v "$tool_name" &>/dev/null; then
    echo "✓ Optional tool available: $tool_name"
    return 0
  else
    echo "⚠ Optional tool missing: $tool_name"
    echo "  Feature '$feature_name' will be disabled"
    return 1
  fi
}

# Track optional features
declare -A FEATURES=(
  ["complexity_analysis"]="disabled"
  ["security_scan"]="disabled"
  ["coverage_report"]="disabled"
)

# Enable features based on available tools
if validate_optional_tool "lizard" "complexity analysis"; then
  FEATURES["complexity_analysis"]="enabled"
fi

if validate_optional_tool "bandit" "security scanning"; then
  FEATURES["security_scan"]="enabled"
fi

# Use feature flags in main logic
run_assessment() {
  if [ "${FEATURES[complexity_analysis]}" = "enabled" ]; then
    run_complexity_analysis
  else
    echo "Skipping complexity analysis (lizard not available)"
  fi
}
```

**Recommendation**: Use checkpoint validation at script start with clear error messages and remediation steps. Support `SKIP_CHECKS` environment variable for development. Generate JSON reports for programmatic validation.

---

## Summary and Recommendations

### Key Findings

1. **JSON Generation**: Use `jq` exclusively for JSON generation - it's safe, reliable, and available in the NixOS environment

2. **Quality Tools**: All three tools (lizard, pytest, bandit) support JSON output formats which can be easily combined using `jq`

3. **Directory Management**: Use zero-padded 3-digit prefixes with metadata.json files for tracking status and creation date

4. **Template Rendering**: Heredocs work well for inline templates; function-based generation with explicit placeholders ({{VAR}}) for complex templates

5. **Checkpoint Validation**: Implement ordered checkpoint system with clear error messages, remediation steps, and optional JSON reporting

### Implementation Priorities

**High Priority** (Phase 1):
- Implement jq-based JSON generation utilities
- Create checkpoint validation framework
- Set up numbered directory management functions

**Medium Priority** (Phase 2):
- Integrate quality tool wrappers with JSON output
- Create template rendering system for common files
- Add optional feature detection and graceful degradation

**Low Priority** (Phase 3):
- Advanced template conditionals
- Checkpoint report visualization
- Interactive checkpoint remediation

### Next Steps

1. Move to Phase 1: Design
2. Create data-model.md based on research findings
3. Create JSON schemas in contracts/ directory
4. Create quickstart.md with installation guide
5. Update agent context

---

## References

- jq Manual: https://stedolan.github.io/jq/manual/
- Lizard Documentation: https://github.com/terryyin/lizard
- Pytest JSON Report: https://github.com/numirias/pytest-json-report
- Bandit Documentation: https://bandit.readthedocs.io/
- Bash Best Practices: https://mywiki.wooledge.org/BashGuide
