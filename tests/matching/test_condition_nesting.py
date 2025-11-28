"""Tests for the Condition class nested conditions."""

from __future__ import annotations

from typing import Any

from conllu_tools.matching import Condition


def test_condition_test_nested_all_match(sample_token: dict[str, Any]) -> None:
    """Test nested conditions where all must match."""
    inner_conditions: list[str | Condition] = [
        Condition(key='Case', values=['Nom']),
        Condition(key='Number', values=['Sing']),
    ]
    condition = Condition(key='feats', values=inner_conditions, match_any=False)
    assert condition.test(sample_token) is True


def test_condition_test_nested_all_match_one_fails(sample_token: dict[str, Any]) -> None:
    """Test nested conditions where one fails."""
    inner_conditions: list[str | Condition] = [
        Condition(key='Case', values=['Abl']),  # Does not match
        Condition(key='Number', values=['Sing']),
    ]
    condition = Condition(key='feats', values=inner_conditions, match_any=False)
    assert condition.test(sample_token) is False


def test_condition_test_nested_any_match_one_matches(sample_token: dict[str, Any]) -> None:
    """Test nested conditions where any can match - one matches."""
    inner_conditions: list[str | Condition] = [
        Condition(key='Case', values=['Abl']),  # Does not match
        Condition(key='Number', values=['Sing']),  # Matches
    ]
    condition = Condition(key='feats', values=inner_conditions, match_any=True)
    assert condition.test(sample_token) is True


def test_condition_test_nested_any_match_none_match(sample_token: dict[str, Any]) -> None:
    """Test nested conditions where any can match - none match."""
    inner_conditions: list[str | Condition] = [
        Condition(key='Case', values=['Abl']),  # Does not match
        Condition(key='Number', values=['Plur']),  # Does not match
    ]
    condition = Condition(key='feats', values=inner_conditions, match_any=True)
    assert condition.test(sample_token) is False
