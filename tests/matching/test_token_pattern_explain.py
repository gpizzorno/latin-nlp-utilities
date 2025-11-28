"""Tests for the TokenPattern class explain method."""

from __future__ import annotations

from conllu_tools.matching import Condition, TokenPattern


def test_token_pattern_explain_matches_any() -> None:
    """Test explain for pattern that matches any token."""
    pattern = TokenPattern()
    explanation = pattern.explain()

    assert 'any token' in explanation.lower()


def test_token_pattern_explain_with_conditions() -> None:
    """Test explain includes condition explanations."""
    condition = Condition(key='upos', values=['NOUN'])
    pattern = TokenPattern(conditions=[condition])
    explanation = pattern.explain()

    assert 'upos' in explanation or 'NOUN' in explanation


def test_token_pattern_explain_with_exact_count() -> None:
    """Test explain includes exact count when specified."""
    pattern = TokenPattern(count=2)
    explanation = pattern.explain()

    assert 'exactly' in explanation.lower()
    assert '2' in explanation


def test_token_pattern_explain_with_min_max_count() -> None:
    """Test explain includes min/max count range."""
    pattern = TokenPattern(min_count=2, max_count=5)
    explanation = pattern.explain()

    assert 'between' in explanation.lower()
    assert '2' in explanation
    assert '5' in explanation


def test_token_pattern_explain_with_negation() -> None:
    """Test explain includes negation."""
    condition = Condition(key='upos', values=['NOUN'])
    pattern = TokenPattern(conditions=[condition], negate=True)
    explanation = pattern.explain()

    assert 'not' in explanation.lower() or 'does not' in explanation.lower()


def test_token_pattern_explain_with_multiple_conditions() -> None:
    """Test explain with multiple conditions."""
    cond1 = Condition(key='upos', values=['NOUN'])
    cond2 = Condition(key='form', values=['test'])
    pattern = TokenPattern(conditions=[cond1, cond2])
    explanation = pattern.explain()

    assert 'and' in explanation.lower()


def test_token_pattern_explain_with_two_conditions() -> None:
    """Test explain with exactly two conditions."""
    cond1 = Condition(key='upos', values=['NOUN'])
    cond2 = Condition(key='form', values=['test'])
    pattern = TokenPattern(conditions=[cond1, cond2])
    explanation = pattern.explain()

    assert 'and' in explanation


def test_token_pattern_explain_with_three_conditions() -> None:
    """Test explain with three conditions includes comma formatting."""
    cond1 = Condition(key='upos', values=['NOUN'])
    cond2 = Condition(key='form', values=['test'])
    cond3 = Condition(key='lemma', values=['test'])
    pattern = TokenPattern(conditions=[cond1, cond2, cond3])
    explanation = pattern.explain()

    assert 'and' in explanation
