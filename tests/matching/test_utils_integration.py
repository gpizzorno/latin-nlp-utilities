"""Tests for the matching utility functions."""

from __future__ import annotations

import conllu

from conllu_tools.matching import build_pattern, find_in_corpus


def test_build_pattern_and_find_complex_sequence(complex_sentence: conllu.TokenList) -> None:
    """Test building and finding a complex pattern sequence."""
    # Match DET + 1-3 * + NOUN
    pattern = build_pattern('DET+*{1,3}+NOUN', name='det-any-noun')
    results = find_in_corpus([complex_sentence], [pattern])
    assert len(results) == 1
    assert results[0].substring == 'aliam virgam auream sine lapide'


def test_build_pattern_with_feature_condition(complex_sentence: conllu.TokenList) -> None:
    """Test building pattern with feature conditions."""
    pattern = build_pattern('NOUN:feats=(Case=Acc)', name='acc-noun')
    results = find_in_corpus([complex_sentence], [pattern])
    assert len(results) == 1
    assert results[0].substring == 'virgam'
