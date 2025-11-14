"""Tests for tree validation functionality."""

from __future__ import annotations

import conllu
import pytest

from nlp_utilities.conllu.evaluators.base import UDError
from nlp_utilities.conllu.evaluators.evaluator import ConlluEvaluator


def test_validation_with_complex_valid_tree() -> None:
    """Test validation with a complex but valid tree structure."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = The big cat sleeps on the mat
1\tThe\tthe\tDET\t_\t_\t3\tdet\t_\t_
2\tbig\tbig\tADJ\t_\t_\t3\tamod\t_\t_
3\tcat\tcat\tNOUN\t_\t_\t4\tnsubj\t_\t_
4\tsleeps\tsleep\tVERB\t_\t_\t0\troot\t_\t_
5\ton\ton\tADP\t_\t_\t7\tcase\t_\t_
6\tthe\tthe\tDET\t_\t_\t7\tdet\t_\t_
7\tmat\tmat\tNOUN\t_\t_\t4\tobl\t_\t_

"""
    sentence = conllu.parse(text)[0]

    # Should not raise
    evaluator._validate_tree_structure(sentence, 'test1')


def test_validation_with_deep_tree() -> None:
    """Test validation with a deeply nested tree structure."""
    evaluator = ConlluEvaluator()
    # Create a chain: root -> word1 -> word2 -> word3 -> word4
    text = """# sent_id = test1
# text = word0 word1 word2 word3 word4
1\tword0\tword0\tVERB\t_\t_\t0\troot\t_\t_
2\tword1\tword1\tNOUN\t_\t_\t1\tobj\t_\t_
3\tword2\tword2\tADP\t_\t_\t2\tcase\t_\t_
4\tword3\tword3\tNOUN\t_\t_\t3\tobl\t_\t_
5\tword4\tword4\tDET\t_\t_\t4\tdet\t_\t_

"""
    sentence = conllu.parse(text)[0]

    # Should not raise
    evaluator._validate_tree_structure(sentence, 'test1')


def test_validation_with_multiple_children_per_node() -> None:
    """Test validation with nodes having multiple children."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = root child1 child2 child3
1\troot\troot\tVERB\t_\t_\t0\troot\t_\t_
2\tchild1\tchild1\tNOUN\t_\t_\t1\tnsubj\t_\t_
3\tchild2\tchild2\tNOUN\t_\t_\t1\tobj\t_\t_
4\tchild3\tchild3\tADP\t_\t_\t1\tobl\t_\t_

"""
    sentence = conllu.parse(text)[0]

    # Should not raise
    evaluator._validate_tree_structure(sentence, 'test1')


def test_validation_with_projective_tree() -> None:
    """Test validation with a projective (non-crossing) tree."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = The cat sat on mat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t3\tnsubj\t_\t_
3\tsat\tsit\tVERB\t_\t_\t0\troot\t_\t_
4\ton\ton\tADP\t_\t_\t5\tcase\t_\t_
5\tmat\tmat\tNOUN\t_\t_\t3\tobl\t_\t_

"""
    sentence = conllu.parse(text)[0]

    # Should not raise
    evaluator._validate_tree_structure(sentence, 'test1')


def test_validation_with_nonprojective_tree() -> None:
    """Test validation with a non-projective (crossing) tree."""
    evaluator = ConlluEvaluator()
    # Non-projective: word2 depends on word4, crossing over word3
    text = """# sent_id = test1
# text = word1 word2 word3 word4
1\tword1\tword1\tVERB\t_\t_\t0\troot\t_\t_
2\tword2\tword2\tNOUN\t_\t_\t4\tnsubj\t_\t_
3\tword3\tword3\tADV\t_\t_\t1\tadvmod\t_\t_
4\tword4\tword4\tVERB\t_\t_\t1\txcomp\t_\t_

"""
    sentence = conllu.parse(text)[0]

    # Should not raise - non-projectivity is allowed in UD
    evaluator._validate_tree_structure(sentence, 'test1')


def test_validation_with_self_loop() -> None:
    """Test that self-loop passes basic validation (conllu library doesn't detect it)."""
    evaluator = ConlluEvaluator()
    # Word 2 points to itself (self-loop)
    text = """# sent_id = test1
# text = word1 word2
1\tword1\tword1\tVERB\t_\t_\t0\troot\t_\t_
2\tword2\tword2\tNOUN\t_\t_\t2\tobj\t_\t_

"""
    sentence = conllu.parse(text)[0]

    # Self-loops are not detected by conllu.to_tree() - it just ignores them
    # So this passes validation (though it's semantically invalid)
    evaluator._validate_tree_structure(sentence, 'test1')


def test_validation_with_three_way_cycle() -> None:
    """Test detection of three-way cycle (detected as missing root)."""
    evaluator = ConlluEvaluator()
    # Cycle: word1 -> word2 -> word3 -> word1 (no root)
    text = """# sent_id = test1
# text = word1 word2 word3
1\tword1\tword1\tVERB\t_\t_\t2\tdep\t_\t_
2\tword2\tword2\tNOUN\t_\t_\t3\tdep\t_\t_
3\tword3\tword3\tADJ\t_\t_\t1\tdep\t_\t_

"""
    sentence = conllu.parse(text)[0]

    # Cycle detected as missing root since no word has head=0
    with pytest.raises(UDError, match='No root node found'):
        evaluator._validate_tree_structure(sentence, 'test1')
