"""Tests for alignment helper functions."""

from __future__ import annotations

from conllu_tools.evaluation.helpers import (
    _beyond_end,
    _compute_lcs,
    _extend_end,
    _find_multiword_span,
    align_words,
)
from tests.helpers.generation import create_test_udword


def test_align_words_with_identical_sequences() -> None:
    """Test align_words with identical sequences."""
    gold_words = [
        create_test_udword('word1', 'NOUN', 0, 'root', start=0, end=5),
        create_test_udword('word2', 'VERB', 1, 'obj', start=6, end=11),
    ]
    system_words = [
        create_test_udword('word1', 'NOUN', 0, 'root', start=0, end=5),
        create_test_udword('word2', 'VERB', 1, 'obj', start=6, end=11),
    ]

    alignment = align_words(gold_words, system_words)

    assert len(alignment.matched_words) == 2
    assert alignment.matched_words[0].gold_word == gold_words[0]
    assert alignment.matched_words[0].system_word == system_words[0]
    assert alignment.matched_words[1].gold_word == gold_words[1]
    assert alignment.matched_words[1].system_word == system_words[1]


def test_align_words_with_mismatched_word_counts() -> None:
    """Test align_words with mismatched word counts."""
    gold_words = [
        create_test_udword('word1', 'NOUN', 0, 'root', start=0, end=5),
        create_test_udword('word2', 'VERB', 1, 'obj', start=6, end=11),
        create_test_udword('word3', 'ADJ', 2, 'amod', start=12, end=17),
    ]
    system_words = [
        create_test_udword('word1', 'NOUN', 0, 'root', start=0, end=5),
        create_test_udword('word2', 'VERB', 1, 'obj', start=6, end=11),
    ]

    alignment = align_words(gold_words, system_words)

    # Should align first two words
    assert len(alignment.matched_words) == 2
    assert len(alignment.gold_words) == 3
    assert len(alignment.system_words) == 2


def test_align_words_with_multi_word_tokens() -> None:
    """Test align_words with multi-word tokens."""
    # Gold has MWT for "cannot" -> "can" + "not"
    gold_words = [
        create_test_udword('can', 'AUX', 0, 'root', start=0, end=6, is_multiword=True),
        create_test_udword('not', 'PART', 1, 'advmod', start=0, end=6, is_multiword=True),
    ]
    # System has the same
    system_words = [
        create_test_udword('can', 'AUX', 0, 'root', start=0, end=6, is_multiword=True),
        create_test_udword('not', 'PART', 1, 'advmod', start=0, end=6, is_multiword=True),
    ]

    alignment = align_words(gold_words, system_words)

    # Should align both words using LCS
    assert len(alignment.matched_words) == 2


def test_align_words_with_different_word_order() -> None:
    """Test align_words with different word order (different spans)."""
    gold_words = [
        create_test_udword('word1', 'NOUN', 0, 'root', start=0, end=5),
        create_test_udword('word2', 'VERB', 1, 'obj', start=6, end=11),
    ]
    # System has different spans (words at different positions)
    system_words = [
        create_test_udword('extra', 'DET', 0, 'det', start=0, end=5),
        create_test_udword('word1', 'NOUN', 1, 'root', start=6, end=11),
        create_test_udword('word2', 'VERB', 2, 'obj', start=12, end=17),
    ]

    alignment = align_words(gold_words, system_words)

    # Should align based on matching spans (span matching, not form matching)
    # word1 (0-5) aligns with extra (0-5)
    # word2 (6-11) aligns with word1 (6-11)
    assert len(alignment.matched_words) == 2
    assert alignment.matched_words[0].gold_word.token['form'] == 'word1'
    assert alignment.matched_words[0].system_word.token['form'] == 'extra'
    assert alignment.matched_words[1].gold_word.token['form'] == 'word2'
    assert alignment.matched_words[1].system_word.token['form'] == 'word1'


def test_align_words_with_case_insensitive_matching() -> None:
    """Test align_words with case-insensitive matching in MWT."""
    # Test that case differences don't prevent alignment in MWT context
    gold_words = [
        create_test_udword('Word', 'NOUN', 0, 'root', start=0, end=4, is_multiword=True),
    ]
    system_words = [
        create_test_udword('word', 'NOUN', 0, 'root', start=0, end=4, is_multiword=True),
    ]

    alignment = align_words(gold_words, system_words)

    # Should align with case-insensitive matching
    assert len(alignment.matched_words) == 1


def test_align_words_with_empty_word_lists() -> None:
    """Test align_words with empty word lists."""
    alignment = align_words([], [])

    assert len(alignment.matched_words) == 0
    assert len(alignment.gold_words) == 0
    assert len(alignment.system_words) == 0


def test_align_words_with_single_word() -> None:
    """Test align_words with single word."""
    gold_words = [create_test_udword('word', 'NOUN', 0, 'root', start=0, end=4)]
    system_words = [create_test_udword('word', 'NOUN', 0, 'root', start=0, end=4)]

    alignment = align_words(gold_words, system_words)

    assert len(alignment.matched_words) == 1
    assert alignment.matched_words[0].gold_word == gold_words[0]


def test_lcs_computation_for_multi_word_token_alignment() -> None:
    """Test LCS computation for multi-word token alignment."""
    # Gold: "can" "not" "go" (first two are MWT)
    gold_words = [
        create_test_udword('can', 'AUX', 3, 'aux', start=0, end=6, is_multiword=True),
        create_test_udword('not', 'PART', 3, 'advmod', start=0, end=6, is_multiword=True),
        create_test_udword('go', 'VERB', 0, 'root', start=7, end=9),
    ]
    # System: same structure
    system_words = [
        create_test_udword('can', 'AUX', 3, 'aux', start=0, end=6, is_multiword=True),
        create_test_udword('not', 'PART', 3, 'advmod', start=0, end=6, is_multiword=True),
        create_test_udword('go', 'VERB', 0, 'root', start=7, end=9),
    ]

    alignment = align_words(gold_words, system_words)

    # Should align all three words
    assert len(alignment.matched_words) == 3


def test_alignment_span_matching_logic() -> None:
    """Test alignment span matching logic."""
    # Exact span matches
    gold_words = [
        create_test_udword('the', 'DET', 2, 'det', start=0, end=3),
        create_test_udword('cat', 'NOUN', 0, 'root', start=4, end=7),
    ]
    system_words = [
        create_test_udword('the', 'DET', 2, 'det', start=0, end=3),
        create_test_udword('cat', 'NOUN', 0, 'root', start=4, end=7),
    ]

    alignment = align_words(gold_words, system_words)

    assert len(alignment.matched_words) == 2


def test_find_multiword_span_function() -> None:
    """Test _find_multiword_span function."""
    gold_words = [
        create_test_udword('can', 'AUX', 3, 'aux', start=0, end=6, is_multiword=True),
        create_test_udword('not', 'PART', 3, 'advmod', start=0, end=6, is_multiword=True),
    ]
    system_words = [
        create_test_udword('can', 'AUX', 3, 'aux', start=0, end=6, is_multiword=True),
        create_test_udword('not', 'PART', 3, 'advmod', start=0, end=6, is_multiword=True),
    ]

    gs, ss, gi, si = _find_multiword_span(gold_words, system_words, 0, 0)

    # Should find the span covering both MWT words
    assert gs == 0  # Gold start
    assert ss == 0  # System start
    assert gi == 2  # Gold end (after both words)
    assert si == 2  # System end (after both words)


def test_beyond_end_function() -> None:
    """Test _beyond_end function."""
    words = [
        create_test_udword('word1', 'NOUN', 0, 'root', start=0, end=5),
        create_test_udword('word2', 'VERB', 0, 'root', start=6, end=11),
    ]

    # Index beyond list
    assert _beyond_end(words, 2, 10) is True

    # Index within list but span beyond end
    assert _beyond_end(words, 1, 5) is True

    # Index within list and span within end
    assert _beyond_end(words, 0, 10) is False


def test_extend_end_function() -> None:
    """Test _extend_end function."""
    # Non-multiword doesn't extend
    word = create_test_udword('word', 'NOUN', 0, 'root', start=0, end=5, is_multiword=False)
    assert _extend_end(word, 10) == 10

    # Multiword extends if it goes beyond current end
    mwt_word = create_test_udword('word', 'NOUN', 0, 'root', start=0, end=15, is_multiword=True)
    assert _extend_end(mwt_word, 10) == 15

    # Multiword doesn't extend if it's within current end
    assert _extend_end(mwt_word, 20) == 20


def test_compute_lcs_function() -> None:
    """Test _compute_lcs function."""
    gold_words = [
        create_test_udword('a', 'DET', 0, 'det', start=0, end=1),
        create_test_udword('b', 'NOUN', 0, 'root', start=2, end=3),
    ]
    system_words = [
        create_test_udword('a', 'DET', 0, 'det', start=0, end=1),
        create_test_udword('b', 'NOUN', 0, 'root', start=2, end=3),
    ]

    lcs = _compute_lcs(gold_words, system_words, gi=2, si=2, gs=0, ss=0)

    # LCS matrix should show length of longest common subsequence
    assert len(lcs) == 2  # Gold length
    assert len(lcs[0]) == 2  # System length
    # First cell should show max LCS length (2 in this case)
    assert lcs[0][0] == 2
