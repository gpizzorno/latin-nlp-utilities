"""Test ID sequence validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


def test_valid_sequence(tmp_path: Path) -> None:
    """Test that valid ID sequence passes."""
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path)
    validator = ConlluValidator(level=1)
    errors = validator.validate_file(test_file)
    # Should not have sequence errors
    assert not any('sequence' in e.lower() for e in errors)


def test_out_of_order_ids(tmp_path: Path) -> None:
    """Test that out of order IDs are detected."""
    tokens = [
        {
            'id': 1,
            'form': 'word1',
            'lemma': 'word1',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'word3',
            'lemma': 'word3',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'dep',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'word2',
            'lemma': 'word2',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'dep',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_file(test_file)
    assert any('word-id-sequence' in e for e in errors)
    assert any('1,3,2' in e for e in errors)  # Actual sequence
    assert any('1,2,3' in e for e in errors)  # Expected sequence


def test_gap_in_ids(tmp_path: Path) -> None:
    """Test that gaps in ID sequence are detected."""
    tokens = [
        {
            'id': 1,
            'form': 'word1',
            'lemma': 'word1',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'word3',
            'lemma': 'word3',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'dep',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_file(test_file)
    assert any('word-id-sequence' in e for e in errors)
    assert any('1,3' in e for e in errors)  # Actual sequence
    assert any('1,2' in e for e in errors)  # Expected sequence


def test_duplicate_ids(tmp_path: Path) -> None:
    """Test that duplicate IDs are detected."""
    tokens = [
        {
            'id': 1,
            'form': 'word1',
            'lemma': 'word1',
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
            'form': 'word2',
            'lemma': 'word2',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'dep',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'word2b',
            'lemma': 'word2b',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'dep',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_file(test_file)
    assert any('duplicate-word-id' in e for e in errors)
    # Should also have sequence error (1,2,2 != 1,2,3)
    assert any('word-id-sequence' in e for e in errors)


def test_ids_not_starting_at_1(tmp_path: Path) -> None:
    """Test that IDs not starting at 1 are detected."""
    tokens = [
        {
            'id': 2,
            'form': 'word2',
            'lemma': 'word2',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'word3',
            'lemma': 'word3',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'dep',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_file(test_file)
    assert any('word-id-not-starting-at-1' in e for e in errors)
    # Should also have sequence error
    assert any('word-id-sequence' in e for e in errors)


def test_multiple_errors(tmp_path: Path) -> None:
    """Test that multiple ID sequence errors are detected."""
    tokens = [
        {
            'id': 1,
            'form': 'word1',
            'lemma': 'word1',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': '1.2',
            'form': '_',
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
            'id': 3,
            'form': 'word3',
            'lemma': 'word3',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'dep',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': '2-3',
            'form': 'multiword',
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
    # Should detect: gap in IDs (1,3), empty node skipping 1.1, MWT after words
    assert any('word-id-sequence' in e for e in errors)
    assert any('empty-node-sequence' in e for e in errors)
    assert any('mwt-not-before-words' in e for e in errors)


def test_mwt_with_empty_nodes(tmp_path: Path) -> None:
    """Test that MWT and empty nodes can coexist correctly."""
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
            'id': '1.1',
            'form': '_',
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
        {
            'id': 3,
            'form': 'word3',
            'lemma': 'word3',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'dep',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_file(test_file)
    # All IDs are valid
    assert not any('sequence' in e.lower() for e in errors)
    assert not any('mwt-not-before-words' in e for e in errors)
    assert not any('empty-node' in e for e in errors)
