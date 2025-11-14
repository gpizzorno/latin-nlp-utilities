"""Tests for UPOS scoring."""

from __future__ import annotations

import conllu

from nlp_utilities.conllu.evaluators import ConlluEvaluator


def test_upos_matching_for_aligned_words() -> None:
    """Test UPOS matching for aligned words."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    system_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    assert scores['UPOS'].correct == 2
    assert scores['UPOS'].gold_total == 2


def test_upos_scoring_with_correct_predictions() -> None:
    """Test UPOS scoring with correct predictions."""
    evaluator = ConlluEvaluator()

    text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    assert scores['UPOS'].f1 == 1.0


def test_upos_scoring_with_incorrect_predictions() -> None:
    """Test UPOS scoring with incorrect predictions."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    system_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tVERB\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # Only 1 of 2 correct
    assert scores['UPOS'].correct == 1
    assert scores['UPOS'].f1 == 0.5


def test_upos_scoring_precision_recall_f1() -> None:
    """Test UPOS scoring precision, recall, and F1 calculation."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = The cat runs
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t3\tnsubj\t_\t_
3\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    system_text = """# sent_id = 1
# text = The cat runs
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tVERB\t_\t_\t3\tnsubj\t_\t_
3\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # 2 of 3 correct
    assert scores['UPOS'].correct == 2
    assert scores['UPOS'].precision == 2 / 3
    assert scores['UPOS'].recall == 2 / 3
    assert scores['UPOS'].f1 == 2 / 3
