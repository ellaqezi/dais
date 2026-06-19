"""Tests for dex CLI entry point (dex/main.py)."""

import os
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from dex.main import cli


@pytest.fixture()
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# Top-level group
# ---------------------------------------------------------------------------

class TestCliGroup:
    def test_help_exits_zero(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

    def test_help_lists_all_subcommands(self, runner):
        result = runner.invoke(cli, ["--help"])
        for cmd in ("bootstrap", "audit", "validate", "status"):
            assert cmd in result.output

    def test_version_flag(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_unknown_command_exits_nonzero(self, runner):
        result = runner.invoke(cli, ["notacommand"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# bootstrap  (fail-fast: stops on first failing dir)
# ---------------------------------------------------------------------------

class TestBootstrap:
    def test_help(self, runner):
        result = runner.invoke(cli, ["bootstrap", "--help"])
        assert result.exit_code == 0
        assert "DAIS" in result.output

    def test_nonexistent_target_exits_nonzero(self, runner):
        result = runner.invoke(cli, ["bootstrap", "/no/such/directory"])
        assert result.exit_code != 0

    def test_default_cwd(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["bootstrap"])
            assert result.exit_code == 0
            assert "[dex] bootstrap:" in result.output
            assert "./tasks/task-003.md" in result.output

    def test_explicit_single_target(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["bootstrap", "."])
            assert result.exit_code == 0
            assert "[dex] bootstrap: ." in result.output

    def test_multi_target_fail_fast(self, runner):
        with runner.isolated_filesystem():
            os.makedirs("a")
            os.makedirs("b")
            result = runner.invoke(cli, ["bootstrap", "a", "b"])
            assert result.exit_code != 0
            assert "[dex] bootstrap: a" in result.output
            assert "[dex] bootstrap: b" not in result.output

    def test_no_summary_line(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["bootstrap"])
            assert "Summary:" not in result.output

    def test_unknown_flag_exits_nonzero(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["bootstrap", "--verbose"])
            assert result.exit_code != 0


# ---------------------------------------------------------------------------
# audit  (run-all: visits every dir, exits non-zero if any failed)
# ---------------------------------------------------------------------------

class TestAudit:
    def test_help_includes_apply_flag(self, runner):
        result = runner.invoke(cli, ["audit", "--help"])
        assert result.exit_code == 0
        assert "--apply" in result.output

    def test_nonexistent_target_exits_nonzero(self, runner):
        result = runner.invoke(cli, ["audit", "/no/such/directory"])
        assert result.exit_code != 0

    def test_successful_audit_exits_zero(self, runner):
        with (
            runner.isolated_filesystem(),
            patch("dex.pipeline.run_audit", return_value="# Gap Register\n"),
        ):
            result = runner.invoke(cli, ["audit", "."])
            assert result.exit_code == 0
            assert "[dex] audit: ." in result.output
            assert "# Gap Register" in result.output

    def test_failed_audit_exits_nonzero(self, runner):
        with (
            runner.isolated_filesystem(),
            patch("dex.pipeline.run_audit", side_effect=RuntimeError("agent failed")),
        ):
            result = runner.invoke(cli, ["audit", "."])
            assert result.exit_code != 0

    def test_apply_flag_passed_to_pipeline(self, runner):
        with (
            runner.isolated_filesystem(),
            patch("dex.pipeline.run_audit", return_value="gap") as mock_audit,
        ):
            runner.invoke(cli, ["audit", "--apply", "."])
            _, kwargs = mock_audit.call_args
            assert kwargs.get("apply") is True

    def test_no_apply_by_default(self, runner):
        with (
            runner.isolated_filesystem(),
            patch("dex.pipeline.run_audit", return_value="gap") as mock_audit,
        ):
            runner.invoke(cli, ["audit", "."])
            _, kwargs = mock_audit.call_args
            assert kwargs.get("apply", False) is False

    def test_multi_target_runs_all(self, runner):
        with (
            runner.isolated_filesystem(),
            patch("dex.pipeline.run_audit", return_value="gap") as mock_audit,
        ):
            os.makedirs("a")
            os.makedirs("b")
            result = runner.invoke(cli, ["audit", "a", "b"])
            assert mock_audit.call_count == 2
            assert "[dex] audit: a" in result.output
            assert "[dex] audit: b" in result.output
            assert "Summary: 2 target(s)" in result.output

    def test_multi_target_run_all_despite_failure(self, runner):
        """run-all: second directory must be visited even when first fails."""
        with runner.isolated_filesystem():
            os.makedirs("a")
            os.makedirs("b")
            with patch(
                "dex.pipeline.run_audit",
                side_effect=[RuntimeError("fail"), "gap"],
            ):
                result = runner.invoke(cli, ["audit", "a", "b"])
                assert "[dex] audit: a" in result.output
                assert "[dex] audit: b" in result.output
                assert "1 passed" in result.output
                assert "1 failed" in result.output
                assert result.exit_code != 0

    def test_no_summary_for_single_target(self, runner):
        with (
            runner.isolated_filesystem(),
            patch("dex.pipeline.run_audit", return_value="gap"),
        ):
            result = runner.invoke(cli, ["audit", "."])
            assert "Summary:" not in result.output

    def test_unknown_flag_exits_nonzero(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["audit", "--verbose"])
            assert result.exit_code != 0


# ---------------------------------------------------------------------------
# validate  (run-all: visits every dir, exits non-zero if any failed)
# ---------------------------------------------------------------------------

class TestValidate:
    def test_help(self, runner):
        result = runner.invoke(cli, ["validate", "--help"])
        assert result.exit_code == 0

    def test_nonexistent_target_exits_nonzero(self, runner):
        result = runner.invoke(cli, ["validate", "/no/such/directory"])
        assert result.exit_code != 0

    def test_default_cwd(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["validate"])
            assert result.exit_code != 0
            assert "[dex] validate:" in result.output
            assert "./tasks/task-002.md" in result.output
            assert "make validate" in result.output

    def test_explicit_single_target(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["validate", "."])
            assert result.exit_code != 0
            assert "[dex] validate: ." in result.output

    def test_multi_target_runs_all(self, runner):
        with runner.isolated_filesystem():
            os.makedirs("a")
            os.makedirs("b")
            result = runner.invoke(cli, ["validate", "a", "b"])
            assert "[dex] validate: a" in result.output
            assert "[dex] validate: b" in result.output
            assert "Summary: 2 target(s)" in result.output

    def test_no_summary_for_single_target(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["validate", "."])
            assert "Summary:" not in result.output

    def test_unknown_flag_exits_nonzero(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["validate", "--verbose"])
            assert result.exit_code != 0


# ---------------------------------------------------------------------------
# status  (run-all, always exit 0 — read-only)
# ---------------------------------------------------------------------------

class TestStatus:
    def test_help(self, runner):
        result = runner.invoke(cli, ["status", "--help"])
        assert result.exit_code == 0

    def test_default_cwd(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["status"])
            assert result.exit_code == 0
            assert "[dex] status:" in result.output
            assert "./tasks/task-005.md" in result.output
            assert "task-list.md" in result.output

    def test_explicit_single_target(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["status", "."])
            assert result.exit_code == 0
            assert "[dex] status: ." in result.output

    def test_multi_target_runs_all(self, runner):
        with runner.isolated_filesystem():
            os.makedirs("a")
            os.makedirs("b")
            result = runner.invoke(cli, ["status", "a", "b"])
            assert result.exit_code == 0
            assert "[dex] status: a" in result.output
            assert "[dex] status: b" in result.output
            assert "Summary: 2 target(s)" in result.output

    def test_no_summary_for_single_target(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["status", "."])
            assert "Summary:" not in result.output

    def test_unknown_flag_exits_nonzero(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["status", "--verbose"])
            assert result.exit_code != 0
