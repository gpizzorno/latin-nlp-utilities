"""Tests for the MatchResult class."""

from __future__ import annotations

import conllu

from conllu_tools.matching import MatchResult


def test_match_result_initialization() -> None:
    """Test MatchResult initialization with required fields."""
    tokens = [
        conllu.Token({'id': 1, 'form': 'una', 'lemma': 'unus'}),
        conllu.Token({'id': 2, 'form': 'scala', 'lemma': 'scalae'}),
    ]
    result = MatchResult(pattern_name='test-pattern', sentence_id='sent-1', tokens=tokens)

    assert result.pattern_name == 'test-pattern'
    assert result.sentence_id == 'sent-1'
    assert len(result.tokens) == 2


def test_match_result_substring_single_token() -> None:
    """Test substring property with single token."""
    tokens = [conllu.Token({'id': 1, 'form': 'test', 'lemma': 'test'})]
    result = MatchResult(pattern_name='test', sentence_id='sent-1', tokens=tokens)

    assert result.substring == 'test'


def test_match_result_substring_multiple_tokens() -> None:
    """Test substring property with multiple tokens."""
    tokens = [
        conllu.Token({'id': 1, 'form': 'una', 'lemma': 'unus'}),
        conllu.Token({'id': 2, 'form': 'scala', 'lemma': 'scalae'}),
        conllu.Token({'id': 3, 'form': 'magna', 'lemma': 'magnus'}),
    ]
    result = MatchResult(pattern_name='test', sentence_id='sent-1', tokens=tokens)

    assert result.substring == 'una scala magna'


def test_match_result_lemmata_single_token() -> None:
    """Test lemmata property with single token."""
    tokens = [conllu.Token({'id': 1, 'form': 'scalae', 'lemma': 'scala'})]
    result = MatchResult(pattern_name='test', sentence_id='sent-1', tokens=tokens)

    assert result.lemmata == ['scala']


def test_match_result_lemmata_multiple_tokens() -> None:
    """Test lemmata property with multiple tokens."""
    tokens = [
        conllu.Token({'id': 1, 'form': 'una', 'lemma': 'unus'}),
        conllu.Token({'id': 2, 'form': 'scala', 'lemma': 'scalae'}),
    ]
    result = MatchResult(pattern_name='test', sentence_id='sent-1', tokens=tokens)

    assert result.lemmata == ['unus', 'scalae']


def test_match_result_forms_single_token() -> None:
    """Test forms property with single token."""
    tokens = [conllu.Token({'id': 1, 'form': 'test', 'lemma': 'test'})]
    result = MatchResult(pattern_name='test', sentence_id='sent-1', tokens=tokens)

    assert result.forms == ['test']


def test_match_result_forms_multiple_tokens() -> None:
    """Test forms property with multiple tokens."""
    tokens = [
        conllu.Token({'id': 1, 'form': 'una', 'lemma': 'unus'}),
        conllu.Token({'id': 2, 'form': 'scala', 'lemma': 'scalae'}),
    ]
    result = MatchResult(pattern_name='test', sentence_id='sent-1', tokens=tokens)

    assert result.forms == ['una', 'scala']


def test_match_result_repr() -> None:
    """Test __repr__ includes pattern_name, sentence_id, and substring."""
    tokens = [
        conllu.Token({'id': 1, 'form': 'una', 'lemma': 'unus'}),
        conllu.Token({'id': 2, 'form': 'scala', 'lemma': 'scalae'}),
    ]
    result = MatchResult(pattern_name='test-pattern', sentence_id='sent-1', tokens=tokens)
    repr_str = repr(result)

    assert 'MatchResult' in repr_str
    assert 'test-pattern' in repr_str
    assert 'sent-1' in repr_str
    assert 'una scala' in repr_str


def test_match_result_str_returns_substring() -> None:
    """Test __str__ returns the substring."""
    tokens = [
        conllu.Token({'id': 1, 'form': 'una', 'lemma': 'unus'}),
        conllu.Token({'id': 2, 'form': 'scala', 'lemma': 'scalae'}),
    ]
    result = MatchResult(pattern_name='test-pattern', sentence_id='sent-1', tokens=tokens)

    assert str(result) == 'una scala'


def test_match_result_empty_tokens_list() -> None:
    """Test MatchResult with empty tokens list."""
    result = MatchResult(pattern_name='test', sentence_id='sent-1', tokens=[])

    assert result.substring == ''
    assert result.lemmata == []
    assert result.forms == []


def test_match_result_with_special_characters_in_form() -> None:
    """Test MatchResult with special characters in token forms."""
    tokens = [
        conllu.Token({'id': 1, 'form': 'ab', 'lemma': 'ab'}),
        conllu.Token({'id': 2, 'form': ':', 'lemma': ':'}),
    ]
    result = MatchResult(pattern_name='test', sentence_id='sent-1', tokens=tokens)

    assert result.substring == 'ab :'
    assert result.forms == ['ab', ':']


def test_match_result_with_punctuation() -> None:
    """Test MatchResult with punctuation tokens."""
    tokens = [
        conllu.Token({'id': 1, 'form': 'scala', 'lemma': 'scalae'}),
        conllu.Token({'id': 2, 'form': '.', 'lemma': '.'}),
    ]
    result = MatchResult(pattern_name='test', sentence_id='sent-1', tokens=tokens)

    assert result.substring == 'scala .'
    assert result.forms == ['scala', '.']
