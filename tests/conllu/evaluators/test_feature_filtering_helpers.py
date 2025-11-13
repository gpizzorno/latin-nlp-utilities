"""Tests for helper functions (alignment, enhanced deps, feature filtering)."""

from __future__ import annotations

from nlp_utilities.conllu.evaluators.helpers import align_words, filter_universal_features
from tests.helpers.generation import create_test_udword


def test_filter_universal_features_with_only_universal() -> None:
    """Test filter_universal_features with only universal features."""
    feats = {
        'Case': 'Nom',
        'Gender': 'Masc',
        'Number': 'Sing',
    }

    result = filter_universal_features(feats)

    assert result == feats
    assert 'Case' in result
    assert 'Gender' in result
    assert 'Number' in result


def test_filter_universal_features_with_language_specific() -> None:
    """Test filter_universal_features with language-specific features."""
    feats = {
        'Case': 'Nom',
        'NameType': 'Geo',  # Language-specific
        'Number': 'Sing',
    }

    result = filter_universal_features(feats)

    # Should only keep universal features
    assert len(result) == 2
    assert 'Case' in result
    assert 'Number' in result
    assert 'NameType' not in result


def test_filter_universal_features_with_mixed_features() -> None:
    """Test filter_universal_features with mixed features."""
    feats = {
        'Case': 'Nom',
        'Gender': 'Masc',
        'Number': 'Sing',
        'Abbr': 'Yes',
        'CustomFeature': 'Value',  # Language-specific
        'InflClass': 'IndEurO',  # Language-specific
    }

    result = filter_universal_features(feats)

    # Should keep only universal features
    assert len(result) == 4
    assert 'Case' in result
    assert 'Gender' in result
    assert 'Number' in result
    assert 'Abbr' in result
    assert 'CustomFeature' not in result
    assert 'InflClass' not in result


def test_filter_universal_features_with_none_input() -> None:
    """Test filter_universal_features with None/empty input."""
    result_none = filter_universal_features(None)
    result_empty = filter_universal_features({})

    assert result_none == {}
    assert result_empty == {}


def test_filter_universal_features_preserves_values() -> None:
    """Test filter_universal_features preserves universal feature values."""
    feats = {
        'VerbForm': 'Fin',
        'Mood': 'Ind',
        'Tense': 'Pres',
        'Person': '3',
        'Number': 'Sing',
    }

    result = filter_universal_features(feats)

    # Should preserve all values exactly
    assert result['VerbForm'] == 'Fin'
    assert result['Mood'] == 'Ind'
    assert result['Tense'] == 'Pres'
    assert result['Person'] == '3'
    assert result['Number'] == 'Sing'


def test_filter_universal_features_all_universal() -> None:
    """Test filter_universal_features with all universal feature types."""
    # Test a comprehensive set of universal features
    feats = {
        'PronType': 'Prs',
        'NumType': 'Card',
        'Poss': 'Yes',
        'Reflex': 'Yes',
        'Foreign': 'Yes',
        'Abbr': 'Yes',
        'Gender': 'Masc',
        'Number': 'Sing',
        'Case': 'Nom',
        'Definite': 'Def',
        'Degree': 'Pos',
        'VerbForm': 'Fin',
        'Mood': 'Ind',
        'Tense': 'Pres',
        'Aspect': 'Perf',
        'Voice': 'Act',
        'Person': '3',
        'Polarity': 'Neg',
    }

    result = filter_universal_features(feats)

    # All should be preserved
    assert len(result) == len(feats)
    assert result == feats


def test_align_words_skips_non_matching_spans() -> None:
    """Test that align_words correctly skips words with non-matching spans."""
    gold_words = [
        create_test_udword('word1', 'NOUN', 0, 'root', start=0, end=5),
        create_test_udword('word2', 'VERB', 1, 'obj', start=6, end=11),
    ]
    # System has word at different position
    system_words = [
        create_test_udword('word1', 'NOUN', 0, 'root', start=10, end=15),
    ]

    alignment = align_words(gold_words, system_words)

    # Should not align any words due to span mismatch
    assert len(alignment.matched_words) == 0


def test_align_words_with_partial_overlap() -> None:
    """Test align_words with partial word overlap."""
    gold_words = [
        create_test_udword('word1', 'NOUN', 0, 'root', start=0, end=5),
        create_test_udword('word2', 'VERB', 1, 'obj', start=6, end=11),
        create_test_udword('word3', 'ADJ', 2, 'amod', start=12, end=17),
    ]
    system_words = [
        create_test_udword('word1', 'NOUN', 0, 'root', start=0, end=5),
        create_test_udword('different', 'ADV', 1, 'advmod', start=6, end=15),
        create_test_udword('word3', 'ADJ', 2, 'amod', start=16, end=21),
    ]

    alignment = align_words(gold_words, system_words)

    # Should only align word1 (matching span)
    assert len(alignment.matched_words) == 1
    assert alignment.matched_words[0].gold_word.token['form'] == 'word1'
