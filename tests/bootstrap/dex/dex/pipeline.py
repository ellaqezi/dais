"""Audit pipeline: audit-agent → gap-agent → remediation-agent.

Usage
-----
from dex import pipeline

gap_register = pipeline.run_audit("/path/to/project", apply=True)
print(gap_register)
"""
from __future__ import annotations

from pathlib import Path

from dex import io as _io
from dex import runner as _runner

# Directories and file patterns to exclude from the audit context.
_SKIP_NAMES = {
    ".git", ".venv", "__pycache__", ".pytest_cache",
    "node_modules", ".ruff_cache", ".mypy_cache",
}
# Key files whose full text is included in the context (up to _MAX_FILE_BYTES each).
_KEY_FILES = ("README.md", "pyproject.toml", "Makefile", "CHANGELOG.md")
_MAX_FILE_BYTES = 8_192  # 8 KB per file — keeps the prompt bounded


def run_audit(target_dir: str | Path, *, apply: bool = False) -> str:
    """Run the DAIS audit pipeline on *target_dir*.

    Stages
    ------
    1. ``audit-agent``     — analyses the project; produces structured findings
    2. ``gap-agent``       — organises findings into a gap register
    3. ``remediation-agent`` — adds remediation steps to each gap

    Parameters
    ----------
    target_dir:
        Path to the project directory to audit.  Must exist.
    apply:
        When *False* (default) the gap register is only printed to stdout; the
        target project is not modified.  When *True*, ``gap-register.md`` is
        written to *target_dir*.

    Returns
    -------
    str
        The final gap register text produced by ``remediation-agent``.

    Raises
    ------
    ValueError
        If *target_dir* is not an existing directory.
    RuntimeError
        If any pipeline stage fails.
    """
    target = Path(target_dir).resolve()
    if not target.is_dir():
        raise ValueError(f"Not a directory: {target}")

    context = _build_context(target)
    audit_output = _runner.run_agent("audit-agent", context)
    gap_output = _runner.run_agent("gap-agent", audit_output)
    gap_register = _runner.run_agent("remediation-agent", gap_output)

    if apply:
        _io.write_gap_register(target, gap_register)

    return gap_register


def _build_context(target: Path) -> str:
    """Build the initial context text for ``audit-agent``."""
    lines: list[str] = [f"# Audit Target: {target}", "", "## Directory Tree", "```"]

    for item in sorted(target.rglob("*")):
        if _skip_path(item, target):
            continue
        rel = item.relative_to(target)
        indent = "  " * (len(rel.parts) - 1)
        suffix = "/" if item.is_dir() else ""
        lines.append(f"{indent}{rel.name}{suffix}")

    lines += ["```", ""]

    for name in _KEY_FILES:
        candidate = target / name
        if candidate.is_file():
            raw = candidate.read_bytes()
            text = raw[:_MAX_FILE_BYTES].decode("utf-8", errors="replace")
            truncated = len(raw) > _MAX_FILE_BYTES
            lines += [f"## {name}", "```", text]
            if truncated:
                lines.append(f"... (truncated at {_MAX_FILE_BYTES} bytes)")
            lines += ["```", ""]

    return "\n".join(lines)


def _skip_path(path: Path, root: Path) -> bool:
    """Return True if *path* should be excluded from the audit context."""
    return any(
        part in _SKIP_NAMES or part.endswith(".egg-info")
        for part in path.relative_to(root).parts
    )
