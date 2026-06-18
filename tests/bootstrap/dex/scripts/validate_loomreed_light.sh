#!/usr/bin/env bash
# validate_loomreed_light.sh
# Validates loom-reed-light task schema: sections, status vocabulary, S/M sizing, sync.
# Usage: bash scripts/validate_loomreed_light.sh [root-dir]
# Exits 0 on pass, 1 on any violation.

set -euo pipefail

ROOT_DIR="${1:-.}"
TASKS_DIR="$ROOT_DIR/tasks"
TASK_LIST="$TASKS_DIR/task-list.md"

VALID_STATUSES="todo needs-refine ready in-progress blocked in-review done deferred decomposed canceled"
REQUIRED_SECTIONS=(
  "Summary"
  "Spec Links"
  "Acceptance Criteria"
  "Impact"
  "Size"
  "Status"
  "Test Plan"
  "Notes"
)

fail_count=0

log_error() {
  echo "ERROR: $1"
  fail_count=$((fail_count + 1))
}

trim() {
  local s="$1"
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s' "$s"
}

contains_status() {
  local needle="$1"
  for s in $VALID_STATUSES; do
    if [[ "$needle" == "$s" ]]; then
      return 0
    fi
  done
  return 1
}

if [[ ! -d "$TASKS_DIR" ]]; then
  echo "No tasks/ directory found. Skipping Loom-Reed-Light validation."
  exit 0
fi

if [[ ! -f "$TASK_LIST" ]]; then
  log_error "Missing tasks/task-list.md"
  echo "Validation failed with $fail_count error(s)."
  exit 1
fi

list_ids_file="$(mktemp)"
file_ids_file="$(mktemp)"
trap 'rm -f "$list_ids_file" "$file_ids_file"' EXIT

line_no=0
while IFS= read -r line; do
  line_no=$((line_no + 1))

  if [[ "$line" =~ ^\|[[:space:]]*task-[0-9]{3}[[:space:]]*\| ]]; then
    IFS='|' read -r _ c1 c2 c3 c4 _ <<< "$line"

    id="$(trim "$c1")"
    title="$(trim "$c2")"
    status="$(trim "$c3")"
    size="$(trim "$c4")"

    echo "$id" >> "$list_ids_file"

    if [[ -z "$title" ]]; then
      log_error "task-list.md:$line_no has empty Title for $id"
    fi

    if ! contains_status "$status"; then
      log_error "task-list.md:$line_no has invalid Status '$status' for $id"
    fi

    if [[ "$size" != "S" && "$size" != "M" ]]; then
      log_error "task-list.md:$line_no has invalid Size '$size' for $id (expected S or M)"
    fi
  fi
done < "$TASK_LIST"

if [[ ! -s "$list_ids_file" ]]; then
  log_error "No task rows found in tasks/task-list.md (expected rows like '| task-001 | ... |')"
fi

for f in "$TASKS_DIR"/task-[0-9][0-9][0-9].md; do
  if [[ -e "$f" ]]; then
    base="$(basename "$f" .md)"
    echo "$base" >> "$file_ids_file"

    for section in "${REQUIRED_SECTIONS[@]}"; do
      if ! grep -Eiq "^###[[:space:]]+$section|^##[[:space:]]+$section" "$f"; then
        log_error "$f is missing section heading '$section'"
      fi
    done
  fi
done

if [[ ! -s "$file_ids_file" ]]; then
  log_error "No detail files found in tasks/ (expected task-<id>.md files)"
fi

sort -u "$list_ids_file" -o "$list_ids_file"
sort -u "$file_ids_file" -o "$file_ids_file"

while IFS= read -r id; do
  if ! grep -qx "$id" "$file_ids_file"; then
    log_error "Task list contains $id but $TASKS_DIR/$id.md is missing"
  fi
done < "$list_ids_file"

while IFS= read -r id; do
  if ! grep -qx "$id" "$list_ids_file"; then
    log_error "Task file exists for $id but it is missing from tasks/task-list.md"
  fi
done < "$file_ids_file"

if [[ $fail_count -gt 0 ]]; then
  echo "Validation failed with $fail_count error(s)."
  exit 1
fi

echo "Loom-Reed-Light validation passed."
