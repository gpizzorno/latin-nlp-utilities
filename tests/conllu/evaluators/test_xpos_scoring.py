"""Tests for XPOS scoring."""

from __future__ import annotations

import conllu

from nlp_utilities.conllu.evaluators import UDEvaluator


def test_xpos_matching_for_aligned_words() -> None:
    """Test XPOS matching for aligned words."""
    evaluator = UDEvaluator()

    gold_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\tDT\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\tNN\t_\t0\troot\t_\t_

"""
    system_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\tDT\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\tNN\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    assert scores['XPOS'].correct == 2


def test_xpos_scoring_with_correct_predictions() -> None:
    """Test XPOS scoring with correct predictions."""
    evaluator = UDEvaluator()

    text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\tDT\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\tNN\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    assert scores['XPOS'].f1 == 1.0


def test_xpos_scoring_with_incorrect_predictions() -> None:
    """Test XPOS scoring with incorrect predictions."""
    evaluator = UDEvaluator()

    gold_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\tDT\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\tNN\t_\t0\troot\t_\t_

"""
    system_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\tDT\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\tVB\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    assert scores['XPOS'].correct == 1
    assert scores['XPOS'].f1 == 0.5
