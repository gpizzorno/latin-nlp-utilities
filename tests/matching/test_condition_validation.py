"""Tests for the Condition class validation."""

from __future__ import annotations

from typing import Any

from conllu_tools.matching import Condition


def test_condition_test_missing_key_returns_false(sample_token: dict[str, Any]) -> None:
    """Test that missing key returns False."""
    condition = Condition(key='nonexistent', values=['value'])
    assert condition.test(sample_token) is False


def test_condition_test_missing_key_with_negation_returns_true(sample_token: dict[str, Any]) -> None:
    """Test that missing key with negation returns True."""
    condition = Condition(key='nonexistent', values=['value'], negate=True)
    assert condition.test(sample_token) is True


def test_condition_test_none_feats(punct_token: dict[str, Any]) -> None:
    """Test condition on token with None feats."""
    condition = Condition(key='feats', values=[Condition(key='Case', values=['Nom'])])
    assert condition.test(punct_token) is False


def test_condition_is_valid_returns_true_for_properly_configured() -> None:
    """Test is_valid returns True for properly configured condition."""
    condition = Condition(key='upos', values=['NOUN'])
    assert condition.is_valid is True


def test_condition_is_container_returns_true_for_nested() -> None:
    """Test is_container returns True for nested conditions."""
    inner: list[str | Condition] = [Condition(key='Case', values=['Nom'])]
    condition = Condition(values=inner)
    assert condition.is_container is True


def test_condition_is_container_returns_false_for_simple() -> None:
    """Test is_container returns False for simple conditions."""
    condition = Condition(key='upos', values=['NOUN'])
    assert condition.is_container is False
