"""Tests for the build_pattern function."""

from __future__ import annotations

import pytest

from conllu_tools.matching import SentencePattern, build_pattern


def test_build_pattern_simple_upos() -> None:
    """Test build_pattern with simple UPOS pattern."""
    pattern = build_pattern('NOUN')
    assert isinstance(pattern, SentencePattern)
    assert len(pattern.pattern) == 1


def test_build_pattern_with_name() -> None:
    """Test build_pattern with name parameter."""
    pattern = build_pattern('NOUN', name='test-pattern')
    assert pattern.name == 'test-pattern'


def test_build_pattern_multiple_tokens() -> None:
    """Test build_pattern with multiple token patterns joined by +."""
    pattern = build_pattern('NOUN+VERB')
    assert len(pattern.pattern) == 2


def test_build_pattern_wildcard() -> None:
    """Test build_pattern with wildcard token."""
    pattern = build_pattern('NOUN+*+VERB')
    assert len(pattern.pattern) == 3


def test_build_pattern_empty_raises() -> None:
    """Test build_pattern raises for empty string."""
    with pytest.raises(ValueError, match='non-empty string'):
        build_pattern('')


def test_build_pattern_none_raises() -> None:
    """Test build_pattern raises for None."""
    with pytest.raises(ValueError, match='non-empty string'):
        build_pattern(None)  # type: ignore[arg-type]


def test_build_pattern_with_lemma_condition() -> None:
    """Test build_pattern with lemma condition."""
    pattern = build_pattern('NOUN:lemma=test')
    assert len(pattern.pattern) == 1
    tp = pattern.pattern[0]
    # Should have upos condition and lemma condition
    assert len(tp.conditions) == 2


def test_build_pattern_with_contains() -> None:
    """Test build_pattern with contains match."""
    pattern = build_pattern('NOUN:lemma=<part>')
    tp = pattern.pattern[0]
    # Find the lemma condition
    lemma_cond = next(c for c in tp.conditions if c.key == 'lemma')
    assert lemma_cond.match_type == 'contains'


def test_build_pattern_with_negation() -> None:
    """Test build_pattern with negated UPOS."""
    pattern = build_pattern('!NOUN')
    tp = pattern.pattern[0]
    assert tp.negate is True


def test_build_pattern_with_nested_condition() -> None:
    """Test build_pattern with nested feature conditions."""
    pattern = build_pattern('NOUN:feats=(Case=Nom)')
    tp = pattern.pattern[0]
    feats_cond = next(c for c in tp.conditions if c.key == 'feats')
    assert len(feats_cond.values) == 1


def test_build_pattern_multiple_conditions() -> None:
    """Test build_pattern with multiple conditions on same token."""
    pattern = build_pattern('NOUN:lemma=test:form=testing')
    tp = pattern.pattern[0]
    # upos + lemma + form = 3 conditions
    assert len(tp.conditions) == 3


def test_build_pattern_with_count() -> None:
    """Test build_pattern with count specifier."""
    pattern = build_pattern('NOUN{2}')
    tp = pattern.pattern[0]
    assert tp.count == 2


def test_build_pattern_with_zero_count() -> None:
    """Test build_pattern with zero count (optional)."""
    pattern = build_pattern('*{0}')
    tp = pattern.pattern[0]
    assert tp.count == 0


def test_build_pattern_with_range() -> None:
    """Test build_pattern with min,max range."""
    pattern = build_pattern('NOUN{1,3}')
    tp = pattern.pattern[0]
    assert tp.min_count == 1
    assert tp.max_count == 3


def test_build_pattern_combined_counter_and_conditions() -> None:
    """Test build_pattern with counter and conditions."""
    pattern = build_pattern('NOUN{2}:lemma=test')
    tp = pattern.pattern[0]
    assert tp.count == 2
    # Should have upos and lemma conditions
    assert len(tp.conditions) == 2


def test_build_pattern_complex() -> None:
    """Test build_pattern with complex multi-token pattern."""
    pattern = build_pattern('DET+ADJ{0,2}+NOUN')
    assert len(pattern.pattern) == 3


def test_build_pattern_alternation() -> None:
    """Test build_pattern with UPOS alternation."""
    pattern = build_pattern('NOUN|PROPN')
    tp = pattern.pattern[0]
    upos_cond = next(c for c in tp.conditions if c.key == 'upos')
    assert upos_cond.values == ['NOUN', 'PROPN']


def test_build_pattern_wildcard_with_conditions() -> None:
    """Test build_pattern with wildcard and conditions."""
    pattern = build_pattern('*:lemma=test')
    assert len(pattern.pattern) == 1
    tp = pattern.pattern[0]
    # Should have only lemma condition, no upos
    assert len(tp.conditions) == 1
    assert tp.conditions[0].key == 'lemma'
