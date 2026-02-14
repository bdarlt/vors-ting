"""Tests for configuration loading."""

from pathlib import Path

import pytest

from vors_ting.core.config import Config, load_config


def test_load_config(tmp_path: Path) -> None:
    """Test loading a valid configuration."""
    config_content = """
task: "Test task"
artifact_type: "adr"
agents:
  - name: "Creator1"
    role: "creator"
    model: "gpt-4"
    provider: "openai"
rounds: 3
mode: "converge"
"""

    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)

    config = load_config(config_file)

    assert config.task == "Test task"
    assert config.artifact_type == "adr"
    assert len(config.agents) == 1
    assert config.agents[0].name == "Creator1"
    assert config.rounds == 3
    assert config.mode == "converge"


def test_invalid_config(tmp_path: Path) -> None:
    """Test loading an invalid configuration."""
    config_content = """
task: "Test task"
artifact_type: "adr"
agents: []
"""

    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)

    with pytest.raises(ValueError, match="At least one agent must be configured"):
        load_config(config_file)


def test_config_validation() -> None:
    """Test configuration validation."""
    # Test valid configuration
    valid_data = {
        "task": "Test",
        "artifact_type": "adr",
        "agents": [
            {"name": "A1", "role": "creator", "model": "gpt-4", "provider": "openai"}
        ],
        "rounds": 5,
    }

    config = Config(**valid_data)
    assert config.rounds == 5

    # Test invalid rounds
    invalid_data = {**valid_data, "rounds": 0}
    with pytest.raises(ValueError, match="Rounds must be a positive integer"):
        Config(**invalid_data)
