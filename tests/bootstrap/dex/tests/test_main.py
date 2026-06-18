"""Tests for dex CLI entry point (dex/main.py)."""

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
# bootstrap
# ---------------------------------------------------------------------------

class TestBootstrap:
    def test_help(self, runner):
        result = runner.invoke(cli, ["bootstrap", "--help"])
        assert result.exit_code == 0
        assert "DAIS" in result.output
        assert "--verbose" in result.output

    def test_nonexistent_target_exits_nonzero(self, runner):
        result = runner.invoke(cli, ["bootstrap", "/no/such/directory"])
        assert result.exit_code != 0

    def test_default_terse_output(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["bootstrap"])
            assert result.exit_code == 0
            assert "[dex] bootstrap:" in result.output
            assert "./tasks/task-003.md" in result.output
            assert "--verbose" in result.output
            # detailed steps should NOT appear without --verbose
            assert "derive-agent" not in result.output

    def test_verbose_output(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["bootstrap", "--verbose"])
            assert result.exit_code == 0
            assert "derive-agent" in result.output
            assert "manifest-agent" in result.output
            assert "execute phase" in result.output

    def test_verbose_short_flag(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["bootstrap", "-v"])
            assert result.exit_code == 0
            assert "derive-agent" in result.output


# ---------------------------------------------------------------------------
# audit
# ---------------------------------------------------------------------------

class TestAudit:
    def test_help(self, runner):
        result = runner.invoke(cli, ["audit", "--help"])
        assert result.exit_code == 0
        assert "--verbose" in result.output

    def test_nonexistent_target_exits_nonzero(self, runner):
        result = runner.invoke(cli, ["audit", "/no/such/directory"])
        assert result.exit_code != 0

    def test_default_terse_output(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["audit"])
            assert result.exit_code == 0
            assert "[dex] audit:" in result.output
            assert "./tasks/task-004.md" in result.output
            assert "--verbose" in result.output
            assert "audit-agent" not in result.output

    def test_verbose_output(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["audit", "--verbose"])
            assert result.exit_code == 0
            assert "audit-agent" in result.output
            assert "gap-agent" in result.output
            assert "remediation-agent" in result.output

    def test_verbose_short_flag(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["audit", "-v"])
            assert result.exit_code == 0
            assert "audit-agent" in result.output


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

class TestValidate:
    def test_help(self, runner):
        result = runner.invoke(cli, ["validate", "--help"])
        assert result.exit_code == 0
        assert "--verbose" in result.output

    def test_nonexistent_target_exits_nonzero(self, runner):
        result = runner.invoke(cli, ["validate", "/no/such/directory"])
        assert result.exit_code != 0

    def test_default_terse_output(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["validate"])
            assert result.exit_code == 0
            assert "[dex] validate:" in result.output
            assert "./tasks/task-002.md" in result.output
            assert "make validate" in result.output
            assert "--verbose" in result.output
            # layer details should NOT appear without --verbose
            assert "pre-commit" not in result.output

    def test_verbose_output(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["validate", "--verbose"])
            assert result.exit_code == 0
            assert "pre-commit" in result.output
            assert "LOOM schema" in result.output
            assert "shellcheck" in result.output
            assert "make validate" in result.output

    def test_verbose_short_flag(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["validate", "-v"])
            assert result.exit_code == 0
            assert "pre-commit" in result.output


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

class TestStatus:
    def test_help(self, runner):
        result = runner.invoke(cli, ["status", "--help"])
        assert result.exit_code == 0
        assert "--verbose" in result.output

    def test_default_terse_output(self, runner):
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        assert "[dex] status" in result.output
        assert "./tasks/task-005.md" in result.output
        assert "task-list.md" in result.output
        assert "--verbose" in result.output
        # state sources should NOT appear without --verbose
        assert "spec/" not in result.output

    def test_verbose_output(self, runner):
        result = runner.invoke(cli, ["status", "--verbose"])
        assert result.exit_code == 0
        assert "task-list.md" in result.output
        assert "spec/" in result.output
        assert "gap register" in result.output

    def test_verbose_short_flag(self, runner):
        result = runner.invoke(cli, ["status", "-v"])
        assert result.exit_code == 0
        assert "spec/" in result.output
