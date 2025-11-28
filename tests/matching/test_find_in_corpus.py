"""Tests for the find_in_corpus function."""

from __future__ import annotations

import conllu

from conllu_tools.matching import build_pattern, find_in_corpus


def test_find_in_corpus_single_pattern_match(sample_corpus: list[conllu.TokenList]) -> None:
    """Test find_in_corpus finds matches for a single pattern."""
    pattern = build_pattern('NOUN', name='noun-pattern')
    results = find_in_corpus(sample_corpus, [pattern])

    assert len(results) == 2
    forms = [r.substring for r in results]
    assert 'cat' in forms
    assert 'dog' in forms


def test_find_in_corpus_multi_token_pattern(sample_corpus: list[conllu.TokenList]) -> None:
    """Test find_in_corpus with multi-token pattern."""
    pattern = build_pattern('NOUN+VERB', name='noun-verb')
    results = find_in_corpus(sample_corpus, [pattern])

    assert len(results) == 2
    substrings = [r.substring for r in results]
    assert 'cat runs' in substrings
    assert 'dog sleeps' in substrings


def test_find_in_corpus_no_matches(sample_corpus: list[conllu.TokenList]) -> None:
    """Test find_in_corpus returns empty list when no matches."""
    pattern = build_pattern('ADJ+NOUN', name='adj-noun')
    results = find_in_corpus(sample_corpus, [pattern])

    assert len(results) == 0


def test_find_in_corpus_multiple_patterns(sample_corpus: list[conllu.TokenList]) -> None:
    """Test find_in_corpus with multiple patterns."""
    pattern1 = build_pattern('NOUN', name='nouns')
    pattern2 = build_pattern('VERB', name='verbs')
    results = find_in_corpus(sample_corpus, [pattern1, pattern2])

    assert len(results) == 4
    noun_results = [r for r in results if r.pattern_name == 'nouns']
    verb_results = [r for r in results if r.pattern_name == 'verbs']
    assert len(noun_results) == 2
    assert len(verb_results) == 2


def test_find_in_corpus_result_has_sentence_id(
    sample_corpus: list[conllu.TokenList],
) -> None:
    """Test find_in_corpus results include sentence_id."""
    pattern = build_pattern('NOUN', name='noun-pattern')
    results = find_in_corpus(sample_corpus, [pattern])

    sentence_ids = {r.sentence_id for r in results}
    assert 'sent-1' in sentence_ids
    assert 'sent-2' in sentence_ids


def test_find_in_corpus_empty_corpus() -> None:
    """Test find_in_corpus with empty corpus."""
    pattern = build_pattern('NOUN', name='noun-pattern')
    results = find_in_corpus([], [pattern])

    assert len(results) == 0


def test_find_in_corpus_empty_patterns(sample_corpus: list[conllu.TokenList]) -> None:
    """Test find_in_corpus with empty patterns list."""
    results = find_in_corpus(sample_corpus, [])

    assert len(results) == 0


def test_find_in_corpus_with_condition(sample_corpus: list[conllu.TokenList]) -> None:
    """Test find_in_corpus with pattern conditions."""
    pattern = build_pattern('NOUN:lemma=cat', name='cat-only')
    results = find_in_corpus(sample_corpus, [pattern])

    assert len(results) == 1
    assert results[0].substring == 'cat'


def test_find_in_corpus_det_noun_sequence(sample_corpus: list[conllu.TokenList]) -> None:
    """Test find_in_corpus with DET+NOUN sequence."""
    pattern = build_pattern('DET+NOUN', name='det-noun')
    results = find_in_corpus(sample_corpus, [pattern])

    assert len(results) == 2
    substrings = [r.substring for r in results]
    assert 'The cat' in substrings
    assert 'A dog' in substrings
