"""Tests for the Condition class explain method."""

from __future__ import annotations

from conllu_tools.matching import Condition


def test_condition_explain_simple_equals() -> None:
    """Test explain method for simple equals condition."""
    condition = Condition(key='upos', values=['NOUN'])
    explanation = condition.explain()

    assert "'upos'" in explanation
    assert 'NOUN' in explanation


def test_condition_explain_multiple_values() -> None:
    """Test explain method for condition with multiple values."""
    condition = Condition(key='upos', values=['NOUN', 'VERB', 'ADJ'])
    explanation = condition.explain()

    assert 'any of' in explanation
    assert 'NOUN' in explanation
    assert 'VERB' in explanation


def test_condition_explain_negated() -> None:
    """Test explain method for negated condition."""
    condition = Condition(key='upos', values=['NOUN'], negate=True)
    explanation = condition.explain()

    assert 'does not' in explanation


def test_condition_explain_nested() -> None:
    """Test explain method for nested conditions."""
    inner: list[str | Condition] = [
        Condition(key='Case', values=['Nom']),
        Condition(key='Number', values=['Sing']),
    ]
    condition = Condition(key='feats', values=inner, match_any=True)
    explanation = condition.explain()

    assert 'at least one' in explanation or 'true' in explanation
