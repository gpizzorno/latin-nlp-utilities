"""Tests for word processing edge cases and integration."""

from __future__ import annotations

import conllu

from nlp_utilities.conllu.evaluators.evaluator import UDEvaluator


def test_eval_deprels_false_skips_enhanced_processing() -> None:
    """Test that eval_deprels=False skips enhanced deps and functional children."""
    evaluator = UDEvaluator(eval_deprels=False)
    text = """# sent_id = test1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t2:det\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t0:root\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Enhanced deps should not be processed (set to None when eval_deprels=False)
    assert not hasattr(words[0], 'enhanced_deps') or words[0].enhanced_deps is None
    # Functional children should not be populated
    assert not hasattr(words[1], 'functional_children') or words[1].functional_children is None


def test_complex_sentence_with_mwt_and_deps() -> None:
    """Test complex sentence with MWTs and enhanced dependencies."""
    evaluator = UDEvaluator()
    text = """# sent_id = test1
# text = cannot go home
1-2\tcannot\t_\t_\t_\t_\t_\t_\t_\t_
1\tcan\tcan\tAUX\t_\t_\t3\taux\t3:aux\t_
2\tnot\tnot\tPART\t_\t_\t3\tadvmod\t3:advmod\t_
3\tgo\tgo\tVERB\t_\t_\t0\troot\t0:root\t_
4\thome\thome\tNOUN\t_\t_\t3\tobl\t3:obl\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Check structure is correct
    assert len(words) == 4
    assert words[0].is_multiword is True
    assert words[1].is_multiword is True
    assert words[2].is_multiword is False
    assert words[3].is_multiword is False

    # Check enhanced deps were processed
    assert len(words[0].enhanced_deps) > 0  # type: ignore[arg-type]
    assert len(words[2].enhanced_deps) > 0  # type: ignore[arg-type]


def test_sentence_with_multiple_mwts() -> None:
    """Test sentence with multiple multi-word tokens."""
    evaluator = UDEvaluator()
    text = """# sent_id = test1
# text = del al mundo
1-2\tdel\t_\t_\t_\t_\t_\t_\t_\t_
1\tde\tde\tADP\t_\t_\t5\tcase\t_\t_
2\tel\tel\tDET\t_\t_\t5\tdet\t_\t_
3-4\tal\t_\t_\t_\t_\t_\t_\t_\t_
3\ta\ta\tADP\t_\t_\t5\tcase\t_\t_
4\tel\tel\tDET\t_\t_\t5\tdet\t_\t_
5\tmundo\tmundo\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Check all words processed
    assert len(words) == 5

    # Check MWT flags
    assert words[0].is_multiword is True
    assert words[1].is_multiword is True
    assert words[2].is_multiword is True
    assert words[3].is_multiword is True
    assert words[4].is_multiword is False

    # Check spans
    assert words[0].span == words[1].span  # First MWT
    assert words[2].span == words[3].span  # Second MWT
    assert words[0].span != words[2].span  # Different MWTs
