"""File I/O isolation for dex.

All file-system writes go through this module so tests can mock them cleanly.
"""
from __future__ import annotations

from pathlib import Path


def write_gap_register(target_dir: str | Path, content: str) -> Path:
    """Write *content* to ``gap-register.md`` inside *target_dir*.

    Returns the path to the written file.
    """
    out = Path(target_dir) / "gap-register.md"
    out.write_text(content, encoding="utf-8")
    return out


def read_text(path: str | Path) -> str:
    """Return the UTF-8 text content of *path*."""
    return Path(path).read_text(encoding="utf-8")
