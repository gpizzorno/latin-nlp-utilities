"""Tests for the Condition class match types."""

from __future__ import annotations

from typing import Any

import pytest

from conllu_tools.matching import Condition


def test_condition_test_equals_single_value_match(sample_token: dict[str, Any]) -> None:
    """Test equals match type with single matching value."""
    condition = Condition(key='upos', values=['NUM'])
    assert condition.test(sample_token) is True


def test_condition_test_equals_single_value_no_match(sample_token: dict[str, Any]) -> None:
    """Test equals match type with single non-matching value."""
    condition = Condition(key='upos', values=['NOUN'])
    assert condition.test(sample_token) is False


def test_condition_test_equals_multiple_values_match(sample_token: dict[str, Any]) -> None:
    """Test equals match type with multiple values where one matches."""
    condition = Condition(key='upos', values=['NOUN', 'NUM', 'VERB'])
    assert condition.test(sample_token) is True


def test_condition_test_equals_multiple_values_no_match(sample_token: dict[str, Any]) -> None:
    """Test equals match type with multiple values where none match."""
    condition = Condition(key='upos', values=['NOUN', 'VERB', 'ADJ'])
    assert condition.test(sample_token) is False


def test_condition_test_contains_single_value_match(sample_token: dict[str, Any]) -> None:
    """Test contains match type with matching substring."""
    condition = Condition(key='form', values=['un'], match_type='contains')
    assert condition.test(sample_token) is True


def test_condition_test_contains_single_value_no_match(sample_token: dict[str, Any]) -> None:
    """Test contains match type with non-matching substring."""
    condition = Condition(key='form', values=['xyz'], match_type='contains')
    assert condition.test(sample_token) is False


def test_condition_test_contains_multiple_values_match(sample_token: dict[str, Any]) -> None:
    """Test contains match type with multiple values where one matches."""
    condition = Condition(key='form', values=['xyz', 'num', 'abc'], match_type='contains')
    assert condition.test(sample_token) is True


def test_condition_test_startswith_match(sample_token: dict[str, Any]) -> None:
    """Test startswith match type with matching prefix."""
    condition = Condition(key='form', values=['un'], match_type='startswith')
    assert condition.test(sample_token) is True


def test_condition_test_startswith_no_match(sample_token: dict[str, Any]) -> None:
    """Test startswith match type with non-matching prefix."""
    condition = Condition(key='form', values=['num'], match_type='startswith')
    assert condition.test(sample_token) is False


def test_condition_test_startswith_multiple_values_match(sample_token: dict[str, Any]) -> None:
    """Test startswith match type with multiple values where one matches."""
    condition = Condition(key='form', values=['ab', 'un', 'xy'], match_type='startswith')
    assert condition.test(sample_token) is True


def test_condition_test_endswith_match(sample_token: dict[str, Any]) -> None:
    """Test endswith match type with matching suffix."""
    condition = Condition(key='form', values=['um'], match_type='endswith')
    assert condition.test(sample_token) is True


def test_condition_test_endswith_no_match(sample_token: dict[str, Any]) -> None:
    """Test endswith match type with non-matching suffix."""
    condition = Condition(key='form', values=['us'], match_type='endswith')
    assert condition.test(sample_token) is False


def test_condition_test_endswith_multiple_values_match(sample_token: dict[str, Any]) -> None:
    """Test endswith match type with multiple values where one matches."""
    condition = Condition(key='form', values=['us', 'um', 'ae'], match_type='endswith')
    assert condition.test(sample_token) is True


def test_condition_test_unknown_match_type_raises_error(sample_token: dict[str, Any]) -> None:
    """Test that unknown match type raises ValueError."""
    condition = Condition(key='form', values=['test'], match_type='invalid')

    with pytest.raises(ValueError, match='Unknown match type'):
        condition.test(sample_token)
