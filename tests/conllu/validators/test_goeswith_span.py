"""Test goeswith span validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


def test_valid_goeswith_contiguous(tmp_path: Path) -> None:
    """Test valid contiguous goeswith chain."""
    tokens = [
        {
            'id': 1,
            'form': 'so',
            'lemma': '_',
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
            'form': 'me',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'thing',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='some text')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    goeswith_errors = [e for e in errors if 'goeswith-gap' in e or 'goeswith-nospace' in e]
    assert len(goeswith_errors) == 0


def test_invalid_goeswith_gap(tmp_path: Path) -> None:
    """Test goeswith with gap in the chain."""
    tokens = [
        {
            'id': 1,
            'form': 'so',
            'lemma': '_',
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
            'form': 'me',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'other',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'thing',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='some text')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    gap_errors = [e for e in errors if 'goeswith-gap' in e]
    assert len(gap_errors) == 1


def test_invalid_goeswith_no_space(tmp_path: Path) -> None:
    """Test goeswith without whitespace separation."""
    tokens = [
        {
            'id': 1,
            'form': 'so',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': 'SpaceAfter=No',
        },
        {
            'id': 2,
            'form': 'me',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'thing',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='something')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    nospace_errors = [e for e in errors if 'goeswith-nospace' in e]
    assert len(nospace_errors) == 1


def test_valid_goeswith_with_space(tmp_path: Path) -> None:
    """Test goeswith with proper whitespace between parts."""
    tokens = [
        {
            'id': 1,
            'form': 'so',
            'lemma': '_',
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
            'form': 'me',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'thing',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': 'SpaceAfter=No',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='some thing')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    nospace_errors = [e for e in errors if 'goeswith-nospace' in e]
    assert len(nospace_errors) == 0


def test_goeswith_middle_node_no_space(tmp_path: Path) -> None:
    """Test goeswith with missing space in middle of chain."""
    tokens = [
        {
            'id': 1,
            'form': 'so',
            'lemma': '_',
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
            'form': 'me',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': 'SpaceAfter=No',
        },
        {
            'id': 3,
            'form': 'thing',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='something')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    nospace_errors = [e for e in errors if 'goeswith-nospace' in e]
    assert len(nospace_errors) == 1


def test_goeswith_with_subtype(tmp_path: Path) -> None:
    """Test goeswith with subtype in relation."""
    tokens = [
        {
            'id': 1,
            'form': 'so',
            'lemma': '_',
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
            'form': 'me',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith:foreign',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'thing',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='some text')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    gap_errors = [e for e in errors if 'goeswith-gap' in e]
    assert len(gap_errors) == 0
