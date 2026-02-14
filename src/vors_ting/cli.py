"""Command-line interface for Vörs ting."""

from pathlib import Path

import typer

from .core.config import load_config
from .orchestration.orchestrator import Orchestrator

app = typer.Typer()

CONFIG_PATH_ARG = typer.Argument(..., help="Path to configuration file")
OUTPUT_DIR_OPTION = typer.Option(
    None, "--output", "-o", help="Output directory for results"
)


@app.command()
def run(
    config_path: Path = CONFIG_PATH_ARG,
    output_dir: Path | None = OUTPUT_DIR_OPTION,
) -> None:
    """Run Vörs ting with the given configuration."""
    # Load configuration
    config = load_config(config_path)

    # Create orchestrator
    orchestrator = Orchestrator(config)

    # Run the feedback loop
    result = orchestrator.run()

    # Save results
    if output_dir:
        orchestrator.save_state(output_dir)
        typer.echo(f"Results saved to {output_dir}")

    # Print summary
    typer.echo(f"Status: {result['status']}")
    typer.echo(f"Completed {orchestrator.current_round} rounds")


if __name__ == "__main__":
    app()
