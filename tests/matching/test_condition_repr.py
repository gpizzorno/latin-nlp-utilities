"""Tests for the Condition class string representation."""

from __future__ import annotations

from conllu_tools.matching import Condition


def test_condition_repr_simple() -> None:
    """Test __repr__ for simple condition."""
    condition = Condition(key='upos', values=['NOUN'])
    repr_str = repr(condition)

    assert 'Condition' in repr_str
    assert 'upos' in repr_str
    assert 'NOUN' in repr_str


def test_condition_repr_with_match_type() -> None:
    """Test __repr__ includes match_type when not equals."""
    condition = Condition(key='form', values=['abc'], match_type='contains')
    repr_str = repr(condition)

    assert 'contains' in repr_str


def test_condition_repr_with_match_any() -> None:
    """Test __repr__ includes match_any when True."""
    condition = Condition(key='upos', values=['NOUN', 'VERB'])
    repr_str = repr(condition)

    assert 'match_any=True' in repr_str


def test_condition_repr_with_negate() -> None:
    """Test __repr__ includes negate when True."""
    condition = Condition(key='upos', values=['NOUN'], negate=True)
    repr_str = repr(condition)

    assert 'negate=True' in repr_str


def test_condition_str_equals_repr() -> None:
    """Test that __str__ returns same as __repr__."""
    condition = Condition(key='upos', values=['NOUN'])

    assert str(condition) == repr(condition)
