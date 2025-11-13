"""Error Handling Tests."""

from __future__ import annotations

import conllu
import pytest

from nlp_utilities.conllu.evaluators.base import UDError
from nlp_utilities.conllu.evaluators.evaluator import UDEvaluator


def test_error_with_empty_form_after_whitespace_removal() -> None:
    """Test error when FORM is empty after whitespace removal."""
    evaluator = UDEvaluator()
    # Create sentence with only whitespace in form
    text = """# sent_id = test1
# text = word
1\t\u00a0\tword\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    with pytest.raises(UDError, match='Empty FORM after removing whitespace'):
        evaluator._convert_to_words(sentence, 'test1')


def test_error_with_empty_mwt_form() -> None:
    """Test error when MWT FORM is empty after whitespace removal."""
    evaluator = UDEvaluator()
    text = """# sent_id = test1
# text = word
1-2\t\u00a0\t_\t_\t_\t_\t_\t_\t_\t_
1\tword\tword\tNOUN\t_\t_\t0\troot\t_\t_
2\tword\tword\tNOUN\t_\t_\t1\tobj\t_\t_

"""
    sentence = conllu.parse(text)[0]

    with pytest.raises(UDError, match='Empty FORM after removing whitespace in multi-word token'):
        evaluator._convert_to_words(sentence, 'test1')


def test_error_with_empty_nodes() -> None:
    """Test error when empty nodes are present (should raise UDError)."""
    evaluator = UDEvaluator()
    # Empty node has ID like "2.1"
    text = """# sent_id = test1
# text = word1 word2
1\tword1\tword1\tNOUN\t_\t_\t0\troot\t_\t_
2.1\tempty\tempty\tNOUN\t_\t_\t1\tobj\t_\t_
2\tword2\tword2\tVERB\t_\t_\t1\txcomp\t_\t_

"""
    sentence = conllu.parse(text)[0]

    with pytest.raises(UDError, match='still contains empty nodes'):
        evaluator._convert_to_words(sentence, 'test1')


def test_no_error_with_valid_sentence() -> None:
    """Test that valid sentences don't raise errors."""
    evaluator = UDEvaluator()
    text = """# sent_id = test1
# text = The cat sleeps
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t3\tnsubj\t_\t_
3\tsleeps\tsleep\tVERB\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    # Should not raise
    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')
    assert len(words) == 3
