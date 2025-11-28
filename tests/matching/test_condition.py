"""Tests for the Condition class."""

from __future__ import annotations

import pytest

from conllu_tools.matching import Condition


def test_condition_initialization_with_key_and_values() -> None:
    """Test basic Condition initialization with key and values."""
    condition = Condition(key='upos', values=['NOUN'])

    assert condition.key == 'upos'
    assert condition.values == ['NOUN']
    assert condition.match_type == 'equals'
    assert condition.match_any is False
    assert condition.negate is False


def test_condition_initialization_with_multiple_values_sets_match_any() -> None:
    """Test that multiple values automatically sets match_any to True."""
    condition = Condition(key='upos', values=['NOUN', 'VERB'])

    assert condition.values == ['NOUN', 'VERB']
    assert condition.match_any is True


def test_condition_initialization_with_nested_conditions() -> None:
    """Test Condition initialization with nested Condition values."""
    inner_conditions: list[str | Condition] = [
        Condition(key='Number', values=['Sing']),
        Condition(key='Case', values=['Abl']),
    ]
    condition = Condition(values=inner_conditions)

    assert condition.key is None
    assert len(condition.values) == 2
    assert condition.is_container is True


def test_condition_initialization_raises_error_without_key_and_values() -> None:
    """Test that Condition raises error when neither key nor values provided."""
    with pytest.raises(ValueError, match='requires a key and values'):
        Condition()


def test_condition_initialization_raises_error_for_non_condition_values_without_key() -> None:
    """Test error when values are strings but key is not provided."""
    with pytest.raises(ValueError, match='all values must be Condition instances'):
        Condition(values=['NOUN', 'VERB'])


def test_condition_initialization_with_match_type() -> None:
    """Test Condition initialization with different match types."""
    contains_cond = Condition(key='form', values=['abc'], match_type='contains')
    assert contains_cond.match_type == 'contains'

    startswith_cond = Condition(key='form', values=['abc'], match_type='startswith')
    assert startswith_cond.match_type == 'startswith'

    endswith_cond = Condition(key='form', values=['abc'], match_type='endswith')
    assert endswith_cond.match_type == 'endswith'


def test_condition_initialization_with_negate() -> None:
    """Test Condition initialization with negation."""
    condition = Condition(key='upos', values=['NOUN'], negate=True)

    assert condition.negate is True


def test_condition_test_with_integer_values() -> None:
    """Test condition with integer values (e.g., head, id)."""
    token = {'id': 1, 'head': 0}
    # Note: This might not work as expected since values are strings
    condition = Condition(key='head', values=['0'])
    # The test method converts to string comparison
    assert condition.test(token) is False  # Integer 0 != string '0'


def test_condition_with_empty_string_value() -> None:
    """Test condition matching empty string."""
    token = {'form': ''}
    condition = Condition(key='form', values=[''])
    assert condition.test(token) is True


def test_condition_explain_single_nested_condition() -> None:
    """Test explain method with single nested condition."""
    inner: list[str | Condition] = [Condition(key='Case', values=['Nom'])]
    condition = Condition(key='feats', values=inner)
    explanation = condition.explain()

    assert 'Case' in explanation


def test_condition_explain_two_nested_conditions() -> None:
    """Test explain method with exactly two nested conditions."""
    inner: list[str | Condition] = [
        Condition(key='Case', values=['Nom']),
        Condition(key='Number', values=['Sing']),
    ]
    condition = Condition(key='feats', values=inner)
    explanation = condition.explain()

    assert 'Case' in explanation
    assert 'Number' in explanation
