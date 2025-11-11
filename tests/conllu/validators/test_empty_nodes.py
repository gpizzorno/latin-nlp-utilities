"""Tests for empty node validation."""

from pathlib import Path

import pytest

from nlp_utilities.conllu.validators.helpers.node_helpers import (
    is_empty_node,
    is_multiword_token,
    is_word,
    parse_empty_node_id,
)
from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


# Test helper functions for detecting node types
@pytest.mark.parametrize(
    ('token_id', 'expected'),
    [
        (1, True),
        (10, True),
        ((1, 2), False),
        ('1', True),
        ('10', True),
        ('1-2', False),
        ('1.1', False),
        ('0', False),  # 0 is not a valid word ID
    ],
)
def test_is_word(token_id: int | str, expected: bool) -> None:  # noqa: FBT001
    """Test is_word function."""
    assert is_word(token_id) == expected


@pytest.mark.parametrize(
    ('token_id', 'expected'),
    [
        ((1, 2), True),
        ((2, 3), True),
        (1, False),
        ('1-2', True),
        ('2-3', True),
        ('1', False),
        ('1.1', False),
    ],
)
def test_is_multiword_token(token_id: int | str, expected: bool) -> None:  # noqa: FBT001
    """Test is_multiword_token function."""
    assert is_multiword_token(token_id) == expected


@pytest.mark.parametrize(
    ('token_id', 'expected'),
    [
        ('1.1', True),
        ('2.3', True),
        ('10.5', True),
        (1, False),
        ((1, 2), False),
        ('1-2', False),
        ('1', False),
        ('0.1', True),  # 0.1 is technically valid format
    ],
)
def test_is_empty_node(token_id: int | str, expected: bool) -> None:  # noqa: FBT001
    """Test is_empty_node function."""
    assert is_empty_node(token_id) == expected


# Test parsing of empty node IDs
def test_parse_valid_empty_node_id() -> None:
    """Test parsing a valid empty node ID."""
    word_id, empty_id = parse_empty_node_id('3.1')
    assert word_id == '3'
    assert empty_id == '1'


def test_parse_valid_empty_node_id_multi_digit() -> None:
    """Test parsing with multi-digit IDs."""
    word_id, empty_id = parse_empty_node_id('10.25')
    assert word_id == '10'
    assert empty_id == '25'


def test_parse_invalid_empty_node_id() -> None:
    """Test that invalid IDs raise ValueError."""
    with pytest.raises(ValueError, match='Not a valid empty node ID'):
        parse_empty_node_id('1-2')

    with pytest.raises(ValueError, match='Not a valid empty node ID'):
        parse_empty_node_id('1')

    with pytest.raises(ValueError, match='Not a valid empty node ID'):
        parse_empty_node_id('abc')


# Test empty node validation in CoNLL-U files
def test_empty_node_with_valid_format(tmp_path: Path) -> None:
    """Test that a properly formatted empty node passes validation."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'will',
            'lemma': 'will',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': '2.1',
            'form': 'come',
            'lemma': 'come',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'come',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    # Should have no critical errors about empty node format
    error_text = '\n'.join(errors)
    assert 'invalid-empty-node-id' not in error_text


def test_empty_node_with_head_value(tmp_path: Path) -> None:
    """Test that empty node with HEAD value generates error."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'will',
            'lemma': 'will',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': '2.1',
            'form': 'come',
            'lemma': 'come',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'xcomp',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'come',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    # Should have error about empty node HEAD
    error_text = '\n'.join(errors)
    assert 'empty-node-head' in error_text or 'must have _ in HEAD' in error_text


def test_empty_node_with_deprel_value(tmp_path: Path) -> None:
    """Test that empty node with DEPREL value generates error."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'will',
            'lemma': 'will',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': '2.1',
            'form': 'come',
            'lemma': 'come',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': 'xcomp',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'come',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    # Should have error about empty node DEPREL
    error_text = '\n'.join(errors)
    assert 'empty-node-deprel' in error_text or 'must have _ in DEPREL' in error_text


def test_empty_node_with_upos_value(tmp_path: Path) -> None:
    """Test that empty node with UPOS value generates warning."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'will',
            'lemma': 'will',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': '2.1',
            'form': 'come',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'come',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    # Should have warning about empty node UPOS
    error_text = '\n'.join(errors)
    assert 'empty-node-upos' in error_text or 'should have _ in UPOS' in error_text


def test_empty_nodes_not_counted_as_roots(tmp_path: Path) -> None:
    """Test that empty nodes are not counted when checking for roots."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': '1.1',
            'form': 'will',
            'lemma': 'will',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'came',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    # Should not complain about multiple roots
    error_text = '\n'.join(errors)
    assert 'multiple-roots' not in error_text
    assert 'no-root' not in error_text
