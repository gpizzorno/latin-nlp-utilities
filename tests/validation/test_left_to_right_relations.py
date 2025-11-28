"""Test left-to-right relation validation."""

from pathlib import Path

from conllu_tools.validation.validator import ConlluValidator
from tests.factories import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_count, assert_no_errors_of_type


def test_valid_conj_left_to_right(tmp_path: Path) -> None:
    """Test that conj going left-to-right is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'cats',
            'lemma': 'cats',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'and',
            'lemma': 'and',
            'upostag': 'CCONJ',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'cc',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'dogs',
            'lemma': 'dogs',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'conj',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='cats and dogs')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'right-to-left-conj')


def test_invalid_conj_right_to_left(tmp_path: Path) -> None:
    """Test that conj going right-to-left is invalid."""
    tokens = [
        {
            'id': 1,
            'form': 'cats',
            'lemma': 'cats',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'conj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'and',
            'lemma': 'and',
            'upostag': 'CCONJ',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'cc',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'dogs',
            'lemma': 'dogs',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='cats and dogs')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_error_count(errors, 1, 'right-to-left-conj')


def test_valid_fixed_left_to_right(tmp_path: Path) -> None:
    """Test that fixed going left-to-right is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'in',
            'lemma': 'in',
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
            'form': 'fact',
            'lemma': 'fact',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='in fact')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'right-to-left-fixed')


def test_invalid_fixed_right_to_left(tmp_path: Path) -> None:
    """Test that fixed going right-to-left is invalid."""
    tokens = [
        {
            'id': 1,
            'form': 'in',
            'lemma': 'in',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'fact',
            'lemma': 'fact',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='in fact')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_error_count(errors, 1, 'right-to-left-fixed')


def test_valid_goeswith_left_to_right(tmp_path: Path) -> None:
    """Test that goeswith going left-to-right is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'qui',
            'lemma': 'qui',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'ckly',
            'lemma': 'ckly',
            'upostag': 'X',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='qui ckly')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'right-to-left-goeswith')


def test_invalid_goeswith_right_to_left(tmp_path: Path) -> None:
    """Test that goeswith going right-to-left is invalid."""
    tokens = [
        {
            'id': 1,
            'form': 'qui',
            'lemma': 'qui',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'ckly',
            'lemma': 'ckly',
            'upostag': 'X',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='qui ckly')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_error_count(errors, 1, 'right-to-left-goeswith')


def test_valid_flat_left_to_right(tmp_path: Path) -> None:
    """Test that flat going left-to-right is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'New',
            'lemma': 'New',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'York',
            'lemma': 'York',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'flat',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='New York')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'right-to-left-flat')


def test_valid_appos_left_to_right(tmp_path: Path) -> None:
    """Test that appos going left-to-right is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'Obama',
            'lemma': 'Obama',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'president',
            'lemma': 'president',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'appos',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='Obama president')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'right-to-left-appos')


def test_relation_with_subtype(tmp_path: Path) -> None:
    """Test that validation works with relation subtypes."""
    tokens = [
        {
            'id': 1,
            'form': 'cats',
            'lemma': 'cats',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'conj:and',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'and',
            'lemma': 'and',
            'upostag': 'CCONJ',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'cc',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'dogs',
            'lemma': 'dogs',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='cats and dogs')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    # Should have right-to-left-conj error (base relation is conj)
    assert_error_count(errors, 1, 'right-to-left-conj')
