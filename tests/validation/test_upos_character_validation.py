"""Tests for UPOS character format validation."""

from pathlib import Path

from conllu_tools.validation.validator import ConlluValidator
from tests.factories import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_contains, assert_error_count, assert_no_errors_of_type


def test_valid_upos(tmp_path: Path) -> None:
    """Test that valid UPOS values are accepted."""
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    # Should not have invalid-upos errors
    assert_no_errors_of_type(errors, 'invalid-upos')


def test_invalid_upos_lowercase(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that lowercase UPOS is rejected."""
    sentence_en_tokens[2]['upostag'] = 'noun'  # Invalid: lowercase
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    # Should have invalid-upos error
    assert_error_count(errors, 1, 'invalid-upos')
    assert_error_contains(errors, 'invalid-upos', 'noun')


def test_invalid_upos_mixed_case(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that mixed case UPOS is rejected."""
    sentence_en_tokens[2]['upostag'] = 'Noun'  # Invalid: mixed case
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    # Should have invalid-upos error
    assert_error_count(errors, 1, 'invalid-upos')


def test_invalid_upos_with_numbers(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that UPOS with numbers is rejected."""
    sentence_en_tokens[2]['upostag'] = 'NOUN1'  # Invalid: contains number
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    # Should have invalid-upos error
    assert_error_count(errors, 1, 'invalid-upos')


def test_empty_node_upos_underscore(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that empty node with _ in UPOS is allowed."""
    sentence_en_tokens[2]['id'] = '1.2'  # Ensure it's an empty node
    sentence_en_tokens[2]['upostag'] = '_'  # Allowed: underscore for empty node
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    # Should not have invalid-upos errors for empty node
    assert_no_errors_of_type(errors, 'invalid-upos')
