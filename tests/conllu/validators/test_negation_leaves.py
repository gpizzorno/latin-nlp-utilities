"""Tests for functional leaves validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


# Test negation exception for functional words
def test_valid_negation_on_aux(tmp_path: Path) -> None:
    """Test aux can have negation advmod (Polarity=Neg)."""
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
            'form': 'not',
            'lemma': 'not',
            'upostag': 'PART',
            'xpostag': '_',
            'feats': 'Polarity=Neg',
            'head': 1,
            'deprel': 'advmod',
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
    error_str = '\n'.join(errors)
    assert 'leaf-aux-cop' not in error_str


def test_valid_negation_on_mark(tmp_path: Path) -> None:
    """Test mark can have negation advmod (Polarity=Neg)."""
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
            'form': 'not',
            'lemma': 'not',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': 'Polarity=Neg',
            'head': 1,
            'deprel': 'advmod',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    assert 'leaf-mark-case' not in error_str


def test_valid_negation_on_case(tmp_path: Path) -> None:
    """Test case can have negation advmod (already allowed via advmod)."""
    tokens = [
        {
            'id': 1,
            'form': 'without',
            'lemma': 'without',
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
            'form': 'not',
            'lemma': 'not',
            'upostag': 'PART',
            'xpostag': '_',
            'feats': 'Polarity=Neg',
            'head': 1,
            'deprel': 'advmod',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    assert 'leaf-mark-case' not in error_str


def test_negation_not_allowed_on_punct(tmp_path: Path) -> None:
    """Test negation exception does not apply to punct."""
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
            'form': 'not',
            'lemma': 'not',
            'upostag': 'PART',
            'xpostag': '_',
            'feats': 'Polarity=Neg',
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
    # Punct cannot have advmod children, even negation
    assert 'leaf-punct' in error_str
