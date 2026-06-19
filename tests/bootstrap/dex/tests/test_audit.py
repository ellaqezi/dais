"""Unit tests for dex audit pipeline (dex/runner.py, dex/io.py, dex/pipeline.py).

Written TDD-first: tests define the required behaviour; the implementation must
satisfy every assertion here.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dex import io as dex_io
from dex import pipeline
from dex import runner


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fake_dais_root(tmp_path: Path) -> Path:
    """Scaffold a minimal fake dais repository root."""
    root = tmp_path / "dais-root"
    root.mkdir(parents=True, exist_ok=True)
    (root / "AGENTS.md").touch()
    audit_dir = root / "agents" / "phase-3" / "audit"
    audit_dir.mkdir(parents=True)
    for name in ("audit-agent.md", "gap-agent.md", "remediation-agent.md"):
        (audit_dir / name).write_text(f"# {name}", encoding="utf-8")
    return root


# ---------------------------------------------------------------------------
# runner — environment & configuration
# ---------------------------------------------------------------------------

class TestRunnerConfig:
    def test_dais_root_auto_detects(self):
        """dais_root() must find the real repo root when run inside the project."""
        root = runner.dais_root()
        assert (root / "AGENTS.md").exists()
        assert (root / "agents").is_dir()

    def test_dais_root_from_env(self, tmp_path):
        """DAIS_ROOT env var overrides auto-detection."""
        fake = tmp_path / "fake-root"
        fake.mkdir()
        (fake / "AGENTS.md").touch()
        (fake / "agents").mkdir()
        with patch.dict(os.environ, {"DAIS_ROOT": str(fake)}):
            assert runner.dais_root() == fake.resolve()

    def test_dais_root_invalid_env_falls_through_to_auto(self, tmp_path):
        """A non-existent DAIS_ROOT path falls through to auto-detection."""
        with patch.dict(os.environ, {"DAIS_ROOT": str(tmp_path / "no-such")}):
            # Either finds the real root or raises — never returns a non-dir.
            try:
                root = runner.dais_root()
                assert (root / "AGENTS.md").exists()
            except RuntimeError:
                pass

    def test_agent_cmd_defaults_to_claude(self):
        env = {k: v for k, v in os.environ.items() if k != "DEX_AGENT_CMD"}
        with patch.dict(os.environ, env, clear=True):
            assert runner.agent_cmd() == ["claude", "--print", "--"]

    def test_agent_cmd_reads_env_var(self):
        with patch.dict(os.environ, {"DEX_AGENT_CMD": "my-llm --flag --json"}):
            assert runner.agent_cmd() == ["my-llm", "--flag", "--json"]


# ---------------------------------------------------------------------------
# runner — run_agent
# ---------------------------------------------------------------------------

class TestRunAgent:
    def test_unknown_agent_id_raises(self):
        with pytest.raises(RuntimeError, match="Unknown agent"):
            runner.run_agent("not-a-real-agent", "input")

    def test_invokes_subprocess_with_system_and_user_prompt(self, tmp_path):
        fake_root = _fake_dais_root(tmp_path)
        with (
            patch.dict(os.environ, {"DAIS_ROOT": str(fake_root)}),
            patch("dex.runner.subprocess.run") as mock_run,
        ):
            mock_run.return_value = MagicMock(stdout="agent output", returncode=0)
            result = runner.run_agent("audit-agent", "my user input")

        assert result == "agent output"
        call_kwargs = mock_run.call_args.kwargs
        # The agent file contents must be part of what is sent to stdin.
        assert "# audit-agent.md" in call_kwargs["input"]
        # The user prompt must be included too.
        assert "my user input" in call_kwargs["input"]

    def test_subprocess_nonzero_exit_raises_runtime_error(self, tmp_path):
        fake_root = _fake_dais_root(tmp_path)
        with (
            patch.dict(os.environ, {"DAIS_ROOT": str(fake_root)}),
            patch(
                "dex.runner.subprocess.run",
                side_effect=subprocess.CalledProcessError(1, "cmd", stderr="boom"),
            ),
        ):
            with pytest.raises(RuntimeError, match="exited 1"):
                runner.run_agent("audit-agent", "input")

    def test_missing_backend_binary_raises_runtime_error(self, tmp_path):
        fake_root = _fake_dais_root(tmp_path)
        with (
            patch.dict(os.environ, {"DAIS_ROOT": str(fake_root)}),
            patch("dex.runner.subprocess.run", side_effect=FileNotFoundError),
        ):
            with pytest.raises(RuntimeError, match="not found"):
                runner.run_agent("audit-agent", "input")

    def test_all_three_audit_agents_are_known(self, tmp_path):
        """Smoke-check: none of the three pipeline agent IDs raise 'Unknown agent'."""
        fake_root = _fake_dais_root(tmp_path)
        for agent_id in ("audit-agent", "gap-agent", "remediation-agent"):
            with (
                patch.dict(os.environ, {"DAIS_ROOT": str(fake_root)}),
                patch("dex.runner.subprocess.run") as mock_run,
            ):
                mock_run.return_value = MagicMock(stdout="ok", returncode=0)
                result = runner.run_agent(agent_id, "input")
                assert result == "ok"


# ---------------------------------------------------------------------------
# io — file operations
# ---------------------------------------------------------------------------

class TestIo:
    def test_write_gap_register_creates_file(self, tmp_path):
        out = dex_io.write_gap_register(tmp_path, "# Gap Register\n")
        assert out == tmp_path / "gap-register.md"
        assert out.read_text(encoding="utf-8") == "# Gap Register\n"

    def test_write_gap_register_overwrites_existing(self, tmp_path):
        dex_io.write_gap_register(tmp_path, "first")
        out = dex_io.write_gap_register(tmp_path, "second")
        assert out.read_text(encoding="utf-8") == "second"

    def test_write_gap_register_returns_path_object(self, tmp_path):
        out = dex_io.write_gap_register(tmp_path, "content")
        assert isinstance(out, Path)

    def test_read_text_returns_file_contents(self, tmp_path):
        f = tmp_path / "hello.txt"
        f.write_text("hello world", encoding="utf-8")
        assert dex_io.read_text(f) == "hello world"

    def test_read_text_accepts_string_path(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("data", encoding="utf-8")
        assert dex_io.read_text(str(f)) == "data"


# ---------------------------------------------------------------------------
# pipeline — run_audit
# ---------------------------------------------------------------------------

class TestPipelineRunAudit:
    def test_raises_on_nonexistent_directory(self, tmp_path):
        with pytest.raises(ValueError, match="Not a directory"):
            pipeline.run_audit(tmp_path / "no-such-dir")

    def test_raises_on_file_path(self, tmp_path):
        f = tmp_path / "file.txt"
        f.touch()
        with pytest.raises(ValueError, match="Not a directory"):
            pipeline.run_audit(f)

    def test_calls_three_agents_in_order(self, tmp_path):
        target = tmp_path / "project"
        target.mkdir()
        call_log: list[str] = []

        def _fake(agent_id: str, input_text: str) -> str:
            call_log.append(agent_id)
            return f"{agent_id}-output"

        with patch("dex.pipeline._runner.run_agent", side_effect=_fake):
            pipeline.run_audit(target)

        assert call_log == ["audit-agent", "gap-agent", "remediation-agent"]

    def test_chains_outputs_between_agents(self, tmp_path):
        target = tmp_path / "project"
        target.mkdir()
        captured: list[tuple[str, str]] = []

        def _fake(agent_id: str, input_text: str) -> str:
            captured.append((agent_id, input_text))
            return f"output-of-{agent_id}"

        with patch("dex.pipeline._runner.run_agent", side_effect=_fake):
            pipeline.run_audit(target)

        # gap-agent must receive audit-agent's output as its input.
        assert captured[1] == ("gap-agent", "output-of-audit-agent")
        # remediation-agent must receive gap-agent's output.
        assert captured[2] == ("remediation-agent", "output-of-gap-agent")

    def test_returns_remediation_agent_output(self, tmp_path):
        target = tmp_path / "project"
        target.mkdir()
        with patch(
            "dex.pipeline._runner.run_agent",
            side_effect=["audit-out", "gap-out", "final-gap-register"],
        ):
            result = pipeline.run_audit(target)
        assert result == "final-gap-register"

    def test_no_write_without_apply_flag(self, tmp_path):
        target = tmp_path / "project"
        target.mkdir()
        with (
            patch("dex.pipeline._runner.run_agent", return_value="gap"),
            patch("dex.pipeline._io.write_gap_register") as mock_write,
        ):
            pipeline.run_audit(target, apply=False)
        mock_write.assert_not_called()

    def test_writes_gap_register_when_apply_true(self, tmp_path):
        target = tmp_path / "project"
        target.mkdir()
        with (
            patch("dex.pipeline._runner.run_agent", return_value="gap register content"),
            patch("dex.pipeline._io.write_gap_register") as mock_write,
        ):
            pipeline.run_audit(target, apply=True)
        mock_write.assert_called_once_with(target.resolve(), "gap register content")

    def test_agent_failure_propagates_runtime_error(self, tmp_path):
        target = tmp_path / "project"
        target.mkdir()
        with (
            patch(
                "dex.pipeline._runner.run_agent",
                side_effect=RuntimeError("backend down"),
            ),
            pytest.raises(RuntimeError, match="backend down"),
        ):
            pipeline.run_audit(target)


# ---------------------------------------------------------------------------
# pipeline — _build_context
# ---------------------------------------------------------------------------

class TestBuildContext:
    def test_includes_directory_tree(self, tmp_path):
        target = tmp_path / "project"
        target.mkdir()
        (target / "src").mkdir()
        (target / "src" / "app.py").write_text("print(1)", encoding="utf-8")
        (target / "README.md").write_text("hello", encoding="utf-8")

        ctx = pipeline._build_context(target)
        assert "src/" in ctx
        assert "app.py" in ctx

    def test_includes_key_file_content(self, tmp_path):
        target = tmp_path / "project"
        target.mkdir()
        (target / "README.md").write_text("# My Project", encoding="utf-8")

        ctx = pipeline._build_context(target)
        assert "# My Project" in ctx

    def test_excludes_venv(self, tmp_path):
        target = tmp_path / "project"
        target.mkdir()
        venv_bin = target / ".venv" / "bin"
        venv_bin.mkdir(parents=True)
        (venv_bin / "python").write_text("#!/usr/bin/env python3", encoding="utf-8")

        ctx = pipeline._build_context(target)
        assert ".venv" not in ctx

    def test_excludes_git(self, tmp_path):
        target = tmp_path / "project"
        target.mkdir()
        git_dir = target / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("[core]", encoding="utf-8")

        ctx = pipeline._build_context(target)
        assert ".git" not in ctx

    def test_excludes_pycache(self, tmp_path):
        target = tmp_path / "project"
        target.mkdir()
        cache = target / "__pycache__"
        cache.mkdir()
        (cache / "app.cpython-313.pyc").write_bytes(b"bytecode")

        ctx = pipeline._build_context(target)
        assert "__pycache__" not in ctx

    def test_context_begins_with_audit_target_header(self, tmp_path):
        target = tmp_path / "project"
        target.mkdir()

        ctx = pipeline._build_context(target)
        assert ctx.startswith("# Audit Target:")
