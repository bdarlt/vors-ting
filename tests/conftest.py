"""Pytest configuration and fixtures."""

import sys
from unittest.mock import MagicMock

import numpy as np
import pytest


def _create_mock_embedding(texts, **_kwargs):
    """Create mock embeddings that support convergence testing.

    Returns identical embeddings for identical texts to support convergence tests.
    """
    # Create deterministic embeddings based on text content
    # This ensures identical texts get identical embeddings
    embeddings = []
    for text in texts:
        # Use hash of text to create deterministic embedding
        hash_val = hash(text) % (2**31)  # Keep it positive
        text_rng = np.random.default_rng(hash_val)
        embedding = text_rng.random(384)
        embeddings.append(embedding)
    return np.array(embeddings)


# Patch sentence_transformers BEFORE any imports happen
_mock_model = MagicMock()
_mock_model.encode = MagicMock(side_effect=_create_mock_embedding)

_mock_st = MagicMock()
_mock_st.SentenceTransformer = MagicMock(return_value=_mock_model)

# Insert into sys.modules before any test imports
sys.modules["sentence_transformers"] = _mock_st


@pytest.fixture(scope="session", autouse=True)
def mock_sentence_transformers():
    """Mock sentence_transformers to avoid slow model loading."""
    # The module is already patched above, this fixture just ensures it stays patched
    return
