"""Subprocess runner for DAIS agents.

Configuration
-------------
DAIS_ROOT    — path to the dais repository root (auto-detected if unset)
DEX_AGENT_CMD — shell command used to invoke the LLM backend
                Default: "claude --print --"
                The command receives the combined system+user prompt on stdin
                and must write the agent's response to stdout.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

DAIS_ROOT_ENV = "DAIS_ROOT"
AGENT_CMD_ENV = "DEX_AGENT_CMD"

# Paths relative to the dais repository root.
AGENT_PATHS: dict[str, str] = {
    "audit-agent": "agents/phase-3/audit/audit-agent.md",
    "gap-agent": "agents/phase-3/audit/gap-agent.md",
    "remediation-agent": "agents/phase-3/audit/remediation-agent.md",
    "derive-agent": "agents/phase-1/derive-agent.md",
    "manifest-agent": "agents/phase-2/manifest-agent.md",
}


def dais_root() -> Path:
    """Resolve the DAIS repository root.

    Checks the ``DAIS_ROOT`` environment variable first.  If unset, walks up
    from this source file looking for the dais root marker (``AGENTS.md`` +
    ``agents/`` directory).

    Raises ``RuntimeError`` if the root cannot be determined.
    """
    from_env = os.environ.get(DAIS_ROOT_ENV, "")
    if from_env:
        root = Path(from_env)
        if root.is_dir():
            return root.resolve()

    for parent in Path(__file__).resolve().parents:
        if (parent / "AGENTS.md").exists() and (parent / "agents").is_dir():
            return parent

    raise RuntimeError(
        f"DAIS root not found. Set {DAIS_ROOT_ENV}=<path/to/dais> or run dex "
        "from within the dais repository."
    )


def agent_cmd() -> list[str]:
    """Return the command list used to invoke the LLM backend.

    Reads ``DEX_AGENT_CMD`` from the environment (splits on whitespace).
    Falls back to ``["claude", "--print", "--"]``.
    """
    cmd = os.environ.get(AGENT_CMD_ENV, "")
    if cmd:
        return cmd.split()
    return ["claude", "--print", "--"]


def run_agent(agent_id: str, input_text: str) -> str:
    """Invoke a DAIS agent and return its text output.

    The agent's ``.md`` file is read from the dais repository and prepended as
    the system prompt.  The *input_text* is passed as the user prompt.  Both
    are written to the backend process's stdin separated by a ``---`` divider.

    Raises
    ------
    RuntimeError
        On unknown agent, missing agent file, non-zero subprocess exit, or
        backend command not found.
    """
    root = dais_root()
    rel = AGENT_PATHS.get(agent_id)
    if rel is None:
        raise RuntimeError(
            f"Unknown agent: {agent_id!r}. Known: {sorted(AGENT_PATHS)}"
        )

    agent_file = root / rel
    if not agent_file.exists():
        raise RuntimeError(f"Agent file not found: {agent_file}")

    system_prompt = agent_file.read_text(encoding="utf-8")
    cmd = agent_cmd()
    full_input = f"{system_prompt}\n\n---\n\n{input_text}"

    try:
        proc = subprocess.run(
            cmd,
            input=full_input,
            capture_output=True,
            text=True,
            check=True,
        )
        return proc.stdout
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Agent {agent_id!r} exited {exc.returncode}:\n{exc.stderr}"
        ) from exc
    except FileNotFoundError as exc:
        cmd_str = " ".join(cmd)
        raise RuntimeError(
            f"LLM runner not found: {cmd_str!r}. "
            f"Set {AGENT_CMD_ENV}=<command> to configure the agent runner."
        ) from exc
