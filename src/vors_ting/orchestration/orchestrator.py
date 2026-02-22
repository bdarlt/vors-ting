"""Main orchestrator for Vörs ting."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
from rich.console import Console
from sentence_transformers import SentenceTransformer

from vors_ting.agents.creator import CreatorAgent
from vors_ting.agents.curator import CuratorAgent
from vors_ting.agents.reviewer import ReviewerAgent
from vors_ting.core.config import Config

if TYPE_CHECKING:
    from vors_ting.agents.base import BaseAgent

# Lazy-loaded embedding model (initialized on first use)
_embedding_model: SentenceTransformer | None = None


def _get_embedding_model() -> SentenceTransformer:
    """Get or initialize the embedding model."""
    global _embedding_model  # noqa: PLW0603
    if _embedding_model is None:
        # Use a lightweight model good for semantic similarity
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


def _get_artifact_extension(artifact_type: str) -> str:
    """Get file extension for artifact type."""
    extensions = {
        "adr": "md",
        "test": "py",
        "doc": "md",
        "cursor-rules": "mdc",
        "meeting": "md",
        "generic": "txt",
    }
    return extensions.get(artifact_type, "txt")


class Orchestrator:
    """Main orchestrator that manages the feedback loop."""

    def __init__(self, config: Config, quiet: bool = False) -> None:
        """Initialize the orchestrator with configuration."""
        self.config = config
        self.agents: list[BaseAgent] = []
        self.round_history: list[dict[str, Any]] = []
        self.current_round = 0
        self.quiet = quiet
        self.console = Console(quiet=quiet)
        self._output_dir: Path | None = None
        self._run_timestamp: str = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")

    def _get_output_dir(self) -> Path:
        """Get or create the output directory."""
        if self._output_dir is None:
            # Use metrics.log_dir from config, default to 'metrics/'
            log_dir = self.config.metrics.log_dir or "metrics/"
            self._output_dir = Path(log_dir) / self._run_timestamp
            self._output_dir.mkdir(parents=True, exist_ok=True)
        return self._output_dir

    def _log(self, message: str, style: str | None = None) -> None:
        """Log a message if not in quiet mode."""
        if not self.quiet:
            if style:
                self.console.print(message, style=style)
            else:
                self.console.print(message)

    def _preview_text(self, text: str, lines: int = 4) -> str:
        """Get first N lines of text for preview."""
        text_lines = text.strip().split("\n")
        preview_lines = text_lines[:lines]
        result = "\n".join(preview_lines)
        if len(text_lines) > lines:
            result += f"\n... ({len(text_lines) - lines} more lines)"
        return result

    def initialize_agents(self) -> None:
        """Initialize agents based on configuration."""
        agent_count = len(self.config.agents)
        self._log(f"Initializing {agent_count} agents...", style="bold blue")

        for agent_config in self.config.agents:
            self._log(f"  Creating {agent_config.role}: {agent_config.name}")

            if agent_config.role == "creator":
                agent = CreatorAgent(
                    name=agent_config.name,
                    role=agent_config.role,
                    model=agent_config.model,
                    provider=agent_config.provider,
                    temperature=agent_config.temperature,
                    system_prompt=agent_config.system_prompt,
                )
            elif agent_config.role == "reviewer":
                agent = ReviewerAgent(
                    name=agent_config.name,
                    role=agent_config.role,
                    model=agent_config.model,
                    provider=agent_config.provider,
                    temperature=agent_config.temperature,
                    system_prompt=agent_config.system_prompt,
                )
            elif agent_config.role == "curator":
                agent = CuratorAgent(
                    name=agent_config.name,
                    role=agent_config.role,
                    model=agent_config.model,
                    provider=agent_config.provider,
                    temperature=agent_config.temperature,
                    system_prompt=agent_config.system_prompt,
                )
            else:
                error_msg = f"Unknown agent role: {agent_config.role}"
                raise ValueError(error_msg)

            self.agents.append(agent)

        self._log("Agents initialized.\n", style="green")

    def run(self) -> dict[str, Any]:
        """Run the feedback loop."""
        result: dict[str, Any] = {}
        try:
            if self.config.mode == "converge":
                result = self._run_converge_mode()
            else:
                result = self._run_diverge_mode()
        except Exception:
            # Save state even on error, then re-raise
            self._auto_save()
            raise
        else:
            # Auto-save results on success
            self._auto_save()
        return result

    def _run_converge_mode(self) -> dict[str, Any]:
        """Run the convergence mode."""
        # Initialize agents
        self.initialize_agents()

        # Round 0: Initial generation
        self._log("=" * 50, style="bold")
        self._log("ROUND 0: Initial Generation", style="bold yellow")
        self._log("=" * 50, style="bold")

        initial_artifacts = self._initial_generation()
        self._log_round(0, {"artifacts": initial_artifacts})

        # Subsequent rounds
        for round_num in range(1, self.config.rounds + 1):
            self.current_round = round_num

            self._log("\n" + "=" * 50, style="bold")
            self._log(f"ROUND {round_num}", style="bold yellow")
            self._log("=" * 50, style="bold")

            # Review phase
            reviews = self._review_phase(initial_artifacts)

            # Refine phase
            refined_artifacts = self._refine_phase(initial_artifacts, reviews)

            # Check convergence
            if self._check_convergence(initial_artifacts, refined_artifacts):
                self._log("\n✓ Convergence reached!", style="bold green")
                self._log_round(
                    round_num,
                    {
                        "reviews": reviews,
                        "artifacts": refined_artifacts,
                        "converged": True,
                    },
                )
                return {"status": "converged", "artifacts": refined_artifacts}

            threshold = self.config.convergence.similarity_threshold
            self._log(f"\nNot converged yet (threshold: {threshold})")

            self._log_round(
                round_num, {"reviews": reviews, "artifacts": refined_artifacts}
            )

            initial_artifacts = refined_artifacts

        self._log(f"\nMax rounds ({self.config.rounds}) reached.", style="bold yellow")
        return {"status": "max_rounds_reached", "artifacts": initial_artifacts}

    def _run_diverge_mode(self) -> dict[str, Any]:
        """Run the divergence mode."""
        # TODO: Implement divergence mode
        error_msg = "Divergence mode not yet implemented"
        raise NotImplementedError(error_msg)

    def _initial_generation(self) -> list[str]:
        """Generate initial artifacts."""
        artifacts = []
        for agent in self.agents:
            if agent.role == "creator":
                self._log(f"\n→ Prompting {agent.name} ({agent.model})", style="cyan")
                self._log(f"  Task: {self.config.task[:60]}...")

                # Build prompt
                prompt = agent._build_generation_prompt(self.config.task)  # noqa: SLF001

                artifact = agent.generate(self.config.task)
                artifacts.append(artifact)

                # Log the interaction
                self._log_interaction(
                    round_num=0,
                    agent_name=agent.name,
                    agent_role="creator",
                    prompt=prompt,
                    response=artifact,
                    metadata={"task": self.config.task, "phase": "initial"},
                )

                self._log(f"  ✓ Received response from {agent.name}", style="green")
                self._log("  Preview:")
                self._log(self._preview_text(artifact))

        return artifacts

    def _review_phase(self, artifacts: list[str]) -> list[dict[str, Any]]:
        """Perform the review phase."""
        self._log("\n--- Review Phase ---", style="bold magenta")
        reviews = []
        rubric = self.config.rubric.model_dump() if self.config.rubric else None

        for artifact in artifacts:
            for agent in self.agents:
                if agent.role == "reviewer":
                    self._log(
                        f"\n→ Connecting with LLM - {agent.name} ({agent.model})",
                        style="cyan",
                    )
                    self._log("  Reviewing artifact...")

                    # Build prompt
                    prompt = agent._build_review_prompt(artifact, rubric)  # noqa: SLF001

                    review = agent.review(artifact, rubric)
                    reviews.append(review)

                    # Log the interaction
                    self._log_interaction(
                        round_num=self.current_round,
                        agent_name=agent.name,
                        agent_role="reviewer",
                        prompt=prompt,
                        response=json.dumps(review, indent=2),
                        metadata={
                            "phase": "review",
                            "rubric": rubric,
                            "artifact_index": artifacts.index(artifact),
                        },
                    )

                    self._log(f"  ✓ Feedback received from {agent.name}", style="green")
                    feedback_text = review.get("feedback", "")
                    feedback_preview = self._preview_text(feedback_text, lines=3)
                    self._log(f"  Feedback preview: {feedback_preview[:100]}...")

        return reviews

    def _refine_phase(
        self, artifacts: list[str], reviews: list[dict[str, Any]]
    ) -> list[str]:
        """Perform the refinement phase."""
        self._log("\n--- Refinement Phase ---", style="bold magenta")
        refined_artifacts = []

        for i, artifact in enumerate(artifacts):
            # Get relevant reviews for this artifact
            artifact_reviews = [
                reviews[j] for j in range(i, len(reviews), len(artifacts))
            ]

            # Find a creator to refine
            for agent in self.agents:
                if agent.role == "creator":
                    self._log(
                        f"\n→ Prompting {agent.name} to refine artifact",
                        style="cyan",
                    )
                    self._log(f"  Incorporating {len(artifact_reviews)} review(s)...")

                    # Build prompt
                    prompt = agent._build_refinement_prompt(  # noqa: SLF001
                        artifact, {"reviews": artifact_reviews}
                    )

                    refined = agent.refine(artifact, {"reviews": artifact_reviews})
                    refined_artifacts.append(refined)

                    # Log the interaction
                    self._log_interaction(
                        round_num=self.current_round,
                        agent_name=agent.name,
                        agent_role="creator",
                        prompt=prompt,
                        response=refined,
                        metadata={
                            "phase": "refinement",
                            "artifact_index": i,
                            "reviews": artifact_reviews,
                        },
                    )

                    self._log(f"  ✓ Refined by {agent.name}", style="green")
                    self._log("  Preview:")
                    self._log(self._preview_text(refined))
                    break

        return refined_artifacts

    def _check_convergence(
        self, old_artifacts: list[str], new_artifacts: list[str]
    ) -> bool:
        """Check if artifacts have converged using semantic similarity.

        Compares each old artifact with its corresponding new artifact
        using cosine similarity of embeddings. Converged if all pairs
        exceed the configured threshold.

        Args:
            old_artifacts: Artifacts from previous round
            new_artifacts: Refined artifacts from current round

        Returns:
            True if all artifacts have converged, False otherwise

        """
        if len(old_artifacts) != len(new_artifacts):
            return False

        if not old_artifacts:
            return True  # No artifacts means trivial convergence

        # Get embeddings for all artifacts
        model = _get_embedding_model()
        old_embeddings = model.encode(old_artifacts, convert_to_numpy=True)
        new_embeddings = model.encode(new_artifacts, convert_to_numpy=True)

        # Compute cosine similarity for each pair
        threshold = self.config.convergence.similarity_threshold
        for old_emb, new_emb in zip(old_embeddings, new_embeddings, strict=True):
            similarity = float(
                np.dot(old_emb, new_emb)
                / (np.linalg.norm(old_emb) * np.linalg.norm(new_emb))
            )
            if similarity < threshold:
                return False

        return True

    def _log_round(self, round_num: int, data: dict[str, Any]) -> None:
        """Log round data."""
        round_data = {"round": round_num, **data}
        self.round_history.append(round_data)

    def _log_interaction(  # noqa: PLR0913
        self,
        round_num: int,
        agent_name: str,
        agent_role: str,
        prompt: str,
        response: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log a prompt/response interaction."""
        interaction = {
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "round": round_num,
            "agent_name": agent_name,
            "agent_role": agent_role,
            "prompt": prompt,
            "response": response,
            "metadata": metadata or {},
        }

        # Add to round history if not already there
        if self.round_history:
            if "interactions" not in self.round_history[-1]:
                self.round_history[-1]["interactions"] = []
            self.round_history[-1]["interactions"].append(interaction)

    def _auto_save(self) -> Path:
        """Auto-save the current state to the configured log directory."""
        output_dir = self._get_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save full run history with prompts/responses
        with (output_dir / "run_history.json").open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "config": {
                        "task": self.config.task,
                        "artifact_type": self.config.artifact_type,
                        "mode": self.config.mode,
                        "rounds": self.config.rounds,
                        "agents": [
                            {
                                "name": a.name,
                                "role": a.role,
                                "model": a.model,
                                "provider": a.provider,
                            }
                            for a in self.config.agents
                        ],
                    },
                    "run_timestamp": self._run_timestamp,
                    "rounds_completed": self.current_round,
                    "round_history": self.round_history,
                },
                f,
                indent=2,
                default=str,
            )

        # Save final artifacts with proper extension
        ext = _get_artifact_extension(self.config.artifact_type)
        if self.round_history:
            final_artifacts = self.round_history[-1].get("artifacts", [])
            for i, artifact in enumerate(final_artifacts):
                with (output_dir / f"artifact_{i}.{ext}").open(
                    "w", encoding="utf-8"
                ) as f:
                    f.write(artifact)

        # Create a summary file
        with (output_dir / "summary.txt").open("w", encoding="utf-8") as f:
            f.write("Vörs ting Run Summary\n")
            f.write("====================\n\n")
            f.write(f"Timestamp: {self._run_timestamp}\n")
            f.write(f"Task: {self.config.task}\n")
            f.write(f"Artifact Type: {self.config.artifact_type}\n")
            f.write(f"Mode: {self.config.mode}\n")
            f.write(f"Rounds Completed: {self.current_round}\n")
            f.write(f"Total Rounds Configured: {self.config.rounds}\n\n")

            if self.round_history:
                final = self.round_history[-1]
                status = "Converged" if final.get("converged") else "Max rounds reached"
                f.write(f"Final Status: {status}\n")
                f.write(f"Artifacts Generated: {len(final.get('artifacts', []))}\n")

        if not self.quiet:
            self._log(f"\nResults saved to: {output_dir}", style="bold green")

        return output_dir

    def save_state(self, output_dir: Path) -> None:
        """Save the current state to a specific directory (legacy/override).

        This maintains backward compatibility with explicit --output usage,
        saving only round_history.json and artifact files (not full prompts).
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save round history (legacy format)
        with (output_dir / "round_history.json").open("w", encoding="utf-8") as f:
            json.dump(self.round_history, f, indent=2, default=str)

        # Save final artifacts
        if self.round_history:
            final_artifacts = self.round_history[-1].get("artifacts", [])
            for i, artifact in enumerate(final_artifacts):
                ext = _get_artifact_extension(self.config.artifact_type)
                with (output_dir / f"artifact_{i}.{ext}").open(
                    "w", encoding="utf-8"
                ) as f:
                    f.write(artifact)
