"""Tests for interaction logging strategies."""

import json
from pathlib import Path

from vors_ting.core.logging import (
    InMemoryInteractionLogger,
    StreamingInteractionLogger,
)


def test_in_memory_logger_stores_interactions() -> None:
    """Test that InMemoryInteractionLogger stores interactions in memory."""
    logger = InMemoryInteractionLogger()

    result = logger.log_interaction(
        round_num=0,
        agent_name="Creator1",
        agent_role="creator",
        prompt="Generate an ADR",
        response="The ADR content",
        metadata={"task": "Test task", "phase": "initial"},
    )

    # Should return the logged interaction
    assert result is not None
    assert result["round"] == 0
    assert result["agent_name"] == "Creator1"
    assert result["agent_role"] == "creator"
    assert result["prompt"] == "Generate an ADR"
    assert result["response"] == "The ADR content"
    assert result["metadata"]["phase"] == "initial"
    assert "timestamp" in result

    # Should be stored in the list
    assert len(logger.interactions) == 1
    assert logger.interactions[0] == result


def test_in_memory_logger_multiple_interactions() -> None:
    """Test logging multiple interactions."""
    logger = InMemoryInteractionLogger()

    logger.log_interaction(
        round_num=0,
        agent_name="Creator1",
        agent_role="creator",
        prompt="Generate",
        response="Content 1",
    )
    logger.log_interaction(
        round_num=1,
        agent_name="Reviewer1",
        agent_role="reviewer",
        prompt="Review",
        response='{"feedback": "Good"}',
    )

    assert len(logger.interactions) == 2
    assert logger.interactions[0]["round"] == 0
    assert logger.interactions[1]["round"] == 1


def test_streaming_logger_writes_files(tmp_path: Path) -> None:
    """Test that StreamingInteractionLogger writes files immediately."""
    output_dir = tmp_path / "interactions"
    logger = StreamingInteractionLogger(output_dir=output_dir, quiet=True)

    logger.log_interaction(
        round_num=0,
        agent_name="Creator1",
        agent_role="creator",
        prompt="Generate an ADR",
        response="The ADR content",
        metadata={"task": "Test task", "phase": "initial"},
    )

    # Check round directory was created
    round_dir = output_dir / "round_0"
    assert round_dir.exists()

    # Check interaction directory was created
    interaction_dirs = list(round_dir.iterdir())
    assert len(interaction_dirs) == 1
    interaction_dir = interaction_dirs[0]

    # Check directory name format: timestamp_agentname_role
    assert "Creator1" in interaction_dir.name
    assert "creator" in interaction_dir.name

    # Check files were created
    assert (interaction_dir / "prompt.md").exists()
    assert (interaction_dir / "response.md").exists()
    assert (interaction_dir / "metadata.json").exists()

    # Check content
    with (interaction_dir / "prompt.md").open() as f:
        assert f.read() == "Generate an ADR"

    with (interaction_dir / "response.md").open() as f:
        assert f.read() == "The ADR content"

    with (interaction_dir / "metadata.json").open() as f:
        metadata = json.load(f)
        assert metadata["round"] == 0
        assert metadata["agent_name"] == "Creator1"
        assert metadata["agent_role"] == "creator"
        assert metadata["task"] == "Test task"


def test_streaming_logger_multiple_rounds(tmp_path: Path) -> None:
    """Test streaming logger with multiple rounds."""
    output_dir = tmp_path / "interactions"
    logger = StreamingInteractionLogger(output_dir=output_dir, quiet=True)

    # Round 0
    logger.log_interaction(
        round_num=0,
        agent_name="Creator1",
        agent_role="creator",
        prompt="Generate",
        response="Content",
    )

    # Round 1 - review
    logger.log_interaction(
        round_num=1,
        agent_name="Reviewer1",
        agent_role="reviewer",
        prompt="Review",
        response='{"feedback": "Good"}',
    )

    # Round 1 - refinement
    logger.log_interaction(
        round_num=1,
        agent_name="Creator1",
        agent_role="creator",
        prompt="Refine",
        response="Refined content",
    )

    # Check directory structure
    assert (output_dir / "round_0").exists()
    assert (output_dir / "round_1").exists()

    # Round 0 should have 1 interaction
    round0_dirs = list((output_dir / "round_0").iterdir())
    assert len(round0_dirs) == 1

    # Round 1 should have 2 interactions
    round1_dirs = list((output_dir / "round_1").iterdir())
    assert len(round1_dirs) == 2


def test_streaming_logger_sanitizes_agent_names(tmp_path: Path) -> None:
    """Test that agent names with special characters are sanitized."""
    output_dir = tmp_path / "interactions"
    logger = StreamingInteractionLogger(output_dir=output_dir, quiet=True)

    logger.log_interaction(
        round_num=0,
        agent_name=r"Agent Name/With\Special<Chars>",
        agent_role="creator",
        prompt="Generate",
        response="Content",
    )

    round_dir = output_dir / "round_0"
    interaction_dirs = list(round_dir.iterdir())
    dir_name = interaction_dirs[0].name

    # Special chars should be replaced with underscores
    assert "/" not in dir_name
    assert "\\" not in dir_name
    assert "<" not in dir_name
    assert ">" not in dir_name
