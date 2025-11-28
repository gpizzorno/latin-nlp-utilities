"""Tests for CLAS scoring."""

from __future__ import annotations

import conllu
from conllu_tools.evaluation import ConlluEvaluator


def test_clas_calculation() -> None:
    """Test CLAS (content-word LAS) calculation."""
    evaluator = ConlluEvaluator()

    # All content words
    text = """# sent_id = 1
# text = cat runs
1\tcat\tcat\tNOUN\t_\t_\t2\tnsubj\t_\t_
2\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    # Both words are content words
    assert scores['CLAS'].gold_total == 2
    assert scores['CLAS'].correct == 2


def test_clas_filtering_by_content_deprels() -> None:
    """Test CLAS filters by CONTENT_DEPRELS."""
    evaluator = ConlluEvaluator()

    # Mix of content and functional relations
    text = """# sent_id = 1
# text = The cat runs
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t3\tnsubj\t_\t_
3\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    # Only 2 content words (nsubj, root), not det (functional)
    assert scores['CLAS'].gold_total == 2


def test_clas_deprel_normalization() -> None:
    """Test CLAS normalizes deprels (removes subtypes)."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = house
1\thouse\thouse\tNOUN\t_\t_\t0\tnmod:tmod\t_\t_

"""
    # System has base deprel (no subtype)
    system_text = """# sent_id = 1
# text = house
1\thouse\thouse\tNOUN\t_\t_\t0\tnmod\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # Should match after normalization
    assert scores['CLAS'].correct == 1


def test_clas_with_correct_predictions() -> None:
    """Test CLAS with correct predictions."""
    evaluator = ConlluEvaluator()

    text = """# sent_id = 1
# text = cat runs
1\tcat\tcat\tNOUN\t_\t_\t2\tnsubj\t_\t_
2\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    assert scores['CLAS'].f1 == 1.0


def test_clas_with_incorrect_predictions() -> None:
    """Test CLAS with incorrect predictions."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = cat runs
1\tcat\tcat\tNOUN\t_\t_\t2\tnsubj\t_\t_
2\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    # System has wrong deprel for first word
    system_text = """# sent_id = 1
# text = cat runs
1\tcat\tcat\tNOUN\t_\t_\t2\tobj\t_\t_
2\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    assert scores['CLAS'].correct == 1
    assert scores['CLAS'].f1 == 0.5
