"""Main orchestrator for Vörs ting."""

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from vors_ting.agents.creator import CreatorAgent
from vors_ting.agents.curator import CuratorAgent
from vors_ting.agents.reviewer import ReviewerAgent
from vors_ting.core.config import Config

if TYPE_CHECKING:
    from vors_ting.agents.base import BaseAgent


class Orchestrator:
    """Main orchestrator that manages the feedback loop."""

    def __init__(self, config: Config) -> None:
        """Initialize the orchestrator with configuration."""
        self.config = config
        self.agents: list[BaseAgent] = []
        self.round_history: list[dict[str, Any]] = []
        self.current_round = 0

    def initialize_agents(self) -> None:
        """Initialize agents based on configuration."""
        for agent_config in self.config.agents:
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

    def run(self) -> dict[str, Any]:
        """Run the feedback loop."""
        if self.config.mode == "converge":
            return self._run_converge_mode()
        return self._run_diverge_mode()

    def _run_converge_mode(self) -> dict[str, Any]:
        """Run the convergence mode."""
        # Initialize agents
        self.initialize_agents()

        # Round 0: Initial generation
        initial_artifacts = self._initial_generation()
        self._log_round(0, {"artifacts": initial_artifacts})

        # Subsequent rounds
        for round_num in range(1, self.config.rounds + 1):
            self.current_round = round_num

            # Review phase
            reviews = self._review_phase(initial_artifacts)

            # Refine phase
            refined_artifacts = self._refine_phase(initial_artifacts, reviews)

            # Check convergence
            if self._check_convergence(initial_artifacts, refined_artifacts):
                self._log_round(
                    round_num,
                    {
                        "reviews": reviews,
                        "artifacts": refined_artifacts,
                        "converged": True,
                    },
                )
                return {"status": "converged", "artifacts": refined_artifacts}

            self._log_round(
                round_num, {"reviews": reviews, "artifacts": refined_artifacts}
            )

            initial_artifacts = refined_artifacts

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
                artifact = agent.generate(self.config.task)
                artifacts.append(artifact)
        return artifacts

    def _review_phase(self, artifacts: list[str]) -> list[dict[str, Any]]:
        """Perform the review phase."""
        reviews = []
        rubric = self.config.rubric.dict() if self.config.rubric else None

        for artifact in artifacts:
            for agent in self.agents:
                if agent.role == "reviewer":
                    review = agent.review(artifact, rubric)
                    reviews.append(review)

        return reviews

    def _refine_phase(
        self, artifacts: list[str], reviews: list[dict[str, Any]]
    ) -> list[str]:
        """Perform the refinement phase."""
        refined_artifacts = []

        for i, artifact in enumerate(artifacts):
            # Get relevant reviews for this artifact
            artifact_reviews = [
                reviews[j] for j in range(i, len(reviews), len(artifacts))
            ]

            # Find a creator to refine
            for agent in self.agents:
                if agent.role == "creator":
                    refined = agent.refine(artifact, {"reviews": artifact_reviews})
                    refined_artifacts.append(refined)
                    break

        return refined_artifacts

    def _check_convergence(
        self, old_artifacts: list[str], new_artifacts: list[str]
    ) -> bool:
        """Check if artifacts have converged."""
        # TODO: Implement proper convergence checking
        del old_artifacts, new_artifacts  # Unused arguments
        return False

    def _log_round(self, round_num: int, data: dict[str, Any]) -> None:
        """Log round data."""
        round_data = {"round": round_num, **data}
        self.round_history.append(round_data)

    def save_state(self, output_dir: Path) -> None:
        """Save the current state to disk."""

        output_dir.mkdir(parents=True, exist_ok=True)

        # Save round history
        with (output_dir / "round_history.json").open("w", encoding="utf-8") as f:
            json.dump(self.round_history, f, indent=2)

        # Save final artifacts
        if self.round_history:
            final_artifacts = self.round_history[-1].get("artifacts", [])
            for i, artifact in enumerate(final_artifacts):
                with (output_dir / f"artifact_{i}.txt").open(
                    "w", encoding="utf-8"
                ) as f:
                    f.write(artifact)
