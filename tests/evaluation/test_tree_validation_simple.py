"""Tests for tree validation functionality."""

from __future__ import annotations

import conllu
import pytest
from conllu_tools.evaluation.base import UDError
from conllu_tools.evaluation.evaluator import ConlluEvaluator


def test_valid_tree_structure_passes() -> None:
    """Test that a valid tree structure passes validation."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = The cat sleeps
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t3\tnsubj\t_\t_
3\tsleeps\tsleep\tVERB\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]
    # Should not raise
    evaluator._validate_tree_structure(sentence, 'test1')


def test_detection_of_missing_root() -> None:
    """Test detection of missing root (no word with head=0)."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = word1 word2
1\tword1\tword1\tNOUN\t_\t_\t2\tnsubj\t_\t_
2\tword2\tword2\tVERB\t_\t_\t1\tdep\t_\t_

"""
    sentence = conllu.parse(text)[0]

    with pytest.raises(UDError, match='No root node found'):
        evaluator._validate_tree_structure(sentence, 'test1')


def test_detection_of_multiple_roots() -> None:
    """Test detection of multiple roots."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = word1 word2
1\tword1\tword1\tVERB\t_\t_\t0\troot\t_\t_
2\tword2\tword2\tVERB\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    with pytest.raises(UDError, match='Multiple roots found'):
        evaluator._validate_tree_structure(sentence, 'test1')


def test_detection_of_invalid_head_negative() -> None:
    """Test detection of invalid HEAD values (negative)."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = word1 word2
1\tword1\tword1\tVERB\t_\t_\t0\troot\t_\t_
2\tword2\tword2\tNOUN\t_\t_\t-1\tobj\t_\t_

"""
    sentence = conllu.parse(text)[0]

    with pytest.raises(UDError, match=r'HEAD -1.*is out of range'):
        evaluator._validate_tree_structure(sentence, 'test1')


def test_detection_of_invalid_head_exceeds_word_count() -> None:
    """Test detection of invalid HEAD values (exceeds word count)."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = word1 word2
1\tword1\tword1\tVERB\t_\t_\t0\troot\t_\t_
2\tword2\tword2\tNOUN\t_\t_\t5\tobj\t_\t_

"""
    sentence = conllu.parse(text)[0]

    with pytest.raises(UDError, match=r'HEAD 5.*is out of range'):
        evaluator._validate_tree_structure(sentence, 'test1')


def test_detection_of_non_sequential_word_ids() -> None:
    """Test detection of non-sequential word IDs."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = word1 word2
1\tword1\tword1\tVERB\t_\t_\t0\troot\t_\t_
3\tword2\tword2\tNOUN\t_\t_\t1\tobj\t_\t_

"""
    sentence = conllu.parse(text)[0]

    with pytest.raises(UDError, match='Expected word ID 2, got 3'):
        evaluator._validate_tree_structure(sentence, 'test1')


def test_detection_of_cycles() -> None:
    """Test detection of cycles in dependency tree (detected as missing root)."""
    evaluator = ConlluEvaluator()
    # Create a cycle: word1 -> word2 -> word1 (no root)
    text = """# sent_id = test1
# text = word1 word2
1\tword1\tword1\tVERB\t_\t_\t2\tdep\t_\t_
2\tword2\tword2\tNOUN\t_\t_\t1\tdep\t_\t_

"""
    sentence = conllu.parse(text)[0]

    # Cycle detected as missing root since neither word has head=0
    with pytest.raises(UDError, match='No root node found'):
        evaluator._validate_tree_structure(sentence, 'test1')


def test_validation_skipped_when_eval_deprels_false() -> None:
    """Test validation is skipped when eval_deprels=False."""
    evaluator = ConlluEvaluator(eval_deprels=False)
    # Create an invalid tree (cycle)
    text = """# sent_id = test1
# text = word1 word2
1\tword1\tword1\tVERB\t_\t_\t2\tdep\t_\t_
2\tword2\tword2\tNOUN\t_\t_\t1\tdep\t_\t_

"""
    sentence = conllu.parse(text)[0]

    # Should not raise because validation is skipped
    evaluator._validate_tree_structure(sentence, 'test1')
