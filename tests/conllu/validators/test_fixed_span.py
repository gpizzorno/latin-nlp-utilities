"""Test fixed span validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


def test_valid_fixed_contiguous(tmp_path: Path) -> None:
    """Test valid contiguous fixed expression."""
    tokens = [
        {
            'id': 1,
            'form': 'in',
            'lemma': '_',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'order',
            'lemma': '_',
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
            'lemma': '_',
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
            'lemma': '_',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='in order to')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    fixed_errors = [e for e in errors if 'fixed-gap' in e]
    assert len(fixed_errors) == 0


def test_valid_fixed_with_punct(tmp_path: Path) -> None:
    """Test fixed expression with intervening punctuation (allowed)."""
    tokens = [
        {
            'id': 1,
            'form': 'in',
            'lemma': '_',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'order',
            'lemma': '_',
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
            'form': ',',
            'lemma': '_',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'to',
            'lemma': '_',
            'upostag': 'PART',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 5,
            'form': 'go',
            'lemma': '_',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='in order , to')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    fixed_errors = [e for e in errors if 'fixed-gap' in e]
    assert len(fixed_errors) == 0


def test_invalid_fixed_gap(tmp_path: Path) -> None:
    """Test fixed expression with non-punctuation gap."""
    tokens = [
        {
            'id': 1,
            'form': 'in',
            'lemma': '_',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'order',
            'lemma': '_',
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
            'form': 'other',
            'lemma': '_',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'amod',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'to',
            'lemma': '_',
            'upostag': 'PART',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 5,
            'form': 'go',
            'lemma': '_',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='in some order to')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    fixed_errors = [e for e in errors if 'fixed-gap' in e]
    assert len(fixed_errors) == 1


def test_fixed_with_subtype(tmp_path: Path) -> None:
    """Test fixed with subtype in relation."""
    tokens = [
        {
            'id': 1,
            'form': 'in',
            'lemma': '_',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'order',
            'lemma': '_',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'fixed:expr',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'to',
            'lemma': '_',
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
            'lemma': '_',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='in order to')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    fixed_errors = [e for e in errors if 'fixed-gap' in e]
    assert len(fixed_errors) == 0


def test_fixed_two_word_expression(tmp_path: Path) -> None:
    """Test simple two-word fixed expression."""
    tokens = [
        {
            'id': 1,
            'form': 'because',
            'lemma': '_',
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
            'lemma': '_',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'him',
            'lemma': '_',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='because of him')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    fixed_errors = [e for e in errors if 'fixed-gap' in e]
    assert len(fixed_errors) == 0
