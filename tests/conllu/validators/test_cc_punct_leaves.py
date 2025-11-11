"""Tests for functional leaves validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


# Test cc as functional leaves
def test_valid_cc_with_fixed(tmp_path: Path) -> None:
    """Test cc can have fixed child (allowed)."""
    tokens = [
        {
            'id': 1,
            'form': 'both',
            'lemma': 'both',
            'upostag': 'CCONJ',
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
            'head': 1,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    assert 'leaf-cc' not in error_str


def test_valid_cc_with_conj(tmp_path: Path) -> None:
    """Test cc can have conj child (allowed, e.g., 'and/or')."""
    tokens = [
        {
            'id': 1,
            'form': 'and',
            'lemma': 'and',
            'upostag': 'CCONJ',
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
            'head': 1,
            'deprel': 'conj',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    assert 'leaf-cc' not in error_str


def test_valid_cc_with_punct(tmp_path: Path) -> None:
    """Test cc can have punct child (allowed)."""
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
            'form': 'and',
            'lemma': 'and',
            'upostag': 'CCONJ',
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
    error_str = '\n'.join(errors)
    assert 'leaf-cc' not in error_str


def test_invalid_cc_with_nsubj(tmp_path: Path) -> None:
    """Test cc cannot have nsubj child (not allowed)."""
    tokens = [
        {
            'id': 1,
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
    error_str = '\n'.join(errors)
    assert 'leaf-cc' in error_str


def test_invalid_cc_with_cc(tmp_path: Path) -> None:
    """Test cc cannot have another cc child (not allowed)."""
    tokens = [
        {
            'id': 1,
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
            'id': 2,
            'form': 'and',
            'lemma': 'and',
            'upostag': 'CCONJ',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'cc',
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
    error_str = '\n'.join(errors)
    assert 'leaf-cc' in error_str


# Test punct as functional leaves
def test_valid_punct_with_punct_child(tmp_path: Path) -> None:
    """Test punct can have punct child (e.g., quoted exclamation)."""
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
            'form': '!',
            'lemma': '!',
            'upostag': 'PUNCT',
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
    error_str = '\n'.join(errors)
    assert 'leaf-punct' not in error_str


def test_invalid_punct_with_nsubj(tmp_path: Path) -> None:
    """Test punct cannot have nsubj child."""
    tokens = [
        {
            'id': 1,
            'form': ',',
            'lemma': ',',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
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
    error_str = '\n'.join(errors)
    assert 'leaf-punct' in error_str


def test_invalid_punct_with_advmod(tmp_path: Path) -> None:
    """Test punct cannot have advmod child."""
    tokens = [
        {
            'id': 1,
            'form': ',',
            'lemma': ',',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'really',
            'lemma': 'really',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'advmod',
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
    error_str = '\n'.join(errors)
    assert 'leaf-punct' in error_str
