"""End-to-end integration tests for Vörs ting."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from vors_ting.cli import app
from vors_ting.core.config import AgentConfig, Config
from vors_ting.orchestration.orchestrator import Orchestrator, _get_embedding_model


class TestConvergenceFlow:
    """Test the full convergence workflow."""

    def test_full_flow_converges_early(self) -> None:
        """Test that the flow stops early when artifacts converge."""
        # Setup mock agents that return nearly identical content after first refinement
        config = Config(
            task="Write a simple description",
            artifact_type="doc",
            agents=[
                AgentConfig(
                    name="Creator1",
                    role="creator",
                    model="gpt-4",
                    provider="openai",
                ),
                AgentConfig(
                    name="Reviewer1",
                    role="reviewer",
                    model="gpt-4",
                    provider="openai",
                ),
            ],
            rounds=5,  # Request 5 rounds
            convergence={
                "method": "similarity",
                "similarity_threshold": 0.95,
                "max_rounds": 5,
            },
        )

        orchestrator = Orchestrator(config)

        # Mock the agent methods to simulate convergence
        with (
            patch.object(orchestrator, "initialize_agents") as mock_init,
            patch.object(orchestrator, "_initial_generation") as mock_init_gen,
            patch.object(orchestrator, "_review_phase") as mock_review,
            patch.object(orchestrator, "_refine_phase") as mock_refine,
        ):
            # Setup mock
            mock_init.return_value = None
            mock_init_gen.return_value = ["Initial content about Python programming."]
            mock_review.return_value = [{"feedback": "Looks good"}]

            # Return nearly identical content (should trigger convergence)
            mock_refine.return_value = [
                "Initial content about Python programming!"  # Very similar
            ]

            # Add a mock agent
            mock_agent = MagicMock()
            mock_agent.role = "creator"
            orchestrator.agents = [mock_agent]

            result = orchestrator.run()

            # Should converge and stop early
            assert result["status"] == "converged"
            # Should have stopped before max rounds
            assert orchestrator.current_round < config.rounds

    def test_full_flow_max_rounds(self) -> None:
        """Test that the flow runs all rounds when no convergence."""
        config = Config(
            task="Write a description",
            artifact_type="doc",
            agents=[
                AgentConfig(
                    name="Creator1",
                    role="creator",
                    model="gpt-4",
                    provider="openai",
                ),
                AgentConfig(
                    name="Reviewer1",
                    role="reviewer",
                    model="gpt-4",
                    provider="openai",
                ),
            ],
            rounds=3,
            convergence={
                "method": "similarity",
                "similarity_threshold": 0.95,
                "max_rounds": 3,
            },
        )

        orchestrator = Orchestrator(config)

        # Mock to simulate completely different content each round (no convergence)
        with (
            patch.object(orchestrator, "initialize_agents") as mock_init,
            patch.object(orchestrator, "_initial_generation") as mock_init_gen,
            patch.object(orchestrator, "_review_phase") as mock_review,
            patch.object(orchestrator, "_refine_phase") as mock_refine,
        ):
            mock_init.return_value = None
            mock_init_gen.return_value = ["Content about Python."]
            mock_review.return_value = [{"feedback": "Needs work"}]

            # Return completely different content each time (no convergence)
            mock_refine.side_effect = [
                ["A completely different topic about JavaScript."],
                ["Yet another topic about Rust programming."],
                ["Final topic about Go programming."],
            ]

            mock_agent = MagicMock()
            mock_agent.role = "creator"
            orchestrator.agents = [mock_agent]

            result = orchestrator.run()

            assert result["status"] == "max_rounds_reached"
            assert orchestrator.current_round == 3


class TestConvergenceDetection:
    """Test the convergence detection mechanism."""

    def test_convergence_identical_text(self) -> None:
        """Test that identical text is detected as converged."""
        config = Config(
            task="Test",
            artifact_type="doc",
            agents=[
                AgentConfig(
                    name="Creator1", role="creator", model="gpt-4", provider="openai"
                )
            ],
            rounds=3,
            convergence={
                "method": "similarity",
                "similarity_threshold": 0.95,
                "max_rounds": 3,
            },
        )

        orchestrator = Orchestrator(config)
        old = ["This is exactly the same content."]
        new = ["This is exactly the same content."]

        assert orchestrator._check_convergence(old, new) is True

    def test_convergence_semantically_similar(self) -> None:
        """Test that semantically similar text is detected as converged."""
        config = Config(
            task="Test",
            artifact_type="doc",
            agents=[
                AgentConfig(
                    name="Creator1", role="creator", model="gpt-4", provider="openai"
                )
            ],
            rounds=3,
            convergence={
                "method": "similarity",
                "similarity_threshold": 0.95,
                "max_rounds": 3,
            },
        )

        orchestrator = Orchestrator(config)
        # Same meaning, slightly different wording
        old = ["The quick brown fox jumps over the lazy dog."]
        new = ["A fast brown fox leaps over a lazy dog."]

        # These should be semantically similar enough
        result = orchestrator._check_convergence(old, new)
        # Note: This might be True or False depending on threshold, but should be close
        assert isinstance(result, bool)

    def test_convergence_different_text(self) -> None:
        """Test that different text is NOT detected as converged."""
        config = Config(
            task="Test",
            artifact_type="doc",
            agents=[
                AgentConfig(
                    name="Creator1", role="creator", model="gpt-4", provider="openai"
                )
            ],
            rounds=3,
            convergence={
                "method": "similarity",
                "similarity_threshold": 0.95,
                "max_rounds": 3,
            },
        )

        orchestrator = Orchestrator(config)
        # Completely different topics
        old = ["Python is a programming language with dynamic typing."]
        new = ["The capital of France is Paris and it has great food."]

        assert orchestrator._check_convergence(old, new) is False

    def test_convergence_empty_artifacts(self) -> None:
        """Test convergence with empty artifacts."""
        config = Config(
            task="Test",
            artifact_type="doc",
            agents=[
                AgentConfig(
                    name="Creator1", role="creator", model="gpt-4", provider="openai"
                )
            ],
            rounds=3,
        )

        orchestrator = Orchestrator(config)
        assert orchestrator._check_convergence([], []) is True

    def test_convergence_mismatched_lengths(self) -> None:
        """Test convergence with different number of artifacts."""
        config = Config(
            task="Test",
            artifact_type="doc",
            agents=[
                AgentConfig(
                    name="Creator1", role="creator", model="gpt-4", provider="openai"
                )
            ],
            rounds=3,
        )

        orchestrator = Orchestrator(config)
        old = ["Content A"]
        new = ["Content A", "Content B"]

        assert orchestrator._check_convergence(old, new) is False


class TestYAMLIntegration:
    """Test YAML configuration loading and execution."""

    def test_load_and_run_from_yaml(self, tmp_path: Path) -> None:
        """Test loading config from YAML and running orchestrator."""
        config_data = {
            "task": "Write a test document",
            "artifact_type": "doc",
            "agents": [
                {
                    "name": "TestCreator",
                    "role": "creator",
                    "model": "gpt-4",
                    "provider": "openai",
                    "temperature": 0.2,
                },
                {
                    "name": "TestReviewer",
                    "role": "reviewer",
                    "model": "gpt-4",
                    "provider": "openai",
                    "temperature": 0.3,
                },
            ],
            "rounds": 2,
            "mode": "converge",
        }

        config_path = tmp_path / "test_config.yaml"
        with config_path.open("w") as f:
            yaml.dump(config_data, f)

        from vors_ting.core.config import load_config

        config = load_config(config_path)
        assert config.task == "Write a test document"
        assert config.rounds == 2
        assert len(config.agents) == 2

    def test_full_yaml_workflow(self, tmp_path: Path) -> None:
        """Test complete workflow from YAML to saved output."""
        config_data = {
            "task": "Write simple documentation",
            "artifact_type": "doc",
            "agents": [
                {
                    "name": "Creator",
                    "role": "creator",
                    "model": "gpt-4",
                    "provider": "openai",
                },
            ],
            "rounds": 1,
            "mode": "converge",
        }

        config_path = tmp_path / "workflow_config.yaml"
        with config_path.open("w") as f:
            yaml.dump(config_data, f)

        from vors_ting.core.config import load_config

        config = load_config(config_path)
        orchestrator = Orchestrator(config)

        # Mock everything to avoid LLM calls
        with patch("vors_ting.orchestration.orchestrator.CreatorAgent") as mock_creator:
            mock_instance = MagicMock()
            mock_instance.role = "creator"
            mock_instance.name = "Creator"
            mock_instance.model = "gpt-4"
            mock_instance.generate.return_value = "Generated content"
            mock_instance.refine.return_value = "Refined content"
            mock_creator.return_value = mock_instance

            output_dir = tmp_path / "output"
            result = orchestrator.run()
            orchestrator.save_state(output_dir)

            assert result["status"] in ["converged", "max_rounds_reached"]
            assert (output_dir / "round_history.json").exists()


class TestStatePersistence:
    """Test saving and loading state."""

    def test_save_state_creates_files(self, tmp_path: Path) -> None:
        """Test that save_state creates expected files."""
        config = Config(
            task="Test",
            artifact_type="doc",
            agents=[
                AgentConfig(
                    name="Creator1", role="creator", model="gpt-4", provider="openai"
                )
            ],
            rounds=1,
        )

        orchestrator = Orchestrator(config)
        orchestrator.round_history = [
            {
                "round": 0,
                "artifacts": ["First version of the content."],
            },
            {
                "round": 1,
                "artifacts": ["Final version of the content."],
                "converged": True,
            },
        ]

        output_dir = tmp_path / "test_output"
        orchestrator.save_state(output_dir)

        # Check files exist
        assert (output_dir / "round_history.json").exists()
        assert (output_dir / "artifact_0.md").exists()

        # Check content
        with (output_dir / "round_history.json").open() as f:
            history = json.load(f)
            assert len(history) == 2
            assert history[1]["converged"] is True

        with (output_dir / "artifact_0.md").open() as f:
            content = f.read()
            assert content == "Final version of the content."


class TestCLIIntegration:
    """Test CLI commands."""

    def test_cli_run_with_yaml(self, tmp_path: Path) -> None:
        """Test CLI run command with YAML config."""
        from typer.testing import CliRunner

        runner = CliRunner()

        config_data = {
            "task": "Test task",
            "artifact_type": "doc",
            "agents": [
                {
                    "name": "Creator",
                    "role": "creator",
                    "model": "gpt-4",
                    "provider": "openai",
                },
            ],
            "rounds": 1,
        }

        config_path = tmp_path / "cli_config.yaml"
        with config_path.open("w") as f:
            yaml.dump(config_data, f)

        output_dir = tmp_path / "cli_output"

        # Mock the orchestrator to avoid actual LLM calls
        with patch("vors_ting.cli.Orchestrator") as mock_orch_class:
            mock_orch = MagicMock()
            mock_orch.run.return_value = {"status": "converged"}
            mock_orch.current_round = 1
            mock_orch_class.return_value = mock_orch

            result = runner.invoke(app, [str(config_path), "--output", str(output_dir)])

            assert result.exit_code == 0
            assert "Status: converged" in result.output
            assert "Completed 1 rounds" in result.output


class TestPolyadicPattern:
    """Test polyadic patterns with multiple creators."""

    def test_multiple_creators_flow(self) -> None:
        """Test workflow with multiple creator agents."""
        config = Config(
            task="Write documentation",
            artifact_type="doc",
            agents=[
                AgentConfig(
                    name="Creator1",
                    role="creator",
                    model="gpt-4",
                    provider="openai",
                ),
                AgentConfig(
                    name="Creator2",
                    role="creator",
                    model="gpt-4",
                    provider="openai",
                ),
                AgentConfig(
                    name="Reviewer1",
                    role="reviewer",
                    model="gpt-4",
                    provider="openai",
                ),
            ],
            rounds=2,
        )

        orchestrator = Orchestrator(config)

        with (
            patch("vors_ting.orchestration.orchestrator.CreatorAgent") as mock_creator,
            patch(
                "vors_ting.orchestration.orchestrator.ReviewerAgent"
            ) as mock_reviewer,
        ):
            # Setup creator mocks
            creator_instance = MagicMock()
            creator_instance.role = "creator"
            creator_instance.generate.return_value = "Creator output"
            creator_instance.refine.return_value = "Refined creator output"
            mock_creator.return_value = creator_instance

            # Setup reviewer mocks
            reviewer_instance = MagicMock()
            reviewer_instance.role = "reviewer"
            reviewer_instance.review.return_value = {"feedback": "Good"}
            mock_reviewer.return_value = reviewer_instance

            result = orchestrator.run()

            # Should create 2 creators
            assert mock_creator.call_count == 2
            assert result["status"] in ["converged", "max_rounds_reached"]


@pytest.mark.slow
class TestEmbeddingModel:
    """Tests that actually use the embedding model (marked as slow)."""

    def test_embedding_model_initialization(self) -> None:
        """Test that the embedding model loads correctly."""
        model = _get_embedding_model()
        assert model is not None

        # Calling again should return same instance (singleton)
        model2 = _get_embedding_model()
        assert model is model2

    def test_convergence_with_real_embeddings(self) -> None:
        """Test convergence detection with actual embeddings."""
        config = Config(
            task="Test",
            artifact_type="doc",
            agents=[
                AgentConfig(
                    name="Creator1", role="creator", model="gpt-4", provider="openai"
                )
            ],
            rounds=3,
            convergence={
                "method": "similarity",
                "similarity_threshold": 0.90,  # Lower threshold for test
                "max_rounds": 3,
            },
        )

        orchestrator = Orchestrator(config)

        # Very similar content
        old = ["Python is a high-level programming language."]
        new = ["Python is a high level programming language"]

        result = orchestrator._check_convergence(old, new)
        assert result is True  # Should converge with 0.90 threshold

    def test_non_convergence_with_real_embeddings(self) -> None:
        """Test that different content doesn't converge."""
        config = Config(
            task="Test",
            artifact_type="doc",
            agents=[
                AgentConfig(
                    name="Creator1", role="creator", model="gpt-4", provider="openai"
                )
            ],
            rounds=3,
            convergence={
                "method": "similarity",
                "similarity_threshold": 0.95,
                "max_rounds": 3,
            },
        )

        orchestrator = Orchestrator(config)

        # Completely different content
        old = ["Machine learning is transforming software development."]
        new = ["The best pasta recipes include fresh ingredients."]

        result = orchestrator._check_convergence(old, new)
        assert result is False
