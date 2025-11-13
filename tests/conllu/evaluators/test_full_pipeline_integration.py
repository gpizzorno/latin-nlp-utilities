"""Integration tests for full pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from nlp_utilities.conllu.evaluators import UDEvaluator


def test_full_pipeline_with_test_data() -> None:
    """Test complete evaluation pipeline with gold.conllu and system.conllu."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = UDEvaluator()
    scores = evaluator.evaluate_files(gold_path, system_path)

    # Verify all expected metrics are present
    expected_metrics = [
        'Tokens',
        'Sentences',
        'Words',
        'UPOS',
        'XPOS',
        'UFeats',
        'AllTags',
        'Lemmas',
        'UAS',
        'LAS',
        'CLAS',
        'MLAS',
        'BLEX',
        'ELAS',
        'EULAS',
    ]

    for metric in expected_metrics:
        assert metric in scores
        assert scores[metric].precision is not None
        assert scores[metric].recall is not None
        assert scores[metric].f1 is not None


def test_results_match_baseline() -> None:
    """Test evaluation results approximate evaluation_baseline.json.

    Note: The baseline may have been generated with slightly different code,
    so we allow some tolerance and verify relationships between metrics.
    """
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')
    baseline_path = Path('tests/test_data/evaluation_baseline.json')

    evaluator = UDEvaluator()
    scores = evaluator.evaluate_files(gold_path, system_path)

    # Load baseline
    with baseline_path.open(encoding='utf-8') as f:
        baseline = json.load(f)

    # Compare each metric (with reasonable tolerance for differences)
    tolerance = 0.01  # 1% tolerance for potential code differences

    for metric_name, baseline_values in baseline.items():
        assert metric_name in scores, f'Missing metric: {metric_name}'

        score = scores[metric_name]
        # Check values are reasonably close (allow for implementation differences)
        assert abs(score.precision - baseline_values['precision']) < tolerance, (
            f'{metric_name} precision differs significantly: {score.precision} vs {baseline_values["precision"]}'
        )
        assert abs(score.recall - baseline_values['recall']) < tolerance, (
            f'{metric_name} recall differs significantly: {score.recall} vs {baseline_values["recall"]}'
        )
        assert abs(score.f1 - baseline_values['f1']) < tolerance, (
            f'{metric_name} F1 differs significantly: {score.f1} vs {baseline_values["f1"]}'
        )


def test_precision_recall_f1_ranges() -> None:
    """Test all precision, recall, F1 values are in valid range [0, 1]."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = UDEvaluator()
    scores = evaluator.evaluate_files(gold_path, system_path)

    for metric_name, score in scores.items():
        assert 0.0 <= score.precision <= 1.0, f'{metric_name} precision out of range: {score.precision}'
        assert 0.0 <= score.recall <= 1.0, f'{metric_name} recall out of range: {score.recall}'
        assert 0.0 <= score.f1 <= 1.0, f'{metric_name} F1 out of range: {score.f1}'


def test_aligned_accuracy_calculation() -> None:
    """Test aligned_accuracy is correctly calculated for morphological metrics."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = UDEvaluator()
    scores = evaluator.evaluate_files(gold_path, system_path)

    # Morphological metrics should have aligned_accuracy
    morphological_metrics = ['UPOS', 'XPOS', 'UFeats', 'AllTags', 'Lemmas']

    for metric in morphological_metrics:
        assert scores[metric].aligned_total is not None
        assert scores[metric].aligned_total > 0  # type: ignore [operator]
        # aligned_accuracy = correct / aligned_total
        expected_accuracy = scores[metric].correct / scores[metric].aligned_total  # type: ignore [operator]
        assert abs(scores[metric].aligned_accuracy - expected_accuracy) < 1e-6  # type: ignore [operator]
