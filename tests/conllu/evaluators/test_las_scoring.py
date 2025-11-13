"""Tests for LAS scoring."""

from __future__ import annotations

import conllu

from nlp_utilities.conllu.evaluators import UDEvaluator


def test_las_calculation() -> None:
    """Test LAS (labeled attachment score) calculation."""
    evaluator = UDEvaluator()

    text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    assert scores['LAS'].f1 == 1.0


def test_las_requires_both_head_and_deprel_match() -> None:
    """Test LAS requires both HEAD and DEPREL to match."""
    evaluator = UDEvaluator()

    gold_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    # System has correct HEAD but wrong DEPREL
    system_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tnmod\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # UAS should have 2 correct, but LAS should have only 1 (second word)
    assert scores['UAS'].correct == 2
    assert scores['LAS'].correct == 1


def test_las_with_correct_predictions() -> None:
    """Test LAS with correct predictions."""
    evaluator = UDEvaluator()

    text = """# sent_id = 1
# text = The cat runs
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t3\tnsubj\t_\t_
3\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    assert scores['LAS'].correct == 3


def test_las_with_incorrect_predictions() -> None:
    """Test LAS with incorrect predictions."""
    evaluator = UDEvaluator()

    gold_text = """# sent_id = 1
# text = The cat runs
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t3\tnsubj\t_\t_
3\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    # System has some wrong attachments
    system_text = """# sent_id = 1
# text = The cat runs
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t3\tobj\t_\t_
3\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # 2 of 3 correct (second word has wrong DEPREL)
    assert scores['LAS'].correct == 2


def test_las_skipped_when_eval_deprels_false() -> None:
    """Test LAS is skipped when eval_deprels=False."""
    evaluator = UDEvaluator(eval_deprels=False)

    text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    assert scores['LAS'].gold_total is None
