"""Tests for DEPREL character format validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_contains, assert_error_count, assert_no_errors_of_type


def test_valid_deprel(tmp_path: Path) -> None:
    """Test that valid DEPREL values are accepted."""
    test_file = ConlluSentenceFactory.as_file(tmp_path)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    # Should not have invalid-deprel errors
    assert_no_errors_of_type(errors, 'invalid-deprel')


def test_valid_deprel_with_subtype(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that DEPREL with subtype is accepted."""
    sentence_en_tokens[2]['deprel'] = 'cc:pass'  # pass as subtype
    test_file = ConlluSentenceFactory.as_file(tmp_path, lang='en', tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    # Should not have invalid-deprel errors
    assert_no_errors_of_type(errors, 'invalid-deprel')


def test_invalid_deprel_uppercase(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that uppercase DEPREL is rejected."""
    sentence_en_tokens[2]['deprel'] = 'CC'  # Invalid: uppercase
    test_file = ConlluSentenceFactory.as_file(tmp_path, lang='en', tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    # Should have invalid-deprel error
    assert_error_count(errors, 1, 'invalid-deprel')
    assert_error_contains(errors, 'invalid-deprel', 'CC')


def test_invalid_deprel_mixed_case(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that mixed case DEPREL is rejected."""
    sentence_en_tokens[2]['deprel'] = 'Cc'  # Invalid: mixed case
    test_file = ConlluSentenceFactory.as_file(tmp_path, lang='en', tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    # Should have invalid-deprel error
    assert_error_count(errors, 1, 'invalid-deprel')


def test_invalid_deprel_with_numbers(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that DEPREL with numbers is rejected."""
    sentence_en_tokens[2]['deprel'] = 'cc1'  # Invalid: contains number
    test_file = ConlluSentenceFactory.as_file(tmp_path, lang='en', tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    # Should have invalid-deprel error
    assert_error_count(errors, 1, 'invalid-deprel')


def test_empty_node_deprel_underscore(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that empty node with _ in DEPREL is allowed."""
    sentence_en_tokens[2]['id'] = '1.2'  # Ensure it's an empty node
    sentence_en_tokens[2]['deprel'] = '_'  # Allowed: underscore for empty node
    test_file = ConlluSentenceFactory.as_file(tmp_path, lang='en', tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    # Should not have invalid-deprel errors for empty node
    assert_no_errors_of_type(errors, 'invalid-deprel')
