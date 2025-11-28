"""Tests for validation.py - Helper functions for token type detection."""

import conllu
import pytest

from conllu_tools.validation.helpers import (
    add_token_to_reconstruction,
    get_alt_language,
    is_empty_node,
    is_multiword_token,
    is_part_of_mwt,
    is_word,
    is_word_part_of_mwt,
    parse_empty_node_id,
)
from tests.factories import build_conllu_sentence


def test_is_word_with_positive_integer() -> None:
    """Test is_word() returns True for positive integers."""
    assert is_word(1) is True
    assert is_word(5) is True
    assert is_word(100) is True


def test_is_word_with_zero() -> None:
    """Test is_word() returns False for zero (root)."""
    assert is_word(0) is False


def test_is_word_with_negative_integer() -> None:
    """Test is_word() returns False for negative integers."""
    assert is_word(-1) is False
    assert is_word(-5) is False


def test_is_word_with_string_integer() -> None:
    """Test is_word() returns True for string representations of positive integers."""
    assert is_word('1') is True
    assert is_word('5') is True
    assert is_word('100') is True


def test_is_word_with_string_zero() -> None:
    """Test is_word() returns False for string '0'."""
    assert is_word('0') is False


def test_is_word_with_multiword_token_tuple() -> None:
    """Test is_word() returns False for multiword token tuples."""
    assert is_word((1, 2)) is False
    assert is_word((5, 7)) is False


def test_is_word_with_multiword_token_string() -> None:
    """Test is_word() returns False for multiword token strings."""
    assert is_word('1-2') is False
    assert is_word('10-15') is False


def test_is_word_with_empty_node_string() -> None:
    """Test is_word() returns False for empty node strings."""
    assert is_word('1.1') is False
    assert is_word('5.2') is False


def test_is_word_with_invalid_string() -> None:
    """Test is_word() returns False for invalid string formats."""
    assert is_word('abc') is False
    assert is_word('1a') is False
    assert is_word('') is False


def test_is_word_with_leading_zero_string() -> None:
    """Test is_word() returns False for strings with leading zeros."""
    assert is_word('01') is False
    assert is_word('005') is False


def test_is_multiword_token_with_tuple() -> None:
    """Test is_multiword_token() returns True for tuples."""
    assert is_multiword_token((1, '-', 2)) is True
    assert is_multiword_token((10, '-', 12)) is True
    assert is_multiword_token((1, '-', 10)) is True


def test_is_multiword_token_with_integer() -> None:
    """Test is_multiword_token() returns False for integers."""
    assert is_multiword_token(1) is False
    assert is_multiword_token(5) is False


def test_is_multiword_token_with_range_string() -> None:
    """Test is_multiword_token() returns True for range strings."""
    assert is_multiword_token('1-2') is True
    assert is_multiword_token('5-7') is True
    assert is_multiword_token('10-15') is True


def test_is_multiword_token_with_simple_string() -> None:
    """Test is_multiword_token() returns False for simple number strings."""
    assert is_multiword_token('1') is False
    assert is_multiword_token('5') is False


def test_is_multiword_token_with_empty_node_string() -> None:
    """Test is_multiword_token() returns False for empty node strings."""
    assert is_multiword_token('1.1') is False
    assert is_multiword_token('5.2') is False


def test_is_multiword_token_with_invalid_string() -> None:
    """Test is_multiword_token() returns False for invalid formats."""
    assert is_multiword_token('abc') is False
    assert is_multiword_token('1-') is False
    assert is_multiword_token('-2') is False


def test_is_empty_node_with_decimal_string() -> None:
    """Test is_empty_node() returns True for decimal strings."""
    assert is_empty_node('1.1') is True
    assert is_empty_node('5.2') is True
    assert is_empty_node('10.25') is True


def test_is_empty_node_with_tuple() -> None:
    """Test is_empty_node() returns True for empty node tuples."""
    assert is_empty_node((1, '.', 1)) is True
    assert is_empty_node((5, '.', 2)) is True
    assert is_empty_node((10, '.', 25)) is True


def test_is_empty_node_with_integer() -> None:
    """Test is_empty_node() returns False for integers."""
    assert is_empty_node(1) is False
    assert is_empty_node(5) is False


def test_is_empty_node_with_simple_string() -> None:
    """Test is_empty_node() returns False for simple number strings."""
    assert is_empty_node('1') is False
    assert is_empty_node('5') is False


def test_is_empty_node_with_multiword_token_string() -> None:
    """Test is_empty_node() returns False for multiword token strings."""
    assert is_empty_node('1-2') is False
    assert is_empty_node('5-7') is False


def test_is_empty_node_with_wrong_separator_tuple() -> None:
    """Test is_empty_node() returns False for tuples with wrong separator."""
    assert is_empty_node((1, '-', 2)) is False
    assert is_empty_node((1, ':', 1)) is False


def test_is_empty_node_with_invalid_string() -> None:
    """Test is_empty_node() returns False for invalid formats."""
    assert is_empty_node('abc') is False
    assert is_empty_node('1.') is False
    assert is_empty_node('.1') is False


def test_parse_empty_node_id_with_string() -> None:
    """Test parse_empty_node_id() parses decimal strings correctly."""
    assert parse_empty_node_id('1.1') == ('1', '1')
    assert parse_empty_node_id('5.2') == ('5', '2')
    assert parse_empty_node_id('10.25') == ('10', '25')


def test_parse_empty_node_id_with_tuple() -> None:
    """Test parse_empty_node_id() parses tuples correctly."""
    assert parse_empty_node_id((1, '.', 1)) == ('1', '1')
    assert parse_empty_node_id((5, '.', 2)) == ('5', '2')
    assert parse_empty_node_id((10, '.', 25)) == ('10', '25')


def test_parse_empty_node_id_with_invalid_string() -> None:
    """Test parse_empty_node_id() raises ValueError for invalid strings."""
    with pytest.raises(ValueError, match='Not a valid empty node ID'):
        parse_empty_node_id('1-2')

    with pytest.raises(ValueError, match='Not a valid empty node ID'):
        parse_empty_node_id('abc')

    with pytest.raises(ValueError, match='Not a valid empty node ID'):
        parse_empty_node_id('1')


def test_parse_empty_node_id_returns_strings() -> None:
    """Test parse_empty_node_id() always returns string tuples."""
    word_id, empty_id = parse_empty_node_id((1, '.', 1))
    assert isinstance(word_id, str)
    assert isinstance(empty_id, str)

    word_id, empty_id = parse_empty_node_id('5.2')
    assert isinstance(word_id, str)
    assert isinstance(empty_id, str)


def test_is_word_part_of_mwt_returns_true() -> None:
    """Test is_word_part_of_mwt() returns True when word is in MWT range."""
    tokens = [
        {
            'id': '1-2',
            'form': 'delcat',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 1,
            'form': 'del',
            'lemma': 'de',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'cat',
            'lemma': 'el',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
    ]
    sentence = conllu.TokenList([conllu.Token(t) for t in tokens])  # type: ignore [call-overload]
    assert is_word_part_of_mwt(1, sentence) is True
    assert is_word_part_of_mwt(2, sentence) is True


def test_is_word_part_of_mwt_returns_false() -> None:
    """Test is_word_part_of_mwt() returns False when word is not in MWT range."""
    tokens = [
        {
            'id': '1-2',
            'form': 'delcat',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 1,
            'form': 'del',
            'lemma': 'de',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'cat',
            'lemma': 'el',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'not',
            'lemma': 'not',
            'upostag': 'NEG',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
    ]
    sentence = conllu.TokenList([conllu.Token(t) for t in tokens])  # type: ignore [call-overload]
    assert is_word_part_of_mwt(3, sentence) is False


def test_is_word_part_of_mwt_with_no_mwt() -> None:
    """Test is_word_part_of_mwt() returns False when no MWT in sentence."""
    sentence_dict = {
        'sent_id': 'test',
        'text': 'word',
        'tokens': [
            {
                'id': 1,
                'form': 'word',
                'lemma': 'word',
                'upostag': 'NOUN',
                'xpostag': '_',
                'feats': '_',
                'head': 0,
                'deprel': 'root',
                'deps': '_',
                'misc': '_',
            },
        ],
    }
    text = build_conllu_sentence(sentence_dict)
    sentence = conllu.parse(text)[0]

    assert is_word_part_of_mwt(1, sentence) is False


def test_is_part_of_mwt_returns_true() -> None:
    """Test is_part_of_mwt() returns True when token is in range."""
    mwt_ranges = [(1, 2), (5, 7)]

    assert is_part_of_mwt(1, mwt_ranges) is True
    assert is_part_of_mwt(2, mwt_ranges) is True
    assert is_part_of_mwt(5, mwt_ranges) is True
    assert is_part_of_mwt(6, mwt_ranges) is True
    assert is_part_of_mwt(7, mwt_ranges) is True


def test_is_part_of_mwt_returns_false() -> None:
    """Test is_part_of_mwt() returns False when token is not in range."""
    mwt_ranges = [(1, 2), (5, 7)]

    assert is_part_of_mwt(3, mwt_ranges) is False
    assert is_part_of_mwt(4, mwt_ranges) is False
    assert is_part_of_mwt(8, mwt_ranges) is False


def test_is_part_of_mwt_with_empty_ranges() -> None:
    """Test is_part_of_mwt() returns False with empty ranges list."""
    assert is_part_of_mwt(1, []) is False
    assert is_part_of_mwt(5, []) is False


def test_is_part_of_mwt_with_non_integer_id() -> None:
    """Test is_part_of_mwt() returns False for non-integer token IDs."""
    mwt_ranges = [(1, 2)]

    assert is_part_of_mwt('1', mwt_ranges) is False
    assert is_part_of_mwt((1, 2), mwt_ranges) is False
    assert is_part_of_mwt('1.1', mwt_ranges) is False


def test_is_part_of_mwt_with_boundary_values() -> None:
    """Test is_part_of_mwt() handles boundary values correctly."""
    mwt_ranges = [(10, 15)]

    assert is_part_of_mwt(9, mwt_ranges) is False
    assert is_part_of_mwt(10, mwt_ranges) is True
    assert is_part_of_mwt(15, mwt_ranges) is True
    assert is_part_of_mwt(16, mwt_ranges) is False


def test_is_part_of_mwt_with_single_token_range() -> None:
    """Test is_part_of_mwt() works with single-token ranges."""
    mwt_ranges = [(5, 5)]

    assert is_part_of_mwt(4, mwt_ranges) is False
    assert is_part_of_mwt(5, mwt_ranges) is True
    assert is_part_of_mwt(6, mwt_ranges) is False


def test_add_token_to_reconstruction_basic() -> None:
    """Test add_token_to_reconstruction() adds form and space."""
    token = conllu.Token(
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': None,
            'head': 0,
            'deprel': 'root',
            'deps': None,
            'misc': None,
        },
    )
    parts: list[str] = []
    add_token_to_reconstruction(token, parts)
    assert parts == ['word', ' ']


def test_add_token_to_reconstruction_with_spaceafter_no() -> None:
    """Test add_token_to_reconstruction() handles SpaceAfter=No."""
    token = conllu.Token(
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': None,
            'head': 0,
            'deprel': 'root',
            'deps': None,
            'misc': {'SpaceAfter': 'No'},
        },
    )
    parts: list[str] = []
    add_token_to_reconstruction(token, parts)
    assert parts == ['word']


def test_add_token_to_reconstruction_with_none_misc() -> None:
    """Test add_token_to_reconstruction() handles None MISC."""
    token = conllu.Token(
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': None,
            'head': 0,
            'deprel': 'root',
            'deps': None,
            'misc': None,
        },
    )
    parts: list[str] = []
    add_token_to_reconstruction(token, parts)
    assert parts == ['word', ' ']


def test_add_token_to_reconstruction_with_other_misc_values() -> None:
    """Test add_token_to_reconstruction() ignores other MISC values."""
    token = conllu.Token(
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': None,
            'head': 0,
            'deprel': 'root',
            'deps': None,
            'misc': {'SpaceAfter': 'Yes', 'Other': 'Value'},
        },
    )
    parts: list[str] = []
    add_token_to_reconstruction(token, parts)
    assert parts == ['word', ' ']


def test_add_token_to_reconstruction_multiple_tokens() -> None:
    """Test add_token_to_reconstruction() with multiple tokens."""
    tokens = [
        conllu.Token(
            {
                'id': 1,
                'form': 'word1',
                'lemma': 'word1',
                'upostag': 'NOUN',
                'xpostag': '_',
                'feats': None,
                'head': 0,
                'deprel': 'root',
                'deps': None,
                'misc': None,
            },
        ),
        conllu.Token(
            {
                'id': 2,
                'form': 'word2',
                'lemma': 'word2',
                'upostag': 'NOUN',
                'xpostag': '_',
                'feats': None,
                'head': 1,
                'deprel': 'obj',
                'deps': None,
                'misc': {'SpaceAfter': 'No'},
            },
        ),
        conllu.Token(
            {
                'id': 3,
                'form': '.',
                'lemma': '.',
                'upostag': 'PUNCT',
                'xpostag': '_',
                'feats': None,
                'head': 1,
                'deprel': 'punct',
                'deps': None,
                'misc': None,
            },
        ),
    ]

    parts: list[str] = []
    for token in tokens:
        add_token_to_reconstruction(token, parts)

    assert parts == ['word1', ' ', 'word2', '.', ' ']


def test_get_alt_language_with_lang_attribute() -> None:
    """Test get_alt_language() extracts Lang attribute."""
    token = conllu.Token(
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': None,
            'head': 0,
            'deprel': 'root',
            'deps': None,
            'misc': {'Lang': 'la'},
        },
    )

    assert get_alt_language(token) == 'la'


def test_get_alt_language_with_none_misc() -> None:
    """Test get_alt_language() returns None when MISC is None."""
    token = conllu.Token(
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': None,
            'head': 0,
            'deprel': 'root',
            'deps': None,
            'misc': None,
        },
    )

    assert get_alt_language(token) is None


def test_get_alt_language_without_lang_attribute() -> None:
    """Test get_alt_language() returns None when Lang not in MISC."""
    token = conllu.Token(
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': None,
            'head': 0,
            'deprel': 'root',
            'deps': None,
            'misc': {'SpaceAfter': 'No'},
        },
    )

    assert get_alt_language(token) is None


def test_get_alt_language_with_empty_lang_value() -> None:
    """Test get_alt_language() handles empty Lang value."""
    token = conllu.Token(
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': None,
            'head': 0,
            'deprel': 'root',
            'deps': None,
            'misc': {'Lang': ''},
        },
    )

    result = get_alt_language(token)
    # Empty string is falsy, so returns None
    assert result is None


def test_get_alt_language_with_different_language_codes() -> None:
    """Test get_alt_language() works with various language codes."""
    for lang_code in ['en', 'la', 'grc', 'de', 'fr', 'es']:
        token = conllu.Token(
            {
                'id': 1,
                'form': 'word',
                'lemma': 'word',
                'upostag': 'NOUN',
                'xpostag': '_',
                'feats': None,
                'head': 0,
                'deprel': 'root',
                'deps': None,
                'misc': {'Lang': lang_code},
            },
        )

        assert get_alt_language(token) == lang_code


def test_get_alt_language_returns_string() -> None:
    """Test get_alt_language() converts value to string."""
    token = conllu.Token(
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': None,
            'head': 0,
            'deprel': 'root',
            'deps': None,
            'misc': {'Lang': 'la'},
        },
    )

    result = get_alt_language(token)
    assert isinstance(result, str)


@pytest.mark.parametrize(
    ('token_id', 'expected'),
    [
        (1, True),
        (0, False),
        (-1, False),
        ('1', True),
        ('0', False),
        ((1, 2), False),
        ('1-2', False),
        ('1.1', False),
        ((1, '.', 1), False),
    ],
)
def test_is_word_parametrized(token_id: int | tuple[int, int] | str, expected: bool) -> None:  # noqa: FBT001
    """Test is_word() with various inputs (parametrized)."""
    assert is_word(token_id) == expected


@pytest.mark.parametrize(
    ('token_id', 'expected'),
    [
        ((1, '-', 2), True),
        ('1-2', True),
        (1, False),
        ('1', False),
        ('1.1', False),
        ((1, '.', 1), False),
    ],
)
def test_is_multiword_token_parametrized(token_id: int | tuple[int, str, int] | str, expected: bool) -> None:  # noqa: FBT001
    """Test is_multiword_token() with various inputs (parametrized)."""
    assert is_multiword_token(token_id) == expected


@pytest.mark.parametrize(
    ('token_id', 'expected'),
    [
        ('1.1', True),
        ((1, '.', 1), True),
        (1, False),
        ('1', False),
        ('1-2', False),
        ((1, 2), False),
    ],
)
def test_is_empty_node_parametrized(token_id: int | tuple[int, str, int] | str, expected: bool) -> None:  # noqa: FBT001
    """Test is_empty_node() with various inputs (parametrized)."""
    assert is_empty_node(token_id) == expected
