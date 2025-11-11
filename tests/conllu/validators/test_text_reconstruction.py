"""Tests for text reconstruction and metadata validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


def test_text_reconstruction_basic(tmp_path: Path) -> None:
    """Test basic text reconstruction with spaces."""
    tokens = [
        {
            'id': 1,
            'form': 'John',
            'lemma': 'John',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'saw',
            'lemma': 'see',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'Mary',
            'lemma': 'Mary',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'obj',
            'deps': '_',
            'misc': 'SpaceAfter=No',
        },
        {
            'id': 4,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    assert len(errors) == 0


def test_text_reconstruction_mismatch(tmp_path: Path) -> None:
    """Test text reconstruction mismatch detection."""
    tokens = [
        {
            'id': 1,
            'form': 'John',
            'lemma': 'John',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'saw',
            'lemma': 'see',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'Mary',
            'lemma': 'Mary',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'obj',
            'deps': '_',
            'misc': 'SpaceAfter=No',
        },
        {
            'id': 4,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    # Override the text metadata to create a mismatch
    text = ConlluSentenceFactory.as_text(
        lang='en',
        tmp_path=tmp_path,
        tokens=tokens,
        sent_id='test-1',
        text='John saw Mary .',  # Mismatch: space before period
    )
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    text_errors = [e for e in errors if 'text-mismatch' in e]
    assert len(text_errors) == 1


def test_missing_text_attribute(tmp_path: Path) -> None:
    """Test detection of missing text attribute."""
    tokens = [
        {
            'id': 1,
            'form': 'John',
            'lemma': 'John',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'saw',
            'lemma': 'see',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    # Generate text without the text metadata
    text = ConlluSentenceFactory.as_text(
        lang='en',
        tmp_path=tmp_path,
        tokens=tokens,
        sent_id='test-1',
        text=None,  # No text metadata
    )
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    missing_text_errors = [e for e in errors if 'missing-text' in e]
    assert len(missing_text_errors) == 1


def test_missing_sent_id_attribute(tmp_path: Path) -> None:
    """Test detection of missing sent_id attribute."""
    tokens = [
        {
            'id': 1,
            'form': 'John',
            'lemma': 'John',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'saw',
            'lemma': 'see',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    # Generate text without the sent_id metadata
    text = ConlluSentenceFactory.as_text(
        lang='en',
        tmp_path=tmp_path,
        tokens=tokens,
        sent_id=None,  # No sent_id metadata
        text='John saw Mary.',
    )
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    missing_id_errors = [e for e in errors if 'missing-sent-id' in e]
    assert len(missing_id_errors) == 1
