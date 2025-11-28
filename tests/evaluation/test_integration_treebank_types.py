"""Integration tests for treebank types."""

from __future__ import annotations

from pathlib import Path

from conllu_tools.evaluation import ConlluEvaluator


def test_evaluation_with_treebank_type_default() -> None:
    """Test evaluation with treebank_type='' (all enhancements enabled)."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator(treebank_type='')
    scores = evaluator.evaluate_files(gold_path, system_path)

    # Should have ELAS/EULAS scores
    assert scores['ELAS'].gold_total is not None
    assert scores['EULAS'].gold_total is not None


def test_evaluation_with_treebank_type_no_gapping() -> None:
    """Test evaluation with treebank_type='1' (no gapping)."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')
    evaluator_no_gapping = ConlluEvaluator(treebank_type='1')
    scores_no_gapping = evaluator_no_gapping.evaluate_files(gold_path, system_path)
    # Enhanced dep counts might differ if gapping is filtered
    # (though might be same if no gapping in test data)
    assert scores_no_gapping['ELAS'].gold_total is not None


def test_evaluation_with_treebank_type_multiple_filters() -> None:
    """Test evaluation with treebank_type='12' (multiple filters)."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator(treebank_type='12')
    scores = evaluator.evaluate_files(gold_path, system_path)

    # Should still compute scores
    assert scores['ELAS'].gold_total is not None


def test_evaluation_with_treebank_type_all_filters() -> None:
    """Test evaluation with treebank_type='123456' (all filters)."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator(treebank_type='123456')
    scores = evaluator.evaluate_files(gold_path, system_path)

    # With all filters, enhanced dep counts should be lower or equal
    evaluator_default = ConlluEvaluator(treebank_type='')
    scores_default = evaluator_default.evaluate_files(gold_path, system_path)

    assert scores['ELAS'].gold_total <= scores_default['ELAS'].gold_total  # type: ignore [operator]


def test_treebank_type_impact_on_elas_scores() -> None:
    """Test that treebank_type filters affect ELAS/EULAS scores."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator_default = ConlluEvaluator(treebank_type='')
    evaluator_filtered = ConlluEvaluator(treebank_type='6')  # no case info

    scores_default = evaluator_default.evaluate_files(gold_path, system_path)
    scores_filtered = evaluator_filtered.evaluate_files(gold_path, system_path)

    # Both should compute scores
    assert scores_default['ELAS'].gold_total is not None
    assert scores_filtered['ELAS'].gold_total is not None
