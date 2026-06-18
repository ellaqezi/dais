"""dex — DevEx executor CLI entry point."""

import sys

import click

from dex import pipeline


def _print_summary(command: str, results: list[tuple[str, bool]]) -> None:
    """Print a multi-target summary line."""
    if len(results) <= 1:
        return
    passed = sum(1 for _, ok in results if ok)
    failed = len(results) - passed
    click.echo(f"\nSummary: {len(results)} target(s) \u2014 {passed} passed, {failed} failed")


@click.group()
@click.version_option()
def cli() -> None:
    """DevEx executor: bootstrap, audit, validate, and track across DAIS, dotclaude, and loom-reed-light."""


@cli.command()
@click.argument("target_dirs", nargs=-1, type=click.Path(exists=True, file_okay=False))
def bootstrap(target_dirs: tuple) -> None:
    """Bootstrap a project with DAIS derive → manifest → execute pipeline."""
    dirs = target_dirs or (".",)
    for target in dirs:
        click.echo(f"[dex] bootstrap: {target}")
        click.echo("  Not yet implemented  \u2192  ./tasks/task-003.md")
        click.echo("  Interim: run the DAIS bootstrap pipeline from the dais/ root")
        # fail-fast: stop on first unimplemented/failed dir
        sys.exit(1) if len(dirs) > 1 else None


@cli.command()
@click.argument("target_dirs", nargs=-1, type=click.Path(exists=True, file_okay=False))
@click.option("--apply", is_flag=True, help="Write gap-register.md to each target directory.")
def audit(target_dirs: tuple, apply: bool) -> None:
    """Run DAIS audit sequence: audit-agent \u2192 gap-agent \u2192 remediation-agent."""
    dirs = target_dirs or (".",)
    results: list[tuple[str, bool]] = []
    for target in dirs:
        click.echo(f"[dex] audit: {target}")
        try:
            gap_register = pipeline.run_audit(target, apply=apply)
            click.echo(gap_register)
            results.append((target, True))
        except (RuntimeError, ValueError) as exc:
            click.echo(f"  Error: {exc}", err=True)
            results.append((target, False))
        if len(dirs) > 1:
            click.echo()
    _print_summary("audit", results)
    if any(not ok for _, ok in results):
        sys.exit(1)


@cli.command()
@click.argument("target_dirs", nargs=-1, type=click.Path(exists=True, file_okay=False))
def validate(target_dirs: tuple) -> None:
    """Run all validators: pre-commit, LOOM schema, shellcheck."""
    dirs = target_dirs or (".",)
    results: list[tuple[str, bool]] = []
    for target in dirs:
        click.echo(f"[dex] validate: {target}")
        click.echo("  Not yet implemented  \u2192  ./tasks/task-002.md  (status: ready \u2014 implement next)")
        click.echo("  Interim: make validate")
        results.append((target, False))
        if len(dirs) > 1:
            click.echo()
    _print_summary("validate", results)
    if any(not ok for _, ok in results):
        sys.exit(1)


@cli.command()
@click.argument("target_dirs", nargs=-1, type=click.Path(exists=True, file_okay=False))
def status(target_dirs: tuple) -> None:
    """Show current task/spec/gap register state."""
    dirs = target_dirs or (".",)
    results: list[tuple[str, bool]] = []
    for target in dirs:
        click.echo(f"[dex] status: {target}")
        click.echo("  Not yet implemented  \u2192  ./tasks/task-005.md")
        click.echo("  Interim: cat tasks/task-list.md")
        results.append((target, False))
        if len(dirs) > 1:
            click.echo()
    _print_summary("status", results)
    # status is always exit 0 (read-only; stub counts as not-an-error)


if __name__ == "__main__":
    cli()
