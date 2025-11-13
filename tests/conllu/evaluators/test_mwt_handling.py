"""Multi-word Token Handling Tests."""

from __future__ import annotations

import conllu

from nlp_utilities.conllu.evaluators.base import UDSpan
from nlp_utilities.conllu.evaluators.evaluator import UDEvaluator


def test_mwt_span_assignment() -> None:
    """Test MWT span is correctly assigned to constituent words."""
    evaluator = UDEvaluator()
    text = """# sent_id = test1
# text = del mundo
1-2\tdel\t_\t_\t_\t_\t_\t_\t_\t_
1\tde\tde\tADP\t_\t_\t3\tcase\t_\t_
2\tel\tel\tDET\t_\t_\t3\tdet\t_\t_
3\tmundo\tmundo\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Both words in MWT should have same span
    assert words[0].span == words[1].span
    assert words[0].span == UDSpan(0, 3)  # 'del'

    # Third word has its own span
    assert words[2].span == UDSpan(3, 8)  # 'mundo'


def test_mwt_range_detection() -> None:
    """Test MWT range detection with tuple IDs."""
    evaluator = UDEvaluator()
    text = """# sent_id = test1
# text = cannot
1-2\tcannot\t_\t_\t_\t_\t_\t_\t_\t_
1\tcan\tcan\tAUX\t_\t_\t3\taux\t_\t_
2\tnot\tnot\tPART\t_\t_\t3\tadvmod\t_\t_
3\tgo\tgo\tVERB\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # First two words should be marked as multiword
    assert words[0].is_multiword is True
    assert words[1].is_multiword is True
    assert words[2].is_multiword is False


def test_mwt_flag_setting() -> None:
    """Test is_multiword flag is correctly set on UDWord objects."""
    evaluator = UDEvaluator()
    text = """# sent_id = test1
# text = word1 del word2
1\tword1\tword1\tNOUN\t_\t_\t0\troot\t_\t_
2-3\tdel\t_\t_\t_\t_\t_\t_\t_\t_
2\tde\tde\tADP\t_\t_\t1\tcase\t_\t_
3\tel\tel\tDET\t_\t_\t1\tdet\t_\t_
4\tword2\tword2\tNOUN\t_\t_\t1\tobj\t_\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Check flags
    assert words[0].is_multiword is False
    assert words[1].is_multiword is True
    assert words[2].is_multiword is True
    assert words[3].is_multiword is False


def test_character_index_tracking_with_mwts() -> None:
    """Test character index tracking with multi-word tokens."""
    evaluator = UDEvaluator()
    text = """# sent_id = test1
# text = pre cannot post
1\tpre\tpre\tNOUN\t_\t_\t0\troot\t_\t_
2-3\tcannot\t_\t_\t_\t_\t_\t_\t_\t_
2\tcan\tcan\tAUX\t_\t_\t1\taux\t_\t_
3\tnot\tnot\tPART\t_\t_\t1\tadvmod\t_\t_
4\tpost\tpost\tNOUN\t_\t_\t1\tobj\t_\t_

"""
    sentence = conllu.parse(text)[0]

    characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Check character positions
    assert ''.join(characters) == 'precannotpost'
    assert words[0].span == UDSpan(0, 3)  # 'pre'
    assert words[1].span == UDSpan(3, 9)  # 'cannot' (MWT)
    assert words[2].span == UDSpan(3, 9)  # 'cannot' (MWT)
    assert words[3].span == UDSpan(9, 13)  # 'post'


def test_token_span_creation_for_mwts() -> None:
    """Test token span creation for multi-word tokens."""
    evaluator = UDEvaluator()
    text = """# sent_id = test1
# text = cannot
1-2\tcannot\t_\t_\t_\t_\t_\t_\t_\t_
1\tcan\tcan\tAUX\t_\t_\t3\taux\t_\t_
2\tnot\tnot\tPART\t_\t_\t3\tadvmod\t_\t_
3\tgo\tgo\tVERB\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, _words, tokens = evaluator._convert_to_words(sentence, 'test1')

    # Should have token for MWT and token for regular word
    assert len(tokens) == 2
    assert tokens[0] == UDSpan(0, 6)  # 'cannot' MWT
    assert tokens[1] == UDSpan(6, 8)  # 'go'
