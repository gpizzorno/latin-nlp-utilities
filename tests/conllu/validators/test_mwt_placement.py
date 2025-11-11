"""Test multiword token placement validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


def test_mwt_before_words(tmp_path: Path) -> None:
    """Test that MWT before words passes."""
    tokens = [
        {
            'id': '1-2',
            'form': 'delcat',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 1,
            'form': 'del',
            'lemma': 'de',
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
            'form': 'cat',
            'lemma': 'el',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_file(test_file)
    assert not any('mwt-not-before-words' in e for e in errors)


def test_mwt_after_words(tmp_path: Path) -> None:
    """Test that MWT after words is detected."""
    tokens = [
        {
            'id': 1,
            'form': 'del',
            'lemma': 'de',
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
            'form': 'cat',
            'lemma': 'el',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': '1-2',
            'form': 'delcat',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_file(test_file)
    assert any('mwt-not-before-words' in e for e in errors)
    assert any('1-2' in e for e in errors)


def test_mwt_between_words(tmp_path: Path) -> None:
    """Test that MWT between its words is detected."""
    tokens = [
        {
            'id': 1,
            'form': 'del',
            'lemma': 'de',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': '1-2',
            'form': 'delcat',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'cat',
            'lemma': 'el',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_file(test_file)
    assert any('mwt-not-before-words' in e for e in errors)
