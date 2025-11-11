"""Tests for DEPS column structural validation (sorting and duplicates)."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


def test_deps_sorted_by_head(tmp_path: Path) -> None:
    """Test that DEPS are correctly sorted by head index."""
    # Valid: sorted by head
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root|2:nsubj',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nmod',
            'deps': '1:nmod',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    deps_errors = [e for e in errors if 'unsorted-deps' in e or 'repeated-deps' in e]
    assert len(deps_errors) == 0, f'Expected no DEPS errors, got: {deps_errors}'


def test_deps_unsorted_by_head(tmp_path: Path) -> None:
    """Test that unsorted DEPS by head are caught."""
    # Invalid: not sorted by head (2 comes before 0)
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '2:nsubj|0:root',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nmod',
            'deps': '1:nmod',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    assert any('unsorted-deps' in e and '2:nsubj|0:root' in e for e in errors), (
        f'Expected unsorted-deps error, got: {errors}'
    )


def test_deps_duplicate_relation(tmp_path: Path) -> None:
    """Test that duplicate head:deprel pairs are caught."""
    # Invalid: duplicate 0:root
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root|0:root',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    assert any('repeated-deps' in e and '0:root' in e for e in errors), f'Expected repeated-deps error, got: {errors}'


def test_deps_same_head_sorted_relations(tmp_path: Path) -> None:
    """Test that relations for same head are alphabetically sorted."""
    # Valid: same head 2, relations sorted (nsubj < xcomp)
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root|2:nsubj|2:xcomp',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nsubj',
            'deps': '1:nsubj',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    deps_errors = [e for e in errors if 'unsorted-deps' in e or 'repeated-deps' in e]
    assert len(deps_errors) == 0, f'Expected no DEPS errors, got: {deps_errors}'


def test_deps_same_head_unsorted_relations(tmp_path: Path) -> None:
    """Test that unsorted relations for same head are caught."""
    # Invalid: same head 2, relations not sorted (xcomp > nsubj)
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root|2:xcomp|2:nsubj',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nsubj',
            'deps': '1:nsubj',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    assert any('unsorted-deps-2' in e and "head '2'" in e for e in errors), (
        f'Expected unsorted-deps-2 error for same-head relations, got: {errors}'
    )


def test_deps_with_empty_nodes(tmp_path: Path) -> None:
    """Test DEPS validation with decimal (empty node) heads."""
    # Valid: sorted with empty node heads (1.1 < 2)
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root|1.1:aux|2:nsubj',
            'misc': '_',
        },
        {
            'id': '1.1',
            'form': 'was',
            'lemma': 'be',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nsubj',
            'deps': '1:nsubj',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    deps_errors = [e for e in errors if 'unsorted-deps' in e or 'repeated-deps' in e]
    assert len(deps_errors) == 0, f'Expected no DEPS errors with empty nodes, got: {deps_errors}'


def test_deps_single_dependency(tmp_path: Path) -> None:
    """Test that single DEPS entries don't trigger validation (nothing to sort)."""
    # Valid: single dependency, nothing to validate
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    deps_errors = [e for e in errors if 'unsorted-deps' in e or 'repeated-deps' in e]
    assert len(deps_errors) == 0, f'Expected no DEPS errors for single dependency, got: {deps_errors}'
