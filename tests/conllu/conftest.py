"""Configure pytest fixtures for CONLLU tests."""

import copy

import pytest

from tests.factories.conllu import EN_SENTENCE, LA_SENTENCE


@pytest.fixture
def sentence_en_tokens() -> list[dict[str, str | int]]:
    """Provide default tokens for a valid English sentence."""
    return copy.deepcopy(EN_SENTENCE['tokens'])


@pytest.fixture
def sentence_la_tokens() -> list[dict[str, str | int]]:
    """Provide default tokens for a valid Latin sentence."""
    return copy.deepcopy(LA_SENTENCE['tokens'])
