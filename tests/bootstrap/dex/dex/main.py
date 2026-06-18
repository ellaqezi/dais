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
    click.echo(f"[dex] bootstrap: {target_dir}")
    click.echo("  Not yet implemented  →  ./tasks/task-003.md")
    click.echo("  Interim: run the DAIS bootstrap pipeline from the dais/ root")


@cli.command()
@click.argument("target_dir", default=".", type=click.Path(exists=True, file_okay=False))
def audit(target_dir: str) -> None:
    """Run DAIS audit sequence: audit-agent → gap-agent → remediation-agent."""
    click.echo(f"[dex] audit: {target_dir}")
    click.echo("  Not yet implemented  →  ./tasks/task-004.md")
    click.echo("  Interim: run DAIS audit agents manually from the dais/ root")


@cli.command()
@click.argument("target_dir", default=".", type=click.Path(exists=True, file_okay=False))
def validate(target_dir: str) -> None:
    """Run all validators: pre-commit, LOOM schema, shellcheck."""
    click.echo(f"[dex] validate: {target_dir}")
    click.echo("  Not yet implemented  →  ./tasks/task-002.md  (status: ready — implement next)")
    click.echo("  Interim: make validate")


@cli.command()
def status() -> None:
    """Show current task/spec/gap register state."""
    click.echo("[dex] status")
    click.echo("  Not yet implemented  →  ./tasks/task-005.md")
    click.echo("  Interim: cat tasks/task-list.md")


if __name__ == "__main__":
    cli()
