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

    def test_default_target_is_cwd(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["bootstrap"])
            assert result.exit_code == 0
            assert "[dex] bootstrap:" in result.output

    def test_explicit_target(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["bootstrap", "."])
            assert result.exit_code == 0
            assert "[dex] bootstrap:" in result.output

    def test_nonexistent_target_exits_nonzero(self, runner):
        result = runner.invoke(cli, ["bootstrap", "/no/such/directory"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# audit
# ---------------------------------------------------------------------------

class TestAudit:
    def test_help(self, runner):
        result = runner.invoke(cli, ["audit", "--help"])
        assert result.exit_code == 0
        assert "audit" in result.output.lower()

    def test_default_target_is_cwd(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["audit"])
            assert result.exit_code == 0
            assert "[dex] audit:" in result.output

    def test_explicit_target(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["audit", "."])
            assert result.exit_code == 0
            assert "[dex] audit:" in result.output

    def test_nonexistent_target_exits_nonzero(self, runner):
        result = runner.invoke(cli, ["audit", "/no/such/directory"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

class TestValidate:
    def test_help(self, runner):
        result = runner.invoke(cli, ["validate", "--help"])
        assert result.exit_code == 0

    def test_default_target_is_cwd(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["validate"])
            assert result.exit_code == 0
            assert "[dex] validate:" in result.output

    def test_explicit_target(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["validate", "."])
            assert result.exit_code == 0
            assert "[dex] validate:" in result.output

    def test_nonexistent_target_exits_nonzero(self, runner):
        result = runner.invoke(cli, ["validate", "/no/such/directory"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

class TestStatus:
    def test_help(self, runner):
        result = runner.invoke(cli, ["status", "--help"])
        assert result.exit_code == 0

    def test_exits_zero(self, runner):
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        assert "[dex] status" in result.output
