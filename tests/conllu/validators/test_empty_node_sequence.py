"""Test empty node sequence validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


def test_valid_empty_node_sequence(tmp_path: Path) -> None:
    """Test that valid empty node sequence passes."""
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
    assert not any('empty-node-sequence' in e for e in errors)


def test_empty_node_skipping_1(tmp_path: Path) -> None:
    """Test that empty node skipping X.1 is detected."""
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
    assert any('empty-node-sequence' in e for e in errors)
    assert any('1.2' in e for e in errors)
    assert any('1.1' in e for e in errors)


def test_empty_node_gap(tmp_path: Path) -> None:
    """Test that gap in empty node sequence is detected."""
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
            'id': '1.3',
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
    assert any('empty-node-sequence' in e for e in errors)


def test_duplicate_empty_node(tmp_path: Path) -> None:
    """Test that duplicate empty node IDs are detected."""
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
    assert any('duplicate-empty-node-id' in e for e in errors)
    assert any('1.1' in e for e in errors)


def test_empty_node_wrong_word(tmp_path: Path) -> None:
    """Test that empty node after wrong word is detected."""
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
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_file(test_file)
    # Empty node 1.1 comes after word 2, so it should appear before word 2
    assert any('empty-node-not-before-next-word' in e for e in errors)


def test_empty_node_before_word(tmp_path: Path) -> None:
    """Test that empty node before its word is detected."""
    tokens = [
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
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_file(test_file)
    assert any('empty-node-not-after-word' in e for e in errors)
