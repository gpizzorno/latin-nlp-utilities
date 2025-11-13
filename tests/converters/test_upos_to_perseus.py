"""Tests for UPOS to Perseus converter function."""

import pytest

from nlp_utilities.constants import UPOS_TO_PERSEUS
from nlp_utilities.converters.upos import upos_to_perseus


@pytest.mark.parametrize(
    ('upos_tag', 'expected'),
    [(k, v) for k, v in UPOS_TO_PERSEUS.items()],
)
def test_upos_to_perseus_known_tags(upos_tag: str, expected: str) -> None:
    assert upos_to_perseus(upos_tag) == expected


def test_upos_to_perseus_unknown_tag() -> None:
    assert upos_to_perseus('FOO') == '-'
    assert upos_to_perseus('') == '-'
    assert upos_to_perseus(None) == '-'  # type: ignore [arg-type]


def test_upos_to_perseus_case_sensitivity() -> None:
    # Should be case-sensitive: "adj" is not "ADJ"
    assert upos_to_perseus('adj') == '-'
