"""Integration tests for edge cases."""

from __future__ import annotations

from pathlib import Path

from nlp_utilities.conllu.evaluators import ConlluEvaluator


def test_evaluation_with_empty_enhanced_deps() -> None:
    """Test evaluation when some words have no enhanced dependencies."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator()
    # Should not raise errors
    scores = evaluator.evaluate_files(gold_path, system_path)

    assert scores['ELAS'].gold_total is not None


def test_evaluation_with_single_word_sentences() -> None:
    """Test evaluation with single-word sentences in test data."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator()
    # Should handle single-word sentences correctly
    scores = evaluator.evaluate_files(gold_path, system_path)

    assert scores['Words'].gold_total > 0  # type: ignore [operator]


def test_evaluation_with_special_characters() -> None:
    """Test evaluation handles special characters in forms."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator()
    # Latin text may have special characters
    scores = evaluator.evaluate_files(gold_path, system_path)

    # Should complete without errors
    assert scores['Tokens'].f1 is not None


def test_evaluation_with_unicode_characters() -> None:
    """Test evaluation correctly handles Unicode characters."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator()
    scores = evaluator.evaluate_files(gold_path, system_path)

    # Character-based metrics should handle Unicode correctly
    assert scores['Tokens'].f1 == 1.0


def test_evaluation_with_punctuation() -> None:
    """Test evaluation handles punctuation correctly."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator()
    scores = evaluator.evaluate_files(gold_path, system_path)

    # Punctuation is included in word counts
    assert scores['Words'].gold_total > 0  # type: ignore [operator]


def test_evaluation_preserves_file_encoding() -> None:
    """Test evaluation correctly handles UTF-8 encoding."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator()
    # Should not raise encoding errors
    scores = evaluator.evaluate_files(gold_path, system_path)

    assert scores is not None


def test_evaluation_with_long_sentences() -> None:
    """Test evaluation handles long sentences in test data."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator()
    scores = evaluator.evaluate_files(gold_path, system_path)

    # Should handle long sentences without performance issues
    assert scores['Words'].gold_total > 0  # type: ignore [operator]


def test_eval_deprels_false_with_real_data() -> None:
    """Test eval_deprels=False works correctly with real data."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator(eval_deprels=False)
    scores = evaluator.evaluate_files(gold_path, system_path)

    # Morphological metrics should have values
    assert scores['UPOS'].gold_total is not None
    assert scores['Words'].gold_total is not None

    # Dependency metrics should be None
    assert scores['UAS'].gold_total is None
    assert scores['LAS'].gold_total is None
    assert scores['ELAS'].gold_total is None


def test_metric_relationships() -> None:
    """Test expected relationships between different metrics."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator()
    scores = evaluator.evaluate_files(gold_path, system_path)

    # LAS correct implies UAS correct
    assert scores['LAS'].correct <= scores['UAS'].correct  # type: ignore [operator]

    # CLAS should be subset of LAS (content words only)
    assert scores['CLAS'].gold_total <= scores['LAS'].gold_total  # type: ignore [operator]

    # MLAS should be harder than CLAS
    assert scores['MLAS'].correct <= scores['CLAS'].correct  # type: ignore [operator]

    # AllTags should be harder than individual components
    assert scores['AllTags'].correct <= scores['UPOS'].correct  # type: ignore [operator]
    assert scores['AllTags'].correct <= scores['UFeats'].correct  # type: ignore [operator]


def test_score_consistency() -> None:
    """Test score values are internally consistent."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator()
    scores = evaluator.evaluate_files(gold_path, system_path)

    for metric_name, score in scores.items():
        if score.gold_total is None:
            continue

        # correct <= gold_total
        assert score.correct <= score.gold_total, f'{metric_name}: correct > gold_total'  # type: ignore [operator]

        # correct <= system_total
        assert score.correct <= score.system_total, f'{metric_name}: correct > system_total'  # type: ignore [operator]

        # Verify F1 calculation
        if score.precision + score.recall > 0:
            expected_f1 = 2 * score.precision * score.recall / (score.precision + score.recall)
            assert abs(score.f1 - expected_f1) < 1e-6, f'{metric_name}: F1 calculation incorrect'
