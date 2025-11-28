"""Tests for the Condition class negation."""

from __future__ import annotations

from typing import Any

from conllu_tools.matching import Condition


def test_condition_test_negated_equals_match(sample_token: dict[str, Any]) -> None:
    """Test negated equals - should return False when value matches."""
    condition = Condition(key='upos', values=['NUM'], negate=True)
    assert condition.test(sample_token) is False


def test_condition_test_negated_equals_no_match(sample_token: dict[str, Any]) -> None:
    """Test negated equals - should return True when value doesn't match."""
    condition = Condition(key='upos', values=['NOUN'], negate=True)
    assert condition.test(sample_token) is True


def test_condition_test_negated_contains(sample_token: dict[str, Any]) -> None:
    """Test negated contains match type."""
    condition = Condition(key='form', values=['un'], match_type='contains', negate=True)
    assert condition.test(sample_token) is False
