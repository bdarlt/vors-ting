"""Interaction logging strategies for Vörs ting."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class InteractionLogger(Protocol):
    """Protocol for logging agent interactions."""

    def log_interaction(  # noqa: PLR0913
        self,
        round_num: int,
        agent_name: str,
        agent_role: str,
        prompt: str,
        response: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Log a prompt/response interaction.

        Args:
            round_num: The current round number
            agent_name: Name of the agent
            agent_role: Role of the agent (creator, reviewer, curator)
            prompt: The prompt sent to the agent
            response: The response received from the agent
            metadata: Optional metadata about the interaction

        Returns:
            Optional dict for in-memory loggers to return the logged data

        """


class InMemoryInteractionLogger:
    """Stores interactions in memory (default for testing)."""

    def __init__(self) -> None:
        """Initialize the in-memory logger."""
        self.interactions: list[dict[str, Any]] = []

    def log_interaction(  # noqa: PLR0913
        self,
        round_num: int,
        agent_name: str,
        agent_role: str,
        prompt: str,
        response: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Store interaction in memory."""
        interaction = {
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "round": round_num,
            "agent_name": agent_name,
            "agent_role": agent_role,
            "prompt": prompt,
            "response": response,
            "metadata": metadata or {},
        }
        self.interactions.append(interaction)
        return interaction


class StreamingInteractionLogger:
    """Writes interactions to disk immediately as they happen."""

    def __init__(self, output_dir: str | Path, quiet: bool = False) -> None:
        """Initialize the streaming logger.

        Args:
            output_dir: Base directory for log files
            quiet: Suppress console output

        """
        self.output_dir: Path = Path(output_dir)
        self.quiet = quiet
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log_interaction(  # noqa: PLR0913
        self,
        round_num: int,
        agent_name: str,
        agent_role: str,
        prompt: str,
        response: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Write interaction files immediately to disk."""
        timestamp = datetime.now(tz=UTC)
        ts_str = timestamp.strftime("%Y%m%d_%H%M%S")

        # Create round directory
        round_dir = self.output_dir / f"round_{round_num}"
        round_dir.mkdir(exist_ok=True)

        # Create interaction directory with timestamp
        safe_agent_name = "".join(c if c.isalnum() else "_" for c in agent_name)
        interaction_dir = round_dir / f"{ts_str}_{safe_agent_name}_{agent_role}"
        interaction_dir.mkdir(exist_ok=True)

        # Write prompt
        with (interaction_dir / "prompt.md").open("w", encoding="utf-8") as f:
            f.write(prompt)

        # Write response
        with (interaction_dir / "response.md").open("w", encoding="utf-8") as f:
            f.write(response)

        # Write metadata as JSON
        meta = {
            "timestamp": timestamp.isoformat(),
            "round": round_num,
            "agent_name": agent_name,
            "agent_role": agent_role,
            **(metadata or {}),
        }
        with (interaction_dir / "metadata.json").open("w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, default=str)

        if not self.quiet:
            print(f"  💾 Logged: {interaction_dir}")  # noqa: T201
