#!/usr/bin/env bash
# brownfield-common.sh - Shared utilities for BrownKit bash scripts
#
# This file contains reusable functions for all brownfield-*.sh scripts.
# Pattern follows research.md findings for JSON generation, directory management,
# template rendering, and checkpoint validation.

set -euo pipefail

# Color output for terminal display
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Error handling
error() {
  echo -e "${RED}Error: $*${NC}" >&2
  exit 1
}

warn() {
  echo -e "${YELLOW}Warning: $*${NC}" >&2
}

info() {
  echo -e "${GREEN}$*${NC}" >&2
}

# Get next brownfield project number
# Returns: Zero-padded 3-digit number (e.g., "001", "002")
# Usage: next_num=$(get_next_brownfield_number)
get_next_brownfield_number() {
  local brownfield_dir="${1:-.specify/brownfield}"
  local max_num=0

  # Find highest numbered directory
  if [ -d "$brownfield_dir" ]; then
    while IFS= read -r dir; do
      local basename_dir
      basename_dir=$(basename "$dir")

      # Extract number from directory name (e.g., "001-project" -> "001")
      if [[ $basename_dir =~ ^([0-9]{3})- ]]; then
        local num="${BASH_REMATCH[1]}"
        # Remove leading zeros for arithmetic
        num=$((10#$num))
        if ((num > max_num)); then
          max_num=$num
        fi
      fi
    done < <(find "$brownfield_dir" -mindepth 1 -maxdepth 1 -type d 2>/dev/null || true)
  fi

  # Next number with leading zeros
  printf "%03d" $((max_num + 1))
}

# Render markdown template with variable substitution
# Usage: render_template template_file output_file VAR1=value1 VAR2=value2 ...
render_template() {
  local template_file="$1"
  local output_file="$2"
  shift 2

  [ -f "$template_file" ] || error "Template file not found: $template_file"

  # Read template content
  local template_content
  template_content=$(<"$template_file")

  # Substitute {{VAR}} placeholders with values
  for arg in "$@"; do
    if [[ $arg =~ ^([A-Z_]+)=(.*)$ ]]; then
      local var_name="${BASH_REMATCH[1]}"
      local var_value="${BASH_REMATCH[2]}"

      # Safe substitution using parameter expansion
      template_content="${template_content//\{\{${var_name}\}\}/${var_value}}"
    fi
  done

  # Write output
  echo "$template_content" > "$output_file"
}

# Validate Spec-Kit installation
# Returns: 0 if installed, 1 if not
# Usage: validate_speckit_installed || error "Spec-Kit not installed"
validate_speckit_installed() {
  if [ ! -d ".specify" ]; then
    return 1
  fi

  if [ ! -f ".specify/memory/constitution.md" ]; then
    return 1
  fi

  return 0
}

# Run quality tool and parse JSON output
# Usage: run_quality_tool "lizard" "src/" "--json" "/tmp/output.json"
# Returns: Path to JSON output file
run_quality_tool() {
  local tool="$1"
  local target="$2"
  local flags="$3"
  local output_file="$4"

  # Check if tool is available
  if ! command -v "$tool" &>/dev/null; then
    warn "$tool not found, skipping analysis"
    echo "{}" > "$output_file"
    return 1
  fi

  # Run tool and capture output
  if $tool $target $flags > "$output_file" 2>/dev/null; then
    return 0
  else
    warn "$tool execution failed"
    echo "{}" > "$output_file"
    return 1
  fi
}

# Parse JSON value using jq
# Usage: value=$(parse_json_value "/path/to/file.json" ".key.subkey")
parse_json_value() {
  local json_file="$1"
  local jq_path="$2"
  local default="${3:-null}"

  if [ ! -f "$json_file" ]; then
    echo "$default"
    return
  fi

  jq -r "$jq_path // $default" "$json_file" 2>/dev/null || echo "$default"
}

# Create directory if it doesn't exist
ensure_dir() {
  local dir="$1"
  mkdir -p "$dir"
}

# Check if git repository has uncommitted changes
has_uncommitted_changes() {
  if [ ! -d .git ]; then
    return 1
  fi

  if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    return 0  # Has changes
  fi

  return 1  # Clean
}

# Get current timestamp in ISO 8601 format
timestamp() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# Validate JSON file against schema (requires jq)
validate_json() {
  local json_file="$1"

  if [ ! -f "$json_file" ]; then
    return 1
  fi

  if jq empty "$json_file" 2>/dev/null; then
    return 0
  else
    return 1
  fi
}

# Export functions for use in other scripts
export -f error
export -f warn
export -f info
export -f get_next_brownfield_number
export -f render_template
export -f validate_speckit_installed
export -f run_quality_tool
export -f parse_json_value
export -f ensure_dir
export -f has_uncommitted_changes
export -f timestamp
export -f validate_json
