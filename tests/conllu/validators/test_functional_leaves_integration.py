"""Tests for functional leaves validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


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
    error_str = '\n'.join(errors)
    # Should detect violations for both aux and cc
    assert 'leaf-aux-cop' in error_str
    assert 'leaf-cc' in error_str


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
    error_str = '\n'.join(errors)
    assert 'leaf-mark-case' not in error_str
    assert 'leaf-aux-cop' not in error_str
    assert 'leaf-cc' not in error_str
    assert 'leaf-fixed' not in error_str
    assert 'leaf-goeswith' not in error_str
    assert 'leaf-punct' not in error_str


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
    error_str = '\n'.join(errors)
    # Should extract base deprel 'case' and detect violation
    assert 'leaf-mark-case' in error_str
