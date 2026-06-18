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
    click.echo()
    click.echo("This command will run the DAIS bootstrap pipeline:")
    click.echo("  1. derive-agent   — infer project topology and stack from existing artefacts")
    click.echo("  2. manifest-agent — present the generation plan for CONFIRM before any files are written")
    click.echo("  3. execute phase  — scaffold, architecture, CI/CD, security, observability, testing, docs, finops")
    click.echo()
    click.echo("Not yet implemented. To implement: see tasks/task-003.md")
    click.echo("In the meantime, run the DAIS pipeline manually from the dais/ root.")


@cli.command()
@click.argument("target_dir", default=".", type=click.Path(exists=True, file_okay=False))
def audit(target_dir: str) -> None:
    """Run DAIS audit sequence: audit-agent → gap-agent → remediation-agent."""
    click.echo(f"[dex] audit: {target_dir}")
    click.echo()
    click.echo("This command will run the DAIS audit pipeline:")
    click.echo("  1. audit-agent       — scan the project for architectural and compliance gaps")
    click.echo("  2. gap-agent         — classify findings by severity and produce a gap register")
    click.echo("  3. remediation-agent — generate a prioritised remediation plan")
    click.echo()
    click.echo("Not yet implemented. To implement: see tasks/task-004.md")
    click.echo("In the meantime, run the DAIS audit agents manually from the dais/ root.")


@cli.command()
@click.argument("target_dir", default=".", type=click.Path(exists=True, file_okay=False))
def validate(target_dir: str) -> None:
    """Run all validators: pre-commit, LOOM schema, shellcheck."""
    click.echo(f"[dex] validate: {target_dir}")
    click.echo()
    click.echo("This command will run the three-layer validation stack in sequence:")
    click.echo("  1. pre-commit        — formatting, whitespace, YAML, secret scanning")
    click.echo("  2. LOOM schema       — task section completeness and S/M size compliance")
    click.echo("  3. shellcheck        — shell script syntax")
    click.echo()
    click.echo("Not yet implemented. To implement: see tasks/task-002.md (status: ready)")
    click.echo("In the meantime, run validators directly:")
    click.echo("  make validate")


@cli.command()
def status() -> None:
    """Show current task/spec/gap register state."""
    click.echo("[dex] status")
    click.echo()
    click.echo("This command will summarise the project state:")
    click.echo("  - tasks/task-list.md  — backlog with status (done / ready / in-progress)")
    click.echo("  - spec/              — specs present and their last-modified dates")
    click.echo("  - gap register       — open audit findings if an audit has been run")
    click.echo()
    click.echo("Not yet implemented. To implement: see tasks/task-005.md")
    click.echo("In the meantime, review tasks/task-list.md directly.")


if __name__ == "__main__":
    cli()
