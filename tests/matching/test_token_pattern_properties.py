"""Tests for the TokenPattern class properties."""

from __future__ import annotations

from conllu_tools.matching import Condition, TokenPattern


def test_token_pattern_is_satisfied_when_min_count_reached() -> None:
    """Test is_satisfied returns True when min_count is reached."""
    pattern = TokenPattern(min_count=2)
    pattern.counter = 2

    assert pattern.is_satisfied is True


def test_token_pattern_is_satisfied_when_below_min_count() -> None:
    """Test is_satisfied returns False when below min_count."""
    pattern = TokenPattern(min_count=2)
    pattern.counter = 1

    assert pattern.is_satisfied is False


def test_token_pattern_is_exceeded_when_max_count_reached() -> None:
    """Test is_exceeded returns True when max_count is reached."""
    pattern = TokenPattern(max_count=3)
    pattern.counter = 3

    assert pattern.is_exceeded is True


def test_token_pattern_is_exceeded_when_below_max_count() -> None:
    """Test is_exceeded returns False when below max_count."""
    pattern = TokenPattern(max_count=3)
    pattern.counter = 2

    assert pattern.is_exceeded is False


def test_token_pattern_is_valid_with_valid_conditions() -> None:
    """Test is_valid returns True for valid conditions."""
    condition = Condition(key='upos', values=['NOUN'])
    pattern = TokenPattern(conditions=[condition])

    assert pattern.is_valid is True


def test_token_pattern_is_valid_with_empty_conditions() -> None:
    """Test is_valid returns True with no conditions (matches any)."""
    pattern = TokenPattern()

    assert pattern.is_valid is True


def test_token_pattern_match_multiple_true_when_max_count_not_one() -> None:
    """Test match_multiple is True when max_count is not 1."""
    pattern = TokenPattern(max_count=5)

    assert pattern.match_multiple is True


def test_token_pattern_match_multiple_false_when_max_count_is_one() -> None:
    """Test match_multiple is False when max_count is 1."""
    pattern = TokenPattern(max_count=1)

    assert pattern.match_multiple is False
