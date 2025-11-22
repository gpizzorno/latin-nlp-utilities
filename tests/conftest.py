"""Shared fixtures for all tests."""

from __future__ import annotations

from typing import Any

import pytest

from nlp_utilities.loaders import load_language_data


@pytest.fixture
def feature_set() -> dict[str, Any]:
    """Load Latin feature set for testing."""
    return load_language_data('feats', 'la', load_dalme=True)
