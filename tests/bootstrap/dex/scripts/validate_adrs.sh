#!/usr/bin/env bash
# validate_adrs.sh
# Checks two things:
#   1. No gaps in ADR number sequence in docs/architecture/
#   2. Every ADR file is referenced in spec/architecture.md, and vice-versa
# Usage: bash scripts/validate_adrs.sh [root-dir]
# Exits 0 on pass, 1 on any violation.

set -euo pipefail

ROOT_DIR="${1:-.}"
ADR_DIR="$ROOT_DIR/docs/architecture"
SPEC_FILE="$ROOT_DIR/spec/architecture.md"

fail_count=0

log_error() {
  echo "ERROR: $1"
  fail_count=$((fail_count + 1))
}

if [[ ! -d "$ADR_DIR" ]]; then
  log_error "docs/architecture/ directory not found"
  echo "Validation failed with $fail_count error(s)."
  exit 1
fi

if [[ ! -f "$SPEC_FILE" ]]; then
  log_error "spec/architecture.md not found"
  echo "Validation failed with $fail_count error(s)."
  exit 1
fi

# --- 1. Collect ADR files and check sequence for gaps ---

nums_file="$(mktemp)"
files_file="$(mktemp)"
trap 'rm -f "$nums_file" "$files_file"' EXIT

for f in "$ADR_DIR"/ADR-[0-9][0-9][0-9][0-9]-*.md; do
  [[ -e "$f" ]] || continue
  base="$(basename "$f")"
  echo "$base" >> "$files_file"
  # extract the 4-digit number, strip leading zeros for arithmetic
  num="${base#ADR-}"
  num="${num%%-*}"
  echo "$((10#$num))" >> "$nums_file"
done

if [[ ! -s "$nums_file" ]]; then
  log_error "No ADR files found in $ADR_DIR (expected ADR-NNNN-*.md)"
  echo "Validation failed with $fail_count error(s)."
  exit 1
fi

# Sort numerically and check for gaps
prev=0
while IFS= read -r n; do
  expected=$((prev + 1))
  if [[ "$n" -ne "$expected" ]]; then
    printf -v padded '%04d' "$((prev + 1))"
    log_error "ADR sequence gap: ADR-${padded}-*.md is missing (have ADR-$(printf '%04d' "$((prev))") and ADR-$(printf '%04d' "$n"))"
  fi
  prev="$n"
done < <(sort -n "$nums_file")

# --- 2. Cross-check ADR files vs spec/architecture.md table ---

spec_refs_file="$(mktemp)"
trap 'rm -f "$nums_file" "$files_file" "$spec_refs_file"' EXIT

# Extract ADR filenames referenced in the spec (links of the form ADR-NNNN-*.md)
grep -oE 'ADR-[0-9]{4}-[A-Za-z0-9_-]+\.md' "$SPEC_FILE" | sort -u > "$spec_refs_file" || true

while IFS= read -r base; do
  if ! grep -qF "$base" "$spec_refs_file"; then
    log_error "$base exists in docs/architecture/ but is not referenced in spec/architecture.md"
  fi
done < <(sort -u "$files_file")

while IFS= read -r ref; do
  if [[ ! -f "$ADR_DIR/$ref" ]]; then
    log_error "spec/architecture.md references $ref but $ADR_DIR/$ref does not exist"
  fi
done < "$spec_refs_file"

# --- Result ---

if [[ $fail_count -gt 0 ]]; then
  echo "ADR validation failed with $fail_count error(s)."
  exit 1
fi

echo "ADR validation passed: $(wc -l < "$files_file" | tr -d ' ') ADR(s), no gaps, spec table in sync."
