"""Tests for AlignmentWord and Alignment classes."""

from __future__ import annotations

from nlp_utilities.conllu.evaluators.base import Alignment, AlignmentWord
from tests.helpers.generation import create_test_udword


def test_alignment_word_creation(alignment_word_pair: AlignmentWord) -> None:
    """Test AlignmentWord creation."""
    assert alignment_word_pair.gold_word is not None
    assert alignment_word_pair.system_word is not None
    assert alignment_word_pair.gold_word.token['form'] == 'word'
    assert alignment_word_pair.system_word.token['form'] == 'word'


def test_alignment_word_with_matching_words() -> None:
    """Test AlignmentWord with matching gold/system words."""
    gold = create_test_udword('test', 'VERB', 0, 'root', start=0, end=4)
    system = create_test_udword('test', 'VERB', 0, 'root', start=0, end=4)

    aligned = AlignmentWord(gold_word=gold, system_word=system)

    assert aligned.gold_word.token['form'] == 'test'
    assert aligned.system_word.token['form'] == 'test'


def test_alignment_initialization(empty_alignment: Alignment) -> None:
    """Test Alignment initialization."""
    assert empty_alignment.gold_words == []
    assert empty_alignment.system_words == []
    assert empty_alignment.matched_words == []
    assert empty_alignment.matched_words_map == {}


def test_alignment_append_aligned_words() -> None:
    """Test append_aligned_words method."""
    gold = create_test_udword('word', 'NOUN', 0, 'root', start=0, end=4)
    system = create_test_udword('word', 'NOUN', 0, 'root', start=0, end=4)

    alignment = Alignment(gold_words=[gold], system_words=[system])
    alignment.append_aligned_words(gold, system)

    assert len(alignment.matched_words) == 1
    assert alignment.matched_words[0].gold_word == gold
    assert alignment.matched_words[0].system_word == system


def test_alignment_matched_words_map_populated() -> None:
    """Test matched_words_map is correctly populated."""
    gold = create_test_udword('word', 'NOUN', 0, 'root', start=0, end=4)
    system = create_test_udword('word', 'NOUN', 0, 'root', start=0, end=4)

    alignment = Alignment(gold_words=[gold], system_words=[system])
    alignment.append_aligned_words(gold, system)

    assert system in alignment.matched_words_map
    assert alignment.matched_words_map[system] == gold


def test_alignment_with_empty_word_lists() -> None:
    """Test alignment with empty word lists."""
    alignment = Alignment(gold_words=[], system_words=[])
    assert len(alignment.gold_words) == 0
    assert len(alignment.system_words) == 0
    assert len(alignment.matched_words) == 0


def test_alignment_with_mismatched_word_counts() -> None:
    """Test alignment with mismatched word counts."""
    gold_words = [
        create_test_udword('word1', 'NOUN', 0, 'root', start=0, end=5),
        create_test_udword('word2', 'VERB', 0, 'root', start=6, end=11),
    ]
    system_words = [
        create_test_udword('word1', 'NOUN', 0, 'root', start=0, end=5),
    ]

    alignment = Alignment(gold_words=gold_words, system_words=system_words)
    assert len(alignment.gold_words) == 2
    assert len(alignment.system_words) == 1
