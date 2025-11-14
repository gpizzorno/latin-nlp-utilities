"""Initialization Tests for the main ConlluEvaluator class."""

from __future__ import annotations

from nlp_utilities.conllu.evaluators import ConlluEvaluator


def test_evaluator_default_initialization() -> None:
    """Test ConlluEvaluator with default parameters."""
    evaluator = ConlluEvaluator()

    assert evaluator.eval_deprels is True
    assert evaluator.treebank_type == {
        'no_gapping': False,
        'no_shared_parents_in_coordination': False,
        'no_shared_dependents_in_coordination': False,
        'no_control': False,
        'no_external_arguments_of_relative_clauses': False,
        'no_case_info': False,
    }


def test_evaluator_with_eval_deprels_false() -> None:
    """Test ConlluEvaluator with eval_deprels=False."""
    evaluator = ConlluEvaluator(eval_deprels=False)

    assert evaluator.eval_deprels is False


def test_treebank_type_single_digit() -> None:
    """Test treebank_type parsing with single digit."""
    evaluator = ConlluEvaluator(treebank_type='1')

    assert evaluator.treebank_type['no_gapping'] is True
    assert evaluator.treebank_type['no_shared_parents_in_coordination'] is False


def test_treebank_type_multiple_digits() -> None:
    """Test treebank_type parsing with multiple digits."""
    evaluator = ConlluEvaluator(treebank_type='12')

    assert evaluator.treebank_type['no_gapping'] is True
    assert evaluator.treebank_type['no_shared_parents_in_coordination'] is True
    assert evaluator.treebank_type['no_shared_dependents_in_coordination'] is False


def test_treebank_type_all_flags() -> None:
    """Test treebank_type parsing with all flags."""
    evaluator = ConlluEvaluator(treebank_type='123456')

    assert evaluator.treebank_type['no_gapping'] is True
    assert evaluator.treebank_type['no_shared_parents_in_coordination'] is True
    assert evaluator.treebank_type['no_shared_dependents_in_coordination'] is True
    assert evaluator.treebank_type['no_control'] is True
    assert evaluator.treebank_type['no_external_arguments_of_relative_clauses'] is True
    assert evaluator.treebank_type['no_case_info'] is True


def test_treebank_type_default_empty_string() -> None:
    """Test treebank_type parsing with empty string (default)."""
    evaluator = ConlluEvaluator(treebank_type='0')

    # '0' is not in '123456', so all should be False
    assert all(not v for v in evaluator.treebank_type.values())
