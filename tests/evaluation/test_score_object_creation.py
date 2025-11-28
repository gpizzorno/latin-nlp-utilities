"""Tests for score object creation."""

from __future__ import annotations

import conllu
from conllu_tools.evaluation import ConlluEvaluator


def test_scores_dictionary_creation() -> None:
    """Test scores dictionary is created with all metrics."""
    evaluator = ConlluEvaluator()

    text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    assert isinstance(scores, dict)
    assert len(scores) > 0


def test_all_metrics_present_in_scores() -> None:
    """Test all expected metrics are present in scores."""
    evaluator = ConlluEvaluator()

    text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

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


def test_scores_with_eval_deprels_false() -> None:
    """Test scores with eval_deprels=False have None values for dependency metrics."""
    evaluator = ConlluEvaluator(eval_deprels=False)

    text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    # Morphology metrics should have values
    assert scores['UPOS'].gold_total is not None
    assert scores['Words'].gold_total is not None

    # Dependency metrics should be None
    assert scores['UAS'].gold_total is None
    assert scores['LAS'].gold_total is None
    assert scores['CLAS'].gold_total is None
    assert scores['MLAS'].gold_total is None
    assert scores['BLEX'].gold_total is None
    assert scores['ELAS'].gold_total is None
    assert scores['EULAS'].gold_total is None


def test_aligned_total_tracking_across_sentences() -> None:
    """Test aligned_total is tracked across all sentences."""
    evaluator = ConlluEvaluator()

    text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

# sent_id = 2
# text = A dog
1\tA\ta\tDET\t_\t_\t2\tdet\t_\t_
2\tdog\tdog\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    # Should track total aligned words across both sentences (4 words total)
    assert scores['UPOS'].aligned_total == 4
    assert scores['LAS'].aligned_total == 4
