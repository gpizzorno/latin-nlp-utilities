"""Tests for DALME to UPOS converter function."""

import pytest

from conllu_tools.constants import DALME_TAGS
from conllu_tools.utils.upos import dalme_to_upos


@pytest.mark.parametrize(
    ('dalme_tag', 'expected_upos'),
    [(k, v) for k, v in DALME_TAGS.items()],
)
def test_dalme_to_upos_known_tags(dalme_tag: str, expected_upos: str) -> None:
    assert dalme_to_upos(dalme_tag) == expected_upos


@pytest.mark.parametrize(
    'unknown_tag',
    [
        'interjection',
        'conjunction',
        'foo',
        '',
        None,
        123,
    ],
)
def test_dalme_to_upos_unknown_tags(unknown_tag: str | None) -> None:
    assert dalme_to_upos(unknown_tag) == 'X'  # type: ignore [arg-type]
