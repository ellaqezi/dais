"""dex — DevEx executor CLI entry point."""

import click


@click.group()
@click.version_option()
def cli() -> None:
    """DevEx executor: bootstrap, audit, validate, and track across DAIS, dotclaude, and loom-reed-light."""


@cli.command()
@click.argument("target_dir", default=".", type=click.Path(exists=True, file_okay=False))
def bootstrap(target_dir: str) -> None:
    """Bootstrap a project with DAIS derive → manifest → execute pipeline."""
    click.echo(f"[dex] bootstrap: {target_dir} (not yet implemented — task-003)")


@cli.command()
@click.argument("target_dir", default=".", type=click.Path(exists=True, file_okay=False))
def audit(target_dir: str) -> None:
    """Run DAIS audit sequence: audit-agent → gap-agent → remediation-agent."""
    click.echo(f"[dex] audit: {target_dir} (not yet implemented — task-004)")


@cli.command()
@click.argument("target_dir", default=".", type=click.Path(exists=True, file_okay=False))
def validate(target_dir: str) -> None:
    """Run all validators: pre-commit, LOOM schema, shellcheck."""
    # Implementation: task-002
    click.echo(f"[dex] validate: {target_dir} (task-002 — status: ready)")


@cli.command()
def status() -> None:
    """Show current task/spec/gap register state."""
    # Implementation: task-005
    click.echo("[dex] status (not yet implemented — task-005)")


if __name__ == "__main__":
    cli()
