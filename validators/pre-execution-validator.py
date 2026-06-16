#!/usr/bin/env python3
"""
DAIS Pre-Execution Validator
Validates agent prompt files (.md) before they are used in the pipeline.
Principle D5: quality is tested, not self-certified.

Exit code 0 = valid.   Pipeline proceeds.
Exit code 1 = invalid. Pipeline is blocked.

Usage:
    python validators/pre-execution-validator.py agents/phase-1/derive-agent.md
    python validators/pre-execution-validator.py agents/phase-1/derive-agent.md system.config.yaml
"""

import re
import sys
import yaml
from pathlib import Path

# ── Structural requirements (D5) ──────────────────────────────────────────────

REQUIRED_SECTIONS = [
    (r"^## Role", "## Role"),
    (r"^## Objective", "## Objective"),
    (r"^## Community", "## Community"),
    (r"^## Key Points", "## Key Points"),
    (r"^## Shape", "## Shape"),
    (r"^## Constraints", "## Constraints"),
]

PLACEHOLDER_PATTERNS = [
    r"<TODO>",
    r"\bTBD\b",
    r"\[fill in\]",
    r"\bPLACEHOLDER\b",
]

# Refusal must include both a refusal verb and a scope/boundary clause
REFUSAL_PATTERN = re.compile(
    r"\b(refuse|will not|cannot)\b.{0,60}\b(scope|outside|redirect|not handle|beyond)\b",
    re.IGNORECASE | re.DOTALL,
)

# Few-shot example: must have both **Input**: and **Output**: markers
FEWSHOT_INPUT = re.compile(r"\*\*Input\*\*\s*:", re.IGNORECASE)
FEWSHOT_OUTPUT = re.compile(r"\*\*Output\*\*\s*:", re.IGNORECASE)

FRONTMATTER_BLOCK = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

REQUIRED_FRONTMATTER_FIELDS = ["agent_id", "version", "tier"]
VALID_TIERS = {"low", "mid", "high"}
VALID_MODES = {"bootstrap", "audit", "both"}


# ── Loader helpers ────────────────────────────────────────────────────────────

def load_system_config(config_path: Path) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f) or {}


def parse_frontmatter(content: str) -> tuple[dict | None, list[str]]:
    """Returns (parsed_frontmatter_dict, errors). None if frontmatter absent."""
    errors = []
    match = FRONTMATTER_BLOCK.match(content)
    if not match:
        errors.append("MISSING_FRONTMATTER: No YAML frontmatter (--- block) found at top of file.")
        return None, errors
    try:
        fm = yaml.safe_load(match.group(1)) or {}
        return fm, errors
    except yaml.YAMLError as exc:
        errors.append(f"INVALID_FRONTMATTER: YAML parse error — {exc}")
        return None, errors


# ── Individual checks ─────────────────────────────────────────────────────────

def check_frontmatter(fm: dict | None, system_config: dict) -> list[str]:
    errors = []
    if fm is None:
        return errors  # Already reported as MISSING_FRONTMATTER

    for field in REQUIRED_FRONTMATTER_FIELDS:
        if field not in fm:
            errors.append(f"MISSING_FRONTMATTER_FIELD: '{field}' not found in frontmatter.")

    tier = fm.get("tier")
    if tier and tier not in VALID_TIERS:
        errors.append(f"INVALID_TIER: '{tier}' is not a valid tier. Expected one of: {VALID_TIERS}.")

    mode = fm.get("mode")
    if mode and mode not in VALID_MODES:
        errors.append(f"INVALID_MODE: '{mode}' is not a valid mode. Expected one of: {VALID_MODES}.")

    agent_id = fm.get("agent_id")
    if agent_id and system_config:
        agents = system_config.get("agents", {})
        if agent_id in agents:
            config_tier = agents[agent_id].get("tier")
            if config_tier and tier and config_tier != tier:
                errors.append(
                    f"TIER_MISMATCH: frontmatter tier '{tier}' does not match "
                    f"system.config.yaml tier '{config_tier}' for agent '{agent_id}'."
                )

    return errors


def check_sections(lines: list[str]) -> list[str]:
    errors = []
    for pattern, name in REQUIRED_SECTIONS:
        if not any(re.match(pattern, line) for line in lines):
            errors.append(f"MISSING_SECTION: '{name}' section not found.")
    return errors


def check_placeholders(content: str) -> list[str]:
    errors = []
    for pattern in PLACEHOLDER_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            errors.append(
                f"PLACEHOLDER_FOUND: Pattern '{pattern}' found {len(matches)} time(s). "
                "Use [GAP-n] format instead."
            )
    return errors


def check_refusal(content: str) -> list[str]:
    if not REFUSAL_PATTERN.search(content):
        return [
            "MISSING_REFUSAL: No refusal pattern found. Agent must declare what it will not do "
            "using: refuse|will not|cannot + scope|outside|redirect|not handle|beyond."
        ]
    return []


def check_fewshot(content: str) -> list[str]:
    errors = []
    if not FEWSHOT_INPUT.search(content):
        errors.append("MISSING_FEWSHOT_INPUT: No '**Input**:' block found.")
    if not FEWSHOT_OUTPUT.search(content):
        errors.append("MISSING_FEWSHOT_OUTPUT: No '**Output**:' block found.")
    return errors


def check_line_count(lines: list[str], fm: dict | None, system_config: dict) -> list[str]:
    errors = []
    if fm is None or not system_config:
        return errors
    agent_id = fm.get("agent_id")
    if not agent_id:
        return errors
    agents = system_config.get("agents", {})
    if agent_id not in agents:
        return errors
    cfg = agents[agent_id]
    min_lines = cfg.get("min_lines", 0)
    max_lines = cfg.get("max_lines", float("inf"))
    n = len(lines)
    if n < min_lines:
        errors.append(
            f"TOO_SHORT: {n} lines found, minimum is {min_lines} for '{agent_id}'."
        )
    if max_lines != float("inf") and n > max_lines:
        errors.append(
            f"TOO_LONG: {n} lines found, maximum is {max_lines} for '{agent_id}'."
        )
    return errors


# ── Main validator ────────────────────────────────────────────────────────────

def validate(filepath: Path, system_config: dict) -> list[str]:
    content = filepath.read_text(encoding="utf-8")
    lines = content.splitlines()

    fm, errors = parse_frontmatter(content)
    errors += check_frontmatter(fm, system_config)
    errors += check_sections(lines)
    errors += check_placeholders(content)
    errors += check_refusal(content)
    errors += check_fewshot(content)
    errors += check_line_count(lines, fm, system_config)

    return errors


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: pre-execution-validator.py <agent-file.md> [system.config.yaml]")
        sys.exit(1)

    agent_path = Path(sys.argv[1])
    config_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("system.config.yaml")

    if not agent_path.exists():
        print(f"ERROR: Agent file not found: {agent_path}")
        sys.exit(1)

    system_config: dict = {}
    if config_path.exists():
        system_config = load_system_config(config_path)
    else:
        print(f"WARNING: system.config.yaml not found at '{config_path}'. Config checks skipped.")

    errors = validate(agent_path, system_config)

    sep = "=" * 64
    if errors:
        print(f"\nVALIDATION FAILED — {agent_path.name}")
        print(sep)
        for i, err in enumerate(errors, 1):
            print(f"  [{i:02d}] {err}")
        print(sep)
        print(f"  {len(errors)} error(s). Pipeline blocked.\n")
        sys.exit(1)
    else:
        print(f"VALIDATION PASSED — {agent_path.name}")
        sys.exit(0)


if __name__ == "__main__":
    main()
