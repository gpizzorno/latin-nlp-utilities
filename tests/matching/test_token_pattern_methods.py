"""Tests for the TokenPattern class methods."""

from __future__ import annotations

from typing import Any

from conllu_tools.matching import Condition, TokenPattern


def test_token_pattern_test_matches_token(sample_token: dict[str, Any]) -> None:
    """Test that TokenPattern matches a valid token."""
    condition = Condition(key='upos', values=['NUM'])
    pattern = TokenPattern(conditions=[condition])

    assert pattern.test(sample_token) is True
    assert pattern.counter == 1


def test_token_pattern_test_does_not_match_token(sample_token: dict[str, Any]) -> None:
    """Test that TokenPattern doesn't match non-matching token."""
    condition = Condition(key='upos', values=['VERB'])
    pattern = TokenPattern(conditions=[condition])

    assert pattern.test(sample_token) is False
    assert pattern.counter == 0


def test_token_pattern_test_multiple_conditions_all_match(sample_token: dict[str, Any]) -> None:
    """Test TokenPattern with multiple conditions that all match."""
    upos_cond = Condition(key='upos', values=['NUM'])
    form_cond = Condition(key='form', values=['unum'])
    pattern = TokenPattern(conditions=[upos_cond, form_cond])

    assert pattern.test(sample_token) is True


def test_token_pattern_test_multiple_conditions_one_fails(sample_token: dict[str, Any]) -> None:
    """Test TokenPattern with multiple conditions where one fails."""
    upos_cond = Condition(key='upos', values=['NUM'])
    form_cond = Condition(key='form', values=['wrong'])
    pattern = TokenPattern(conditions=[upos_cond, form_cond])

    assert pattern.test(sample_token) is False


def test_token_pattern_test_negated_match(sample_token: dict[str, Any]) -> None:
    """Test negated TokenPattern returns False when conditions match."""
    condition = Condition(key='upos', values=['NUM'])
    pattern = TokenPattern(conditions=[condition], negate=True)

    assert pattern.test(sample_token) is False


def test_token_pattern_test_negated_no_match(sample_token: dict[str, Any]) -> None:
    """Test negated TokenPattern returns True when conditions don't match."""
    condition = Condition(key='upos', values=['VERB'])
    pattern = TokenPattern(conditions=[condition], negate=True)

    assert pattern.test(sample_token) is True


def test_token_pattern_test_any_token(sample_token: dict[str, Any]) -> None:
    """Test TokenPattern with no conditions matches any token."""
    pattern = TokenPattern()

    assert pattern.matches_any is True
    assert pattern.test(sample_token) is True


def test_token_pattern_test_counter_increments(sample_token: dict[str, Any]) -> None:
    """Test that counter increments on successful match."""
    condition = Condition(key='upos', values=['NUM'])
    pattern = TokenPattern(conditions=[condition])

    pattern.test(sample_token)
    assert pattern.counter == 1

    pattern.test(sample_token)
    assert pattern.counter == 2


def test_token_pattern_test_counter_does_not_increment_on_failure(
    sample_token: dict[str, Any],
    noun_token: dict[str, Any],
) -> None:
    """Test that counter doesn't increment on failed match."""
    condition = Condition(key='upos', values=['NUM'])
    pattern = TokenPattern(conditions=[condition])

    pattern.test(sample_token)  # Matches
    pattern.test(noun_token)  # Doesn't match

    assert pattern.counter == 1
