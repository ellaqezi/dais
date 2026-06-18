#!/usr/bin/env bash
# validate_stubs.sh
# Checks that every ./tasks/task-NNN.md path referenced in dex/main.py
# actually exists on disk.
# Usage: bash scripts/validate_stubs.sh [root-dir]
# Exits 0 on pass, 1 on any missing file.

set -euo pipefail

ROOT_DIR="${1:-.}"
MAIN_PY="$ROOT_DIR/dex/main.py"

fail_count=0

log_error() {
  echo "ERROR: $1"
  fail_count=$((fail_count + 1))
}

if [[ ! -f "$MAIN_PY" ]]; then
  log_error "$MAIN_PY not found"
  echo "Validation failed with $fail_count error(s)."
  exit 1
fi

# Extract every ./tasks/task-NNN.md reference from main.py
refs_file="$(mktemp)"
trap 'rm -f "$refs_file"' EXIT

grep -oE '\./tasks/task-[0-9]{3}\.md' "$MAIN_PY" | sort -u > "$refs_file" || true

if [[ ! -s "$refs_file" ]]; then
  echo "Stub reference check: no task references found in $MAIN_PY — skipping."
  exit 0
fi

checked=0
while IFS= read -r ref; do
  # ref is like ./tasks/task-004.md; resolve relative to ROOT_DIR
  full_path="$ROOT_DIR/${ref#./}"
  if [[ ! -f "$full_path" ]]; then
    log_error "dex/main.py references '$ref' but $full_path does not exist"
  fi
  checked=$((checked + 1))
done < "$refs_file"

if [[ $fail_count -gt 0 ]]; then
  echo "Stub reference validation failed with $fail_count error(s)."
  exit 1
fi

echo "Stub reference validation passed: $checked task reference(s) verified."
