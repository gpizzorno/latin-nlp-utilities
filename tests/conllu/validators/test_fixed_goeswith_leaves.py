"""Tests for functional leaves validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_count, assert_no_errors_of_type


# Test fixed as functional leaves
def test_valid_fixed_with_goeswith(tmp_path: Path) -> None:
    """Test fixed can have goeswith child (allowed)."""
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
            'form': 'or',
            'lemma': 'or',
            'upostag': 'X',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'der',
            'lemma': 'der',
            'upostag': 'X',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'leaf-fixed')


def test_valid_fixed_with_conj(tmp_path: Path) -> None:
    """Test fixed can have conj child (allowed)."""
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
            'form': 'order',
            'lemma': 'order',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'disorder',
            'lemma': 'disorder',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'conj',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'leaf-fixed')


def test_valid_fixed_with_punct(tmp_path: Path) -> None:
    """Test fixed can have punct child (allowed, e.g., hyphen)."""
    tokens = [
        {
            'id': 1,
            'form': 'up',
            'lemma': 'up',
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
            'form': '-',
            'lemma': '-',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'to',
            'lemma': 'to',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': '-',
            'lemma': '-',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 5,
            'form': 'date',
            'lemma': 'date',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'leaf-fixed')


def test_invalid_fixed_with_fixed(tmp_path: Path) -> None:
    """Test fixed cannot have fixed child (no nesting)."""
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
            'form': 'order',
            'lemma': 'order',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'to',
            'lemma': 'to',
            'upostag': 'PART',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_error_count(errors, 1, 'leaf-fixed')


def test_invalid_fixed_with_nsubj(tmp_path: Path) -> None:
    """Test fixed cannot have nsubj child (not allowed)."""
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
            'form': 'order',
            'lemma': 'order',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'he',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_error_count(errors, 1, 'leaf-fixed')


# Test goeswith as functional leaves
def test_invalid_goeswith_with_any_child(tmp_path: Path) -> None:
    """Test goeswith cannot have any children."""
    tokens = [
        {
            'id': 1,
            'form': 'some',
            'lemma': 'some',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'thing',
            'lemma': 'thing',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'extra',
            'lemma': 'extra',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'amod',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_error_count(errors, 1, 'leaf-goeswith')


def test_invalid_goeswith_with_goeswith_child(tmp_path: Path) -> None:
    """Test goeswith cannot have goeswith child."""
    tokens = [
        {
            'id': 1,
            'form': 'some',
            'lemma': 'some',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'thing',
            'lemma': 'thing',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'more',
            'lemma': 'more',
            'upostag': 'X',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_error_count(errors, 1, 'leaf-goeswith')


def test_invalid_goeswith_with_punct(tmp_path: Path) -> None:
    """Test goeswith cannot have punct child."""
    tokens = [
        {
            'id': 1,
            'form': 'some',
            'lemma': 'some',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'thing',
            'lemma': 'thing',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': '-',
            'lemma': '-',
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
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_error_count(errors, 1, 'leaf-goeswith')
