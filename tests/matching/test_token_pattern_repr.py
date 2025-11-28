"""Tests for the TokenPattern class representation."""

from __future__ import annotations

from conllu_tools.matching import Condition, TokenPattern


def test_token_pattern_repr_basic() -> None:
    """Test __repr__ for basic pattern."""
    condition = Condition(key='upos', values=['NOUN'])
    pattern = TokenPattern(conditions=[condition])
    repr_str = repr(pattern)

    assert 'TokenPattern' in repr_str
    assert 'conditions' in repr_str


def test_token_pattern_repr_with_count() -> None:
    """Test __repr__ includes count when specified."""
    pattern = TokenPattern(count=2)
    repr_str = repr(pattern)

    assert 'count=2' in repr_str


def test_token_pattern_repr_with_min_max_count() -> None:
    """Test __repr__ includes min/max count when specified."""
    pattern = TokenPattern(min_count=2, max_count=5)
    repr_str = repr(pattern)

    assert 'min_count=2' in repr_str
    assert 'max_count=5' in repr_str


def test_token_pattern_repr_with_negate() -> None:
    """Test __repr__ includes negate when True."""
    condition = Condition(key='upos', values=['NOUN'])
    pattern = TokenPattern(conditions=[condition], negate=True)
    repr_str = repr(pattern)

    assert 'negate=True' in repr_str


def test_token_pattern_str_equals_repr() -> None:
    """Test that __str__ returns same as __repr__."""
    condition = Condition(key='upos', values=['NOUN'])
    pattern = TokenPattern(conditions=[condition])

    assert str(pattern) == repr(pattern)
