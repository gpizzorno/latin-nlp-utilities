"""Tests for text reconstruction and metadata validation."""

from pathlib import Path

from conllu_tools.validation.validator import ConlluValidator
from tests.factories import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_count


def test_text_reconstruction_basic(tmp_path: Path) -> None:
    """Test basic text reconstruction with spaces."""
    tokens = [
        {
            'id': 1,
            'form': 'The',
            'lemma': 'the',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'quick',
            'lemma': 'quick',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'amod',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'brown',
            'lemma': 'brown',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
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
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]

    test_file = ConlluSentenceFactory.as_file(
        lang='en',
        tmp_path=tmp_path,
        tokens=tokens,
    )
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    assert_error_count(errors, 0)


def test_text_reconstruction_mismatch(tmp_path: Path) -> None:
    """Test text reconstruction mismatch detection."""
    tokens = [
        {
            'id': 1,
            'form': 'The',
            'lemma': 'the',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'quick',
            'lemma': 'quick',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'amod',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'brown',
            'lemma': 'brown',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
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
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]

    # Override the text metadata to create a mismatch (space before period)
    test_file = ConlluSentenceFactory.as_file(
        lang='en',
        tmp_path=tmp_path,
        tokens=tokens,
        text='The quick brown .',  # Mismatch: space before period
    )
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    assert_error_count(errors, 1, 'text-mismatch')


def test_missing_text_attribute(tmp_path: Path) -> None:
    """Test detection of missing text attribute."""
    # Manually construct file without text attribute (factory always includes it)
    tokens = [
        {
            'id': 1,
            'form': 'The',
            'lemma': 'the',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'quick',
            'lemma': 'quick',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'amod',
            'deps': '_',
            'misc': '_',
        },
    ]

    test_file = tmp_path / 'test.conllu'
    lines = ['# sent_id = test-1']
    for token in tokens:
        line = '\t'.join(
            str(token[field])
            for field in ['id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc']
        )
        lines.append(line)
    lines.append('')  # Blank line
    test_file.write_text('\n'.join(lines))

    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    assert_error_count(errors, 1, 'missing-text')


def test_missing_sent_id_attribute(tmp_path: Path) -> None:
    """Test detection of missing sent_id attribute."""
    # Manually construct file without sent_id attribute (factory always includes it)
    tokens = [
        {
            'id': 1,
            'form': 'The',
            'lemma': 'the',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'quick',
            'lemma': 'quick',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]

    test_file = tmp_path / 'test.conllu'
    lines = ['# text = The quick.']
    for token in tokens:
        line = '\t'.join(
            str(token[field])
            for field in ['id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc']
        )
        lines.append(line)
    lines.append('')  # Blank line
    test_file.write_text('\n'.join(lines))

    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    assert_error_count(errors, 1, 'missing-sent-id')
