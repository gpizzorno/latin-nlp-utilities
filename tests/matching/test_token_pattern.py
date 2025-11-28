"""Tests for the TokenPattern class."""

from __future__ import annotations

from typing import Any

import pytest

from conllu_tools.matching import Condition, TokenPattern


def test_token_pattern_initialization_default() -> None:
    """Test TokenPattern default initialization."""
    pattern = TokenPattern()

    assert pattern.conditions == []
    assert pattern.negate is False
    assert pattern.count == 0
    assert pattern.min_count == 0
    assert pattern.max_count == 1
    assert pattern.match_multiple is False
    assert pattern.counter == 0
    assert pattern.matches_any is True


def test_token_pattern_initialization_with_conditions() -> None:
    """Test TokenPattern initialization with conditions."""
    condition = Condition(key='upos', values=['NOUN'])
    pattern = TokenPattern(conditions=[condition])

    assert len(pattern.conditions) == 1
    assert pattern.matches_any is False


def test_token_pattern_initialization_with_negate() -> None:
    """Test TokenPattern initialization with negation."""
    condition = Condition(key='upos', values=['NOUN'])
    pattern = TokenPattern(conditions=[condition], negate=True)

    assert pattern.negate is True


def test_token_pattern_initialization_with_count() -> None:
    """Test TokenPattern initialization with exact count."""
    pattern = TokenPattern(count=2)

    assert pattern.count == 2
    assert pattern.min_count == 0
    assert pattern.max_count == 1


def test_token_pattern_initialization_with_min_max_count() -> None:
    """Test TokenPattern initialization with min/max count range."""
    pattern = TokenPattern(min_count=2, max_count=5)

    assert pattern.min_count == 2
    assert pattern.max_count == 5
    assert pattern.match_multiple is True


def test_token_pattern_initialization_raises_error_for_non_condition_list() -> None:
    """Test that non-Condition list raises ValueError."""
    with pytest.raises(ValueError, match='must be a list of Condition instances'):
        TokenPattern(conditions=['not a condition'])  # type: ignore[list-item]


def test_token_pattern_initialization_raises_error_for_mixed_list() -> None:
    """Test that mixed list (Condition and non-Condition) raises ValueError."""
    condition = Condition(key='upos', values=['NOUN'])
    with pytest.raises(ValueError, match='must be a list of Condition instances'):
        TokenPattern(conditions=[condition, 'not a condition'])  # type: ignore[list-item]


def test_token_pattern_test_with_nested_feats_condition(sample_token: dict[str, Any]) -> None:
    """Test TokenPattern with nested condition for feats."""
    feats_conds: list[str | Condition] = [
        Condition(key='Case', values=['Nom']),
        Condition(key='Number', values=['Sing']),
    ]
    feats_cond = Condition(key='feats', values=feats_conds)
    pattern = TokenPattern(conditions=[feats_cond])

    assert pattern.test(sample_token) is True


def test_token_pattern_test_with_token_missing_feats(punct_token: dict[str, Any]) -> None:
    """Test TokenPattern on token with None feats."""
    feats_conds: list[str | Condition] = [Condition(key='Case', values=['Nom'])]
    feats_cond = Condition(key='feats', values=feats_conds)
    pattern = TokenPattern(conditions=[feats_cond])

    # Token has None feats, should not match
    assert pattern.test(punct_token) is False


def test_token_pattern_test_with_empty_conditions_list() -> None:
    """Test TokenPattern with explicitly empty conditions list."""
    pattern = TokenPattern(conditions=[])

    assert pattern.matches_any is True


def test_token_pattern_counter_reset() -> None:
    """Test that counter can be manually reset."""
    pattern = TokenPattern()
    pattern.counter = 5
    pattern.counter = 0

    assert pattern.counter == 0
