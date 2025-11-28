"""Functional Children Tests."""

from __future__ import annotations

import conllu
from conllu_tools.evaluation.evaluator import ConlluEvaluator


def test_functional_children_population() -> None:
    """Test functional_children are populated for MLAS metric."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = The big cat
1\tThe\tthe\tDET\t_\t_\t3\tdet\t_\t_
2\tbig\tbig\tADJ\t_\t_\t3\tamod\t_\t_
3\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Word 3 (cat) should have word 1 (The) as functional child
    assert len(words[2].functional_children) == 1  # type: ignore[arg-type]
    assert words[2].functional_children[0] == words[0]  # type: ignore[index]


def test_functional_children_with_multiple_children() -> None:
    """Test functional_children with multiple children."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = The big cat
1\tThe\tthe\tDET\t_\t_\t3\tdet\t_\t_
2\tbig\tbig\tADJ\t_\t_\t3\tamod\t_\t_
3\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Word 3 should have only det as functional child (not amod)
    assert len(words[2].functional_children) == 1  # type: ignore[arg-type]
    assert words[2].functional_children[0].token['deprel'] == 'det'  # type: ignore[index]


def test_functional_children_filtering_by_functional_deprels() -> None:
    """Test functional_children filtering by FUNCTIONAL_DEPRELS."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = in the house
1\tin\tin\tADP\t_\t_\t3\tcase\t_\t_
2\tthe\tthe\tDET\t_\t_\t3\tdet\t_\t_
3\thouse\thouse\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Word 3 should have both case and det as functional children
    assert len(words[2].functional_children) == 2  # type: ignore[arg-type]
    deprels = [child.token['deprel'] for child in words[2].functional_children]  # type: ignore[union-attr]
    assert 'case' in deprels
    assert 'det' in deprels


def test_functional_children_with_empty_list() -> None:
    """Test functional_children with no functional children."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = word
1\tword\tword\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Word should have empty functional_children list
    assert words[0].functional_children == []


def test_functional_children_normalization() -> None:
    """Test functional_children with deprel subtype normalization."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = the house
1\tthe\tthe\tDET\t_\t_\t2\tdet:def\t_\t_
2\thouse\thouse\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # det:def should be normalized to det and counted as functional
    assert len(words[1].functional_children) == 1  # type: ignore[arg-type]
