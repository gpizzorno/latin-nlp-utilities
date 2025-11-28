"""Tests for the matching utility functions."""

from __future__ import annotations

import pytest

from conllu_tools.matching.utils import (
    _format_value,
    _get_match_value,
    _parse_conditions,
)


def test_format_value_single() -> None:
    """Test _format_value with single value."""
    assert _format_value('NOUN') == ['NOUN']


def test_format_value_multiple() -> None:
    """Test _format_value with pipe-separated values."""
    assert _format_value('NOUN|VERB') == ['NOUN', 'VERB']


def test_format_value_multiple_three() -> None:
    """Test _format_value with three pipe-separated values."""
    assert _format_value('NOUN|VERB|ADJ') == ['NOUN', 'VERB', 'ADJ']


def test_format_value_empty() -> None:
    """Test _format_value with empty string."""
    assert _format_value('') == ['']


def test_get_match_value_equals() -> None:
    """Test _get_match_value returns equals for plain value."""
    negation, match_type, values = _get_match_value('NOUN')
    assert negation is False
    assert match_type == 'equals'
    assert values == ['NOUN']


def test_get_match_value_contains() -> None:
    """Test _get_match_value returns contains for <value>."""
    negation, match_type, values = _get_match_value('<part>')
    assert negation is False
    assert match_type == 'contains'
    assert values == ['part']


def test_get_match_value_startswith() -> None:
    """Test _get_match_value returns startswith for <value."""
    negation, match_type, values = _get_match_value('<pre')
    assert negation is False
    assert match_type == 'startswith'
    assert values == ['pre']


def test_get_match_value_endswith() -> None:
    """Test _get_match_value returns endswith for value>."""
    negation, match_type, values = _get_match_value('tion>')
    assert negation is False
    assert match_type == 'endswith'
    assert values == ['tion']


def test_get_match_value_negation_equals() -> None:
    """Test _get_match_value with negation."""
    negation, match_type, values = _get_match_value('!NOUN')
    assert negation is True
    assert match_type == 'equals'
    assert values == ['NOUN']


def test_get_match_value_negation_contains() -> None:
    """Test _get_match_value with negation and contains."""
    negation, match_type, values = _get_match_value('!<part>')
    assert negation is True
    assert match_type == 'contains'
    assert values == ['part']


def test_get_match_value_with_pipe() -> None:
    """Test _get_match_value with pipe-separated values."""
    negation, match_type, values = _get_match_value('NOUN|VERB')
    assert negation is False
    assert match_type == 'equals'
    assert values == ['NOUN', 'VERB']


def test_parse_conditions_simple() -> None:
    """Test _parse_conditions with simple key=value condition."""
    conditions = _parse_conditions(['lemma=test'])
    assert len(conditions) == 1
    assert conditions[0].key == 'lemma'
    assert conditions[0].values == ['test']
    assert conditions[0].match_type == 'equals'


def test_parse_conditions_contains() -> None:
    """Test _parse_conditions with contains match."""
    conditions = _parse_conditions(['lemma=<part>'])
    assert len(conditions) == 1
    assert conditions[0].match_type == 'contains'


def test_parse_conditions_negation() -> None:
    """Test _parse_conditions with negation."""
    conditions = _parse_conditions(['lemma=!test'])
    assert len(conditions) == 1
    assert conditions[0].negate is True


def test_parse_conditions_multiple() -> None:
    """Test _parse_conditions with multiple conditions."""
    conditions = _parse_conditions(['lemma=test', 'form=testing'])
    assert len(conditions) == 2
    assert conditions[0].key == 'lemma'
    assert conditions[1].key == 'form'


def test_parse_conditions_nested() -> None:
    """Test _parse_conditions with nested conditions."""
    conditions = _parse_conditions(['feats=(Case=Nom)'])
    assert len(conditions) == 1
    assert conditions[0].key == 'feats'
    assert len(conditions[0].values) == 1
    assert conditions[0].values[0].key == 'Case'  # type: ignore [union-attr]
    assert conditions[0].values[0].values == ['Nom']  # type: ignore [union-attr]


def test_parse_conditions_nested_multiple() -> None:
    """Test _parse_conditions with nested conditions and multiple values."""
    conditions = _parse_conditions(['feats=(Case=Nom,Number=Sing)'])
    assert len(conditions) == 1
    assert conditions[0].key == 'feats'
    assert len(conditions[0].values) == 2


def test_parse_conditions_nested_match_any() -> None:
    """Test _parse_conditions with nested conditions using match_any."""
    conditions = _parse_conditions(['feats=any(Case=Nom,Number=Sing)'])
    assert len(conditions) == 1
    assert conditions[0].match_any is True


def test_parse_conditions_invalid_nested_key_raises() -> None:
    """Test _parse_conditions raises for non-nestable key."""
    with pytest.raises(ValueError, match='Cannot nest conditions'):
        _parse_conditions(['lemma=(foo=bar)'])
