"""Lemma Scoring Tests."""

from __future__ import annotations

import conllu

from nlp_utilities.conllu.evaluators import UDEvaluator


def test_lemma_matching_for_aligned_words() -> None:
    """Test lemma matching for aligned words."""
    evaluator = UDEvaluator()

    gold_text = """# sent_id = 1
# text = runs
1\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    system_text = """# sent_id = 1
# text = runs
1\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    assert scores['Lemmas'].correct == 1


def test_lemma_scoring_with_underscore_handling() -> None:
    """Test lemma scoring with underscore handling (gold='_' means always match)."""
    evaluator = UDEvaluator()

    gold_text = """# sent_id = 1
# text = runs
1\truns\t_\tVERB\t_\t_\t0\troot\t_\t_

"""
    # System has any lemma
    system_text = """# sent_id = 1
# text = runs
1\truns\twhatever\tVERB\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # Should match because gold lemma is '_'
    assert scores['Lemmas'].correct == 1


def test_lemma_scoring_with_correct_predictions() -> None:
    """Test lemma scoring with correct predictions."""
    evaluator = UDEvaluator()

    text = """# sent_id = 1
# text = The cat runs
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t3\tnsubj\t_\t_
3\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    assert scores['Lemmas'].f1 == 1.0


def test_lemma_scoring_with_incorrect_predictions() -> None:
    """Test lemma scoring with incorrect predictions."""
    evaluator = UDEvaluator()

    gold_text = """# sent_id = 1
# text = The cat runs
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t3\tnsubj\t_\t_
3\truns\trun\tVERB\t_\t_\t0\troot\t_\t_

"""
    system_text = """# sent_id = 1
# text = The cat runs
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tdog\tNOUN\t_\t_\t3\tnsubj\t_\t_
3\truns\twalk\tVERB\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # Only 1 of 3 correct
    assert scores['Lemmas'].correct == 1
    assert scores['Lemmas'].f1 < 1.0
