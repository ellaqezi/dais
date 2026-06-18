"""dex — DevEx executor CLI entry point."""

import click


@click.group()
@click.version_option()
def cli() -> None:
    """DevEx executor: bootstrap, audit, validate, and track across DAIS, dotclaude, and loom-reed-light."""


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Show full pipeline steps and interim workaround.")
@click.argument("target_dir", default=".", type=click.Path(exists=True, file_okay=False))
def bootstrap(target_dir: str, verbose: bool) -> None:
    """Bootstrap a project with DAIS derive → manifest → execute pipeline."""
    click.echo(f"[dex] bootstrap: {target_dir}")
    if verbose:
        click.echo()
        click.echo("Pipeline (when implemented):")
        click.echo("  1. derive-agent   — infer project topology and stack from existing artefacts")
        click.echo("  2. manifest-agent — present the generation plan; gates on explicit CONFIRM")
        click.echo("  3. execute phase  — scaffold, architecture, CI/CD, security, observability, testing, docs, finops")
        click.echo()
        click.echo("Interim: run the DAIS bootstrap pipeline manually from the dais/ root.")
    else:
        click.echo("  Not yet implemented  →  ./tasks/task-003.md")
        click.echo("  Interim: run the DAIS bootstrap pipeline from the dais/ root")
        click.echo("  Tip: dex bootstrap --verbose  for pipeline details")


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Show full pipeline steps and interim workaround.")
@click.argument("target_dir", default=".", type=click.Path(exists=True, file_okay=False))
def audit(target_dir: str, verbose: bool) -> None:
    """Run DAIS audit sequence: audit-agent → gap-agent → remediation-agent."""
    click.echo(f"[dex] audit: {target_dir}")
    if verbose:
        click.echo()
        click.echo("Pipeline (when implemented):")
        click.echo("  1. audit-agent       — scan the project for architectural and compliance gaps")
        click.echo("  2. gap-agent         — classify findings by severity and produce a gap register")
        click.echo("  3. remediation-agent — generate a prioritised remediation plan")
        click.echo()
        click.echo("Interim: run the DAIS audit agents manually from the dais/ root.")
    else:
        click.echo("  Not yet implemented  →  ./tasks/task-004.md")
        click.echo("  Interim: run DAIS audit agents manually from the dais/ root")
        click.echo("  Tip: dex audit --verbose  for pipeline details")


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Show full validator layers and interim workaround.")
@click.argument("target_dir", default=".", type=click.Path(exists=True, file_okay=False))
def validate(target_dir: str, verbose: bool) -> None:
    """Run all validators: pre-commit, LOOM schema, shellcheck."""
    click.echo(f"[dex] validate: {target_dir}")
    if verbose:
        click.echo()
        click.echo("Validation layers (when implemented):")
        click.echo("  1. pre-commit  — formatting, whitespace, YAML, secret scanning")
        click.echo("  2. LOOM schema — task section completeness and S/M size compliance")
        click.echo("  3. shellcheck  — shell script syntax")
        click.echo()
        click.echo("Interim: make validate")
    else:
        click.echo("  Not yet implemented  →  ./tasks/task-002.md  (status: ready — implement next)")
        click.echo("  Interim: make validate")
        click.echo("  Tip: dex validate --verbose  for layer details")


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Show full state sources and interim workaround.")
def status(verbose: bool) -> None:
    """Show current task/spec/gap register state."""
    click.echo("[dex] status")
    if verbose:
        click.echo()
        click.echo("State sources (when implemented):")
        click.echo("  tasks/task-list.md — backlog with status (done / ready / in-progress)")
        click.echo("  spec/              — specs present and their last-modified dates")
        click.echo("  gap register       — open audit findings if an audit has been run")
        click.echo()
        click.echo("Interim: cat tasks/task-list.md")
    else:
        click.echo("  Not yet implemented  →  ./tasks/task-005.md")
        click.echo("  Interim: cat tasks/task-list.md")
        click.echo("  Tip: dex status --verbose  for state source details")


if __name__ == "__main__":
    cli()
