"""Test left-to-right relation validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


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
    conj_errors = [e for e in errors if 'right-to-left-conj' in e]
    assert len(conj_errors) == 0


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
    conj_errors = [e for e in errors if 'right-to-left-conj' in e]
    assert len(conj_errors) == 1


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
    fixed_errors = [e for e in errors if 'right-to-left-fixed' in e]
    assert len(fixed_errors) == 0


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
    fixed_errors = [e for e in errors if 'right-to-left-fixed' in e]
    assert len(fixed_errors) == 1


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
    goeswith_errors = [e for e in errors if 'right-to-left-goeswith' in e]
    assert len(goeswith_errors) == 0


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
    goeswith_errors = [e for e in errors if 'right-to-left-goeswith' in e]
    assert len(goeswith_errors) == 1


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
    flat_errors = [e for e in errors if 'right-to-left-flat' in e]
    assert len(flat_errors) == 0


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
    appos_errors = [e for e in errors if 'right-to-left-appos' in e]
    assert len(appos_errors) == 0


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
    conj_errors = [e for e in errors if 'right-to-left-conj' in e]
    assert len(conj_errors) == 1
