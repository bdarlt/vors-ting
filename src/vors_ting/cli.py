"""Command-line interface for Vörs ting."""

from pathlib import Path

import typer

from vors_ting.core.config import load_config
from vors_ting.orchestration.orchestrator import Orchestrator

app = typer.Typer(
    help="Vors ting - Multi-agent workflow tool for iterative feedback loops"
)

CONFIG_PATH_ARG = typer.Argument(
    ..., help="Path to YAML configuration file"
)
OUTPUT_DIR_OPTION = typer.Option(
    None, "--output", "-o", help="Output directory for results"
)
QUIET_OPTION = typer.Option(
    False, "--quiet", "-q", help="Suppress verbose output (only show summary)"
)


@app.command()
def run(
    config_path: Path = CONFIG_PATH_ARG,
    output_dir: Path | None = OUTPUT_DIR_OPTION,
    quiet: bool = QUIET_OPTION,
) -> None:
    """Run Vors ting with the given YAML configuration.

    In verbose mode (default), shows progress including:
    - LLM connection status
    - Agent prompts and responses
    - First 4 lines of each response preview
    - Convergence status

    Use --quiet to suppress verbose output.
    """
    # Load configuration
    config = load_config(config_path)

    # Create orchestrator
    orchestrator = Orchestrator(config, quiet=quiet)

    # Run the feedback loop
    result = orchestrator.run()

    # Save results
    if output_dir:
        orchestrator.save_state(output_dir)
        if not quiet:
            typer.echo(f"Results saved to {output_dir}")

    # Print summary
    if not quiet:
        typer.echo(f"\nStatus: {result['status']}")
        typer.echo(f"Completed {orchestrator.current_round} rounds")


if __name__ == "__main__":
    app()
