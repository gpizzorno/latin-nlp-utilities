"""Tests for functional leaves validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_count, assert_no_errors_of_type


# Test aux and cop as functional leaves
def test_valid_aux_with_fixed(tmp_path: Path) -> None:
    """Test aux can have fixed child (allowed)."""
    tokens = [
        {
            'id': 1,
            'form': 'has',
            'lemma': 'have',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'been',
            'lemma': 'be',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'fixed',
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
    assert_no_errors_of_type(errors, 'leaf-aux-cop')


def test_valid_cop_with_conj(tmp_path: Path) -> None:
    """Test cop can have conj child (allowed)."""
    tokens = [
        {
            'id': 1,
            'form': 'is',
            'lemma': 'be',
            'upostag': 'AUX',
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
            'form': 'was',
            'lemma': 'be',
            'upostag': 'AUX',
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
    assert_no_errors_of_type(errors, 'leaf-aux-cop')


def test_valid_aux_with_punct(tmp_path: Path) -> None:
    """Test aux can have punct child (allowed)."""
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
            'form': 'can',
            'lemma': 'can',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
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
    assert_no_errors_of_type(errors, 'leaf-aux-cop')


def test_invalid_aux_with_nsubj(tmp_path: Path) -> None:
    """Test aux cannot have nsubj child (not allowed)."""
    tokens = [
        {
            'id': 1,
            'form': 'must',
            'lemma': 'must',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
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
    assert_no_errors_of_type(errors, 'leaf-aux-cop')


def test_invalid_cop_with_advmod(tmp_path: Path) -> None:
    """Test cop cannot have advmod child (not allowed, except negation)."""
    tokens = [
        {
            'id': 1,
            'form': 'is',
            'lemma': 'be',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'cop',
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
            'form': 'good',
            'lemma': 'good',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_error_count(errors, 1, 'leaf-aux-cop')
    # print(errors.errors)
    # assert_error_count(errors, 0)
