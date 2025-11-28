"""Tests for tree validation functionality."""

from __future__ import annotations

import conllu
import pytest
from conllu_tools.evaluation.base import UDError
from conllu_tools.evaluation.evaluator import ConlluEvaluator


def test_validation_with_empty_sentence() -> None:
    """Test validation with empty sentence (no words)."""
    evaluator = ConlluEvaluator()
    # Empty sentence
    sentence = conllu.TokenList([])

    with pytest.raises(UDError, match='has no words'):
        evaluator._validate_tree_structure(sentence, 'test1')


def test_validation_with_single_word_sentence() -> None:
    """Test validation with single-word sentence."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = word
1\tword\tword\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    # Should not raise
    evaluator._validate_tree_structure(sentence, 'test1')


def test_validation_with_multi_word_tokens() -> None:
    """Test validation with multi-word tokens."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = cannot go
1-2\tcannot\t_\t_\t_\t_\t_\t_\t_\t_
1\tcan\tcan\tAUX\t_\t_\t3\taux\t_\t_
2\tnot\tnot\tPART\t_\t_\t3\tadvmod\t_\t_
3\tgo\tgo\tVERB\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    # Should not raise - MWT range should be ignored in validation
    evaluator._validate_tree_structure(sentence, 'test1')


def test_validation_only_checks_words_not_mwt_ranges() -> None:
    """Test that validation only checks word tokens, not MWT ranges."""
    evaluator = ConlluEvaluator()
    # MWT range with tuple ID should be ignored
    text = """# sent_id = test1
# text = del mundo
1-2\tdel\t_\t_\t_\t_\t_\t_\t_\t_
1\tde\tde\tADP\t_\t_\t3\tcase\t_\t_
2\tel\tel\tDET\t_\t_\t3\tdet\t_\t_
3\tmundo\tmundo\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    # Should not raise
    evaluator._validate_tree_structure(sentence, 'test1')


def test_error_messages_include_sentence_id() -> None:
    """Test error messages include sentence ID."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = my_sentence_123
# text = word1 word2
1\tword1\tword1\tVERB\t_\t_\t0\troot\t_\t_
2\tword2\tword2\tVERB\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    with pytest.raises(UDError, match='my_sentence_123'):
        evaluator._validate_tree_structure(sentence, 'my_sentence_123')


def test_error_messages_include_word_form() -> None:
    """Test error messages include word form."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = word1 badword
1\tword1\tword1\tVERB\t_\t_\t0\troot\t_\t_
2\tbadword\tbadword\tNOUN\t_\t_\t10\tobj\t_\t_

"""
    sentence = conllu.parse(text)[0]

    with pytest.raises(UDError, match='badword'):
        evaluator._validate_tree_structure(sentence, 'test1')


def test_error_messages_include_specific_head_values() -> None:
    """Test error messages include specific HEAD values."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = word1 word2
1\tword1\tword1\tVERB\t_\t_\t0\troot\t_\t_
2\tword2\tword2\tNOUN\t_\t_\t99\tobj\t_\t_

"""
    sentence = conllu.parse(text)[0]

    with pytest.raises(UDError, match='HEAD 99'):
        evaluator._validate_tree_structure(sentence, 'test1')


def test_error_messages_include_word_id() -> None:
    """Test error messages include word ID."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = word1 word2
1\tword1\tword1\tVERB\t_\t_\t0\troot\t_\t_
2\tword2\tword2\tNOUN\t_\t_\t5\tobj\t_\t_

"""
    sentence = conllu.parse(text)[0]

    with pytest.raises(UDError, match='id=2'):
        evaluator._validate_tree_structure(sentence, 'test1')
