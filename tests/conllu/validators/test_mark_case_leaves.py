"""Tests for functional leaves validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory
from tests.helpers.assertion import assert_no_errors_of_type


# Test mark and case as functional leaves
def test_valid_mark_with_advmod(tmp_path: Path) -> None:
    """Test mark can have advmod child (allowed)."""
    tokens = [
        {
            'id': 1,
            'form': 'just',
            'lemma': 'just',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'advmod',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'before',
            'lemma': 'before',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'mark',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'going',
            'lemma': 'go',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'leaf-mark-case')


def test_valid_case_with_obl(tmp_path: Path) -> None:
    """Test case can have obl child (allowed)."""
    tokens = [
        {
            'id': 1,
            'form': 'because',
            'lemma': 'because',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'of',
            'lemma': 'of',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'obl',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'him',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'leaf-mark-case')


def test_valid_mark_with_fixed(tmp_path: Path) -> None:
    """Test mark can have fixed child (allowed)."""
    tokens = [
        {
            'id': 1,
            'form': 'in',
            'lemma': 'in',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'mark',
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
            'head': 1,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'go',
            'lemma': 'go',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'leaf-mark-case')


def test_valid_mark_with_conj(tmp_path: Path) -> None:
    """Test mark can have conj child (allowed)."""
    tokens = [
        {
            'id': 1,
            'form': 'if',
            'lemma': 'if',
            'upostag': 'SCONJ',
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
            'form': 'when',
            'lemma': 'when',
            'upostag': 'SCONJ',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'conj',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'leaf-mark-case')


def test_valid_mark_with_punct(tmp_path: Path) -> None:
    """Test mark can have punct child (allowed)."""
    tokens = [
        {
            'id': 1,
            'form': '"',
            'lemma': '"',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'if',
            'lemma': 'if',
            'upostag': 'SCONJ',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'mark',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'go',
            'lemma': 'go',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'leaf-mark-case')


def test_invalid_mark_with_nsubj(tmp_path: Path) -> None:
    """Test mark cannot have nsubj child (not allowed)."""
    tokens = [
        {
            'id': 1,
            'form': 'before',
            'lemma': 'before',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'mark',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'he',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'goes',
            'lemma': 'go',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'leaf-mark-case')


def test_invalid_case_with_obj(tmp_path: Path) -> None:
    """Test case cannot have obj child (not allowed)."""
    tokens = [
        {
            'id': 1,
            'form': 'with',
            'lemma': 'with',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'something',
            'lemma': 'something',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'obj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'him',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'leaf-mark-case')
