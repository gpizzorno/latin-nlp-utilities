"""Sentence/character sequence tests."""

from __future__ import annotations

import conllu
import pytest
from conllu_tools.evaluation import ConlluEvaluator
from conllu_tools.evaluation.base import UDError


def test_evaluate_sentences_identical() -> None:
    """Test _evaluate_sentences with identical gold and system."""
    evaluator = ConlluEvaluator()

    text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    # All scores should be perfect
    assert scores['Tokens'].f1 == 1.0
    assert scores['Sentences'].f1 == 1.0
    assert scores['Words'].f1 == 1.0
    assert scores['UPOS'].f1 == 1.0
    assert scores['LAS'].f1 == 1.0


def test_evaluate_sentences_completely_different() -> None:
    """Test _evaluate_sentences with completely different sentences."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    system_text = """# sent_id = 1
# text = A dog
1\tA\ta\tDET\t_\t_\t2\tdet\t_\t_
2\tdog\tdog\tNOUN\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    with pytest.raises(UDError, match='Text mismatch'):
        evaluator._evaluate_sentences(gold_sentences, system_sentences)


def test_evaluate_sentences_partial_match() -> None:
    """Test _evaluate_sentences with partial matches."""
    evaluator = ConlluEvaluator()

    # Same words, different POS tags
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

    # Tokens and words should match, but UPOS should not
    assert scores['Tokens'].f1 == 1.0
    assert scores['Words'].f1 == 1.0
    assert scores['UPOS'].f1 < 1.0  # One word has wrong UPOS


def test_character_mismatch_detection() -> None:
    """Test character mismatch detection raises UDError."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    system_text = """# sent_id = 1
# text = The dog
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tdog\tdog\tNOUN\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    with pytest.raises(UDError, match='Text mismatch'):
        evaluator._evaluate_sentences(gold_sentences, system_sentences)


def test_character_mismatch_error_message() -> None:
    """Test character mismatch error message formatting."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = test1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    system_text = """# sent_id = test1
# text = The dog
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tdog\tdog\tNOUN\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    with pytest.raises(UDError) as exc_info:
        evaluator._evaluate_sentences(gold_sentences, system_sentences)

    error_msg = str(exc_info.value)
    assert 'test1' in error_msg  # Sentence ID should be in error
    assert 'cat' in error_msg or 'dog' in error_msg  # Some context should be shown


def test_character_mismatch_with_context_display() -> None:
    """Test character mismatch shows context (20 chars)."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = The quick brown fox
1\tThe\tthe\tDET\t_\t_\t4\tdet\t_\t_
2\tquick\tquick\tADJ\t_\t_\t4\tamod\t_\t_
3\tbrown\tbrown\tADJ\t_\t_\t4\tamod\t_\t_
4\tfox\tfox\tNOUN\t_\t_\t0\troot\t_\t_

"""
    system_text = """# sent_id = 1
# text = The quick black cat
1\tThe\tthe\tDET\t_\t_\t4\tdet\t_\t_
2\tquick\tquick\tADJ\t_\t_\t4\tamod\t_\t_
3\tblack\tblack\tADJ\t_\t_\t4\tamod\t_\t_
4\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    with pytest.raises(UDError) as exc_info:
        evaluator._evaluate_sentences(gold_sentences, system_sentences)

    error_msg = str(exc_info.value)
    assert 'First 20 differing characters' in error_msg
