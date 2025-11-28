"""Character Array Conversion Tests."""

from __future__ import annotations

import conllu
from conllu_tools.evaluation.base import UDSpan
from conllu_tools.evaluation.evaluator import ConlluEvaluator


def test_convert_to_words_with_simple_sentence() -> None:
    """Test _convert_to_words with a simple sentence."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    characters, words, tokens = evaluator._convert_to_words(sentence, 'test1')

    # Check characters
    assert ''.join(characters) == 'Thecat'

    # Check words
    assert len(words) == 2
    assert words[0].token['form'] == 'The'
    assert words[1].token['form'] == 'cat'

    # Check tokens
    assert len(tokens) == 2
    assert tokens[0] == UDSpan(0, 3)
    assert tokens[1] == UDSpan(3, 6)


def test_convert_to_words_with_multi_word_tokens() -> None:
    """Test _convert_to_words with multi-word tokens."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = cannot go
1-2\tcannot\t_\t_\t_\t_\t_\t_\t_\t_
1\tcan\tcan\tAUX\t_\t_\t3\taux\t_\t_
2\tnot\tnot\tPART\t_\t_\t3\tadvmod\t_\t_
3\tgo\tgo\tVERB\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Check characters include MWT
    assert ''.join(characters) == 'cannotgo'

    # Check words
    assert len(words) == 3
    assert words[0].token['form'] == 'can'
    assert words[1].token['form'] == 'not'
    assert words[2].token['form'] == 'go'

    # Check multiword flags
    assert words[0].is_multiword is True
    assert words[1].is_multiword is True
    assert words[2].is_multiword is False

    # Check spans - first two share MWT span
    assert words[0].span == UDSpan(0, 6)
    assert words[1].span == UDSpan(0, 6)
    assert words[2].span == UDSpan(6, 8)


def test_convert_to_words_whitespace_removal() -> None:
    """Test _convert_to_words removes Unicode whitespace from forms."""
    evaluator = ConlluEvaluator()
    # Create sentence with Unicode whitespace (U+00A0 non-breaking space)
    text = """# sent_id = test1
# text = word1 word2
1\tword\u00a01\tword1\tNOUN\t_\t_\t0\troot\t_\t_
2\tword2\tword2\tVERB\t_\t_\t1\tobj\t_\t_

"""
    sentence = conllu.parse(text)[0]

    characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Whitespace should be removed
    assert ''.join(characters) == 'word1word2'
    assert words[0].span == UDSpan(0, 5)


def test_convert_to_words_character_position_tracking() -> None:
    """Test _convert_to_words correctly tracks character positions."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = A longer sentence
1\tA\ta\tDET\t_\t_\t3\tdet\t_\t_
2\tlonger\tlong\tADJ\t_\t_\t3\tamod\t_\t_
3\tsentence\tsentence\tNOUN\t_\t_\t0\troot\t_\t_

"""
    sentence = conllu.parse(text)[0]

    characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Check character array
    assert ''.join(characters) == 'Alongersentence'

    # Check word spans match character positions
    assert words[0].span == UDSpan(0, 1)  # 'A'
    assert words[1].span == UDSpan(1, 7)  # 'longer'
    assert words[2].span == UDSpan(7, 15)  # 'sentence'


def test_convert_to_words_token_span_creation() -> None:
    """Test _convert_to_words creates correct token spans."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = word1 word2
1\tword1\tword1\tNOUN\t_\t_\t0\troot\t_\t_
2\tword2\tword2\tVERB\t_\t_\t1\tobj\t_\t_

"""
    sentence = conllu.parse(text)[0]

    _characters, words, tokens = evaluator._convert_to_words(sentence, 'test1')

    # Tokens should match word spans for non-MWT
    assert len(tokens) == 2
    assert tokens[0] == words[0].span
    assert tokens[1] == words[1].span


def test_convert_to_words_with_unicode_characters() -> None:
    """Test _convert_to_words handles Unicode characters."""
    evaluator = ConlluEvaluator()
    text = """# sent_id = test1
# text = café naïve
1\tcafé\tcafé\tNOUN\t_\t_\t0\troot\t_\t_
2\tnaïve\tnaïve\tADJ\t_\t_\t1\tamod\t_\t_

"""
    sentence = conllu.parse(text)[0]

    characters, words, _tokens = evaluator._convert_to_words(sentence, 'test1')

    # Check Unicode characters preserved
    assert ''.join(characters) == 'cafénaïve'
    assert words[0].token['form'] == 'café'
    assert words[1].token['form'] == 'naïve'
