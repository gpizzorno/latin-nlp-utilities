"""Tests for DEPS column structural validation (sorting and duplicates)."""

from pathlib import Path

from conllu_tools.validation.validator import ConlluValidator
from tests.factories import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_contains, assert_error_count, assert_no_errors_of_type


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
    assert_no_errors_of_type(errors, 'unsorted-deps')
    assert_no_errors_of_type(errors, 'repeated-deps')


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
    assert_error_count(errors, 1, 'unsorted-deps')
    assert_error_contains(errors, 'unsorted-deps', '2:nsubj|0:root')


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
    assert_error_count(errors, 1, 'repeated-deps')
    assert_error_contains(errors, 'repeated-deps', '0:root')


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
    assert_no_errors_of_type(errors, 'unsorted-deps')
    assert_no_errors_of_type(errors, 'repeated-deps')


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
    assert_error_count(errors, 1, 'unsorted-deps-2')
    assert_error_contains(errors, 'unsorted-deps-2', "head '2'")


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
    assert_no_errors_of_type(errors, 'unsorted-deps')
    assert_no_errors_of_type(errors, 'repeated-deps')


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
    assert_no_errors_of_type(errors, 'unsorted-deps')
    assert_no_errors_of_type(errors, 'repeated-deps')
