"""Integration tests real-world data."""

from __future__ import annotations

from pathlib import Path

from nlp_utilities.conllu.evaluators import ConlluEvaluator


def test_evaluation_with_latin_test_data() -> None:
    """Test evaluation with actual Latin test data."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator()
    scores = evaluator.evaluate_files(gold_path, system_path)

    # Basic sanity checks on Latin data
    assert scores['Tokens'].f1 == 1.0  # Token boundaries should match exactly
    assert scores['Sentences'].f1 == 1.0  # Sentence count should match
    assert scores['Words'].f1 == 1.0  # Word count should match

    # UPOS should be reasonable for parser output
    assert scores['UPOS'].f1 > 0.5
    assert scores['UPOS'].f1 < 1.0

    # LAS should be lower than UAS (harder metric)
    assert scores['LAS'].f1 <= scores['UAS'].f1


def test_evaluation_with_multiword_tokens() -> None:
    """Test evaluation correctly handles multi-word tokens in test data."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator()
    # Should not raise errors with MWTs
    scores = evaluator.evaluate_files(gold_path, system_path)

    # Tokens and Words should differ if MWTs are present
    # (but in this specific data they might be equal)
    assert scores['Tokens'].gold_total >= scores['Words'].gold_total  # type: ignore [operator]


def test_evaluation_with_enhanced_dependencies() -> None:
    """Test evaluation with enhanced dependencies in test data."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator()
    scores = evaluator.evaluate_files(gold_path, system_path)

    # ELAS and EULAS should have values
    assert scores['ELAS'].gold_total is not None
    assert scores['EULAS'].gold_total is not None

    # EULAS (unlabeled) should be >= ELAS (labeled)
    assert scores['EULAS'].f1 >= scores['ELAS'].f1


def test_evaluation_with_content_vs_functional_relations() -> None:
    """Test CLAS correctly filters content vs functional relations."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator()
    scores = evaluator.evaluate_files(gold_path, system_path)

    # CLAS should have fewer words than LAS (only content words)
    assert scores['CLAS'].gold_total <= scores['LAS'].gold_total  # type: ignore [operator]


def test_evaluation_with_functional_children() -> None:
    """Test MLAS correctly handles functional children."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator()
    scores = evaluator.evaluate_files(gold_path, system_path)

    # MLAS should be more strict than CLAS
    assert scores['MLAS'].f1 <= scores['CLAS'].f1


def test_evaluation_with_complex_morphology() -> None:
    """Test evaluation with complex Latin morphological features."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator()
    scores = evaluator.evaluate_files(gold_path, system_path)

    # UFeats should have total counts
    assert scores['UFeats'].gold_total is not None
    assert scores['UFeats'].gold_total > 0

    # AllTags (UPOS+XPOS+UFeats) should be harder than individual components
    assert scores['AllTags'].f1 <= scores['UPOS'].f1
    assert scores['AllTags'].f1 <= scores['UFeats'].f1


def test_evaluation_with_various_pos_tags() -> None:
    """Test evaluation handles various POS tags correctly."""
    gold_path = Path('tests/test_data/gold.conllu')
    system_path = Path('tests/test_data/system.conllu')

    evaluator = ConlluEvaluator()
    scores = evaluator.evaluate_files(gold_path, system_path)

    # UPOS precision and recall should be equal (same number of words)
    assert abs(scores['UPOS'].precision - scores['UPOS'].recall) < 1e-6
