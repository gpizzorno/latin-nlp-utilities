"""Tests for UAS scoring."""

from __future__ import annotations

import conllu
from conllu_tools.evaluation import ConlluEvaluator


def test_uas_calculation() -> None:
    """Test UAS (unlabeled attachment score) calculation."""
    evaluator = ConlluEvaluator()

    text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    assert scores['UAS'].f1 == 1.0


def test_uas_with_correct_head_predictions() -> None:
    """Test UAS with correct HEAD predictions."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = The cat runs
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t3\tnsubj\t_\t_
3\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    system_text = gold_text

    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    assert scores['UAS'].correct == 3


def test_uas_with_incorrect_head_predictions() -> None:
    """Test UAS with incorrect HEAD predictions."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = The cat runs
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t3\tnsubj\t_\t_
3\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    # System has wrong HEAD for first word
    system_text = """# sent_id = 1
# text = The cat runs
1\tThe\tthe\tDET\t_\t_\t3\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t3\tnsubj\t_\t_
3\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # Only 2 of 3 correct
    assert scores['UAS'].correct == 2
    assert scores['UAS'].f1 < 1.0


def test_uas_skipped_when_eval_deprels_false() -> None:
    """Test UAS is skipped when eval_deprels=False."""
    evaluator = ConlluEvaluator(eval_deprels=False)

    text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    # UAS should be None when eval_deprels=False
    assert scores['UAS'].gold_total is None
    assert scores['UAS'].system_total is None
    assert scores['UAS'].correct is None
