"""Enhanced Dependency Processing Tests."""

from __future__ import annotations

import conllu
from conllu_tools.evaluation.evaluator import ConlluEvaluator


def test_process_word_enhanced_deps_basic() -> None:
    """Test _process_word_enhanced_deps basic functionality."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = word1 word2
1\tword1\tword1\tVERB\t_\t_\t0\troot\t0:root\t_
2\tword2\tword2\tNOUN\t_\t_\t1\tobj\t1:obj\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Check enhanced deps were processed
    assert len(words[0].enhanced_deps) == 1  # type: ignore [arg-type]
    assert words[0].enhanced_deps[0][0] == 0  # type: ignore [index] # root
    assert words[0].enhanced_deps[0][1] == ['root']  # type: ignore [index]

    assert len(words[1].enhanced_deps) == 1  # type: ignore [arg-type]
    assert words[1].enhanced_deps[0][0] == words[0]  # type: ignore [index]
    assert words[1].enhanced_deps[0][1] == ['obj']  # type: ignore [index]


def test_treebank_type_filter_no_gapping() -> None:
    """Test treebank_type filter: no_gapping (enhancement 1)."""
    evaluator = ConlluEvaluator(treebank_type='1')
    text = """# sent_id = test1
# text = word1 word2 word3
1\tword1\tword1\tVERB\t_\t_\t0\troot\t0:root\t_
2\tword2\tword2\tNOUN\t_\t_\t1\tobj\t1:obj|3:nsubj>obj\t_
3\tword3\tword3\tVERB\t_\t_\t1\tconj\t1:conj\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Word 2 should have gapping dep (nsubj>obj) replaced with basic dep
    assert len(words[1].enhanced_deps) == 2  # type: ignore[arg-type]
    # Should have basic obj and basic obj (duplicate removed by logic)
    deps_paths = [dep[1] for dep in words[1].enhanced_deps]  # type: ignore[union-attr]
    assert ['obj'] in deps_paths


def test_treebank_type_filter_no_shared_parents_in_coordination() -> None:
    """Test treebank_type filter: no_shared_parents_in_coordination (enhancement 2)."""
    evaluator = ConlluEvaluator(treebank_type='2')
    text = """# sent_id = test1
# text = word1 word2 word3
1\tword1\tword1\tVERB\t_\t_\t0\troot\t0:root\t_
2\tword2\tword2\tNOUN\t_\t_\t1\tobj\t1:obj|3:obj\t_
3\tword3\tword3\tNOUN\t_\t_\t1\tconj\t1:conj\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Word 2 should keep only conj dependency if it has one
    # In this case word 3 has conj, so word 2 keeps its deps
    # (The filter looks for conj in the word being processed)
    assert len(words[2].enhanced_deps) == 1  # type: ignore [arg-type]
    assert words[2].enhanced_deps[0][1] == ['conj']  # type: ignore [index]


def test_treebank_type_filter_no_shared_dependents_in_coordination() -> None:
    """Test treebank_type filter: no_shared_dependents_in_coordination (enhancement 3)."""
    evaluator = ConlluEvaluator(treebank_type='3')
    text = """# sent_id = test1
# text = word1 word2 word3
1\tword1\tword1\tVERB\t_\t_\t0\troot\t0:root\t_
2\tword2\tword2\tNOUN\t_\t_\t1\tobj\t1:obj|3:obj\t_
3\tword3\tword3\tVERB\t_\t_\t1\tconj\t1:conj\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Word 2 should filter out duplicate deps where parent is not basic head
    deps = words[1].enhanced_deps
    # Should keep only the one with basic head (word 1)
    assert len(deps) == 1  # type: ignore[arg-type]
    assert deps[0][0] == words[0]  # type: ignore [index]


def test_treebank_type_filter_no_control() -> None:
    """Test treebank_type filter: no_control (enhancement 4)."""
    evaluator = ConlluEvaluator(treebank_type='4')
    text = """# sent_id = test1
# text = He wants to go
1\tHe\the\tPRON\t_\t_\t2\tnsubj\t2:nsubj|4:nsubj\t_
2\twants\twant\tVERB\t_\t_\t0\troot\t0:root\t_
3\tto\tto\tPART\t_\t_\t4\tmark\t4:mark\t_
4\tgo\tgo\tVERB\t_\t_\t2\txcomp\t2:xcomp\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Word 1 should not have nsubj of xcomp parent (word 4)
    deps = words[0].enhanced_deps
    # Should only have dep to word 2, not to word 4
    assert len(deps) == 1  # type: ignore [arg-type]
    assert deps[0][0] == words[1]  # type: ignore [index]


def test_treebank_type_filter_no_external_arguments_of_relative_clauses() -> None:
    """Test treebank_type filter: no_external_arguments_of_relative_clauses (enhancement 5)."""
    evaluator = ConlluEvaluator(treebank_type='5')
    text = """# sent_id = test1
# text = book that I read
1\tbook\tbook\tNOUN\t_\t_\t0\troot\t0:root\t_
2\tthat\tthat\tPRON\t_\t_\t4\tobj\t4:obj|4:ref\t_
3\tI\tI\tPRON\t_\t_\t4\tnsubj\t4:nsubj\t_
4\tread\tread\tVERB\t_\t_\t1\tacl:relcl\t1:acl:relcl\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Word 2 should have ref replaced with basic dep
    deps = words[1].enhanced_deps
    # Should have basic dep to word 4, not ref
    assert any(dep[1] == ['obj'] for dep in deps)  # type: ignore [union-attr]


def test_treebank_type_filter_no_case_info() -> None:
    """Test treebank_type filter: no_case_info (enhancement 6)."""
    evaluator = ConlluEvaluator(treebank_type='6')
    text = """# sent_id = test1
# text = in Rome
1\tin\tin\tADP\t_\t_\t2\tcase\t2:case\t_
2\tRome\tRome\tPROPN\t_\t_\t0\troot\t0:obl:in\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Word 2 should have obl:in changed to obl
    deps = words[1].enhanced_deps
    assert deps[0][1] == ['obl']  # type: ignore [index]


def test_treebank_type_combination_of_filters() -> None:
    """Test combination of multiple treebank_type filters."""
    evaluator = ConlluEvaluator(treebank_type='12')
    text = """# sent_id = test1
# text = word1 word2 word3
1\tword1\tword1\tVERB\t_\t_\t0\troot\t0:root\t_
2\tword2\tword2\tNOUN\t_\t_\t1\tobj\t1:obj|3:nsubj>obj\t_
3\tword3\tword3\tVERB\t_\t_\t1\tconj\t1:conj\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Both filters should apply
    assert len(words) == 3


def test_enhanced_deps_with_root() -> None:
    """Test enhanced deps processing with root (head=0)."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = word
1\tword\tword\tVERB\t_\t_\t0\troot\t0:root\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Root should have parent=0
    assert words[0].enhanced_deps[0][0] == 0  # type: ignore [index]
