"""Tests for functional leaves validation."""

from pathlib import Path

from conllu_tools.validation.validator import ConlluValidator
from tests.factories import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_count, assert_no_errors_of_type


# Test integration and edge cases
def test_multiple_violations(tmp_path: Path) -> None:
    """Test sentence with multiple functional leaf violations."""
    tokens = [
        {
            'id': 1,
            'form': 'must',
            'lemma': 'must',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
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
            'form': 'and',
            'lemma': 'and',
            'upostag': 'CCONJ',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'cc',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'she',
            'lemma': 'she',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 5,
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
    # Should detect violations for both aux and cc
    assert_error_count(errors, 1, 'leaf-aux-cop')
    assert_error_count(errors, 1, 'leaf-cc')


def test_no_violations(tmp_path: Path) -> None:
    """Test sentence with no functional leaf violations."""
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
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'leaf-aux-cop')
    assert_no_errors_of_type(errors, 'leaf-cc')
    assert_no_errors_of_type(errors, 'leaf-mark-case')
    assert_no_errors_of_type(errors, 'leaf-fixed')
    assert_no_errors_of_type(errors, 'leaf-goeswith')
    assert_no_errors_of_type(errors, 'leaf-punct')


def test_relation_with_subtype(tmp_path: Path) -> None:
    """Test functional leaves with relation subtypes."""
    tokens = [
        {
            'id': 1,
            'form': 'in',
            'lemma': 'in',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'case:loc',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
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
        {
            'id': 3,
            'form': 'extra',
            'lemma': 'extra',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    # Should extract base deprel 'case' and detect violation
    assert_error_count(errors, 1, 'leaf-mark-case')
