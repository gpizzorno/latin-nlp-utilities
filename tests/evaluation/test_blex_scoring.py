"""Tests for BLEX scoring."""

from __future__ import annotations

import conllu
from conllu_tools.evaluation import ConlluEvaluator


def test_blex_calculation() -> None:
    """Test BLEX (bilexical LAS) calculation."""
    evaluator = ConlluEvaluator()

    text = """# sent_id = 1
# text = cat runs
1\tcat\tcat\tNOUN\t_\t_\t2\tnsubj\t_\t_
2\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    assert scores['BLEX'].gold_total == 2
    assert scores['BLEX'].correct == 2


def test_blex_requires_head_deprel_lemma_match() -> None:
    """Test BLEX requires HEAD + DEPREL + LEMMA to match."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = cat runs
1\tcat\tcat\tNOUN\t_\t_\t2\tnsubj\t_\t_
2\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    # System has wrong lemma for first word
    system_text = """# sent_id = 1
# text = cat runs
1\tcat\tdog\tNOUN\t_\t_\t2\tnsubj\t_\t_
2\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # Only 1 of 2 correct
    assert scores['BLEX'].correct == 1


def test_blex_with_correct_lemmas() -> None:
    """Test BLEX with correct lemmas."""
    evaluator = ConlluEvaluator()

    text = """# sent_id = 1
# text = The cats run
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcats\tcat\tNOUN\t_\t_\t3\tnsubj\t_\t_
3\trun\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    # det is functional, so only 2 content words for BLEX
    assert scores['BLEX'].correct == 2


def test_blex_with_incorrect_lemmas() -> None:
    """Test BLEX with incorrect lemmas."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = cats run
1\tcats\tcat\tNOUN\t_\t_\t2\tnsubj\t_\t_
2\trun\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    # All lemmas wrong
    system_text = """# sent_id = 1
# text = cats run
1\tcats\tdog\tNOUN\t_\t_\t2\tnsubj\t_\t_
2\trun\twalk\tVERB\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    assert scores['BLEX'].correct == 0


def test_blex_lemma_underscore_handling() -> None:
    """Test BLEX handles underscore in gold lemma (always match)."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = cat runs
1\tcat\t_\tNOUN\t_\t_\t2\tnsubj\t_\t_
2\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    # System can have any lemma for first word
    system_text = """# sent_id = 1
# text = cat runs
1\tcat\twhatever\tNOUN\t_\t_\t2\tnsubj\t_\t_
2\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # Should match because gold lemma is '_'
    assert scores['BLEX'].correct == 2
