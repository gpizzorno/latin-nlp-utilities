"""Tests for validate_xpos function."""

import pytest

from nlp_utilities.validators import validate_xpos


def test_validate_xpos_requires_upos() -> None:
    """Test that UPOS is required."""
    with pytest.raises(ValueError, match='UPOS must be provided'):
        validate_xpos(None, 'n-s---mn-')  # type: ignore [arg-type]


def test_validate_xpos_none_xpos_noun() -> None:
    """Test with None XPOS for noun."""
    result = validate_xpos('NOUN', None)
    assert result == 'n--------'
    assert len(result) == 9


def test_validate_xpos_none_xpos_verb() -> None:
    """Test with None XPOS for verb."""
    result = validate_xpos('VERB', None)
    assert result == 'v--------'


def test_validate_xpos_none_xpos_adj() -> None:
    """Test with None XPOS for adjective."""
    result = validate_xpos('ADJ', None)
    assert result == 'a--------'


def test_validate_xpos_valid_noun_xpos() -> None:
    """Test with valid noun XPOS."""
    result = validate_xpos('NOUN', 'n-s---mn-')
    assert result == 'n-s---mn-'


def test_validate_xpos_valid_verb_xpos() -> None:
    """Test with valid verb XPOS."""
    result = validate_xpos('VERB', 'v3spia---')
    assert result == 'v3spia---'


def test_validate_xpos_returns_9_chars() -> None:
    """Test that result is always 9 characters."""
    test_cases = [
        ('NOUN', None),
        ('NOUN', 'n-s---mn-'),
        ('VERB', 'v3spia---'),
        ('NOUN', 'invalid'),
        ('NOUN', 'n-s'),  # Too short
    ]
    for upos, xpos in test_cases:
        result = validate_xpos(upos, xpos)
        assert len(result) == 9, f'Expected 9 chars for {upos}/{xpos}, got {len(result)}'
