"""Integration tests for whitespace validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_count, assert_no_errors_of_type


def test_level_3_no_whitespace_validation(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that Level 3 doesn't validate whitespace."""
    sentence_en_tokens[2]['form'] = 'foo bar'  # Invalid: does not match exception
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_file(test_file)
    # Level 3 should not check whitespace
    assert_no_errors_of_type(errors, 'invalid-word-with-space')


def test_level_4_whitespace_validation(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that Level 4 validates whitespace."""
    sentence_en_tokens[2]['form'] = 'foo bar'  # Invalid: does not match exception
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=4)
    errors = validator.validate_file(test_file)
    # Level 4 should check whitespace
    assert_error_count(errors, 1, 'invalid-word-with-space')


def test_number_pattern_with_spaces(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test various number patterns with spaces."""
    test_cases = [
        ('123', True),  # Plain number (no space but matches [0-9 ]+)
        ('12 345', True),  # Number with space
        ('1 2 3 4', True),  # Multiple spaces
        ('12 345 678', True),  # Many digits with spaces
    ]

    for form, should_pass in test_cases:
        sentence_en_tokens[2]['form'] = form
        test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
        validator = ConlluValidator(level=4)
        errors = validator.validate_file(test_file)
        if should_pass:
            assert_no_errors_of_type(errors, 'invalid-word-with-space')
        else:
            assert_error_count(errors, 1, 'invalid-word-with-space')


def test_decimal_pattern_with_spaces(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test decimal number patterns with spaces."""
    test_cases = [
        ('12 345.67', True),  # Space before decimal point
        ('12 345,67', True),  # Space before decimal comma
        ('1 234.5', True),  # One space
        ('123.45', True),  # No space but matches pattern
    ]

    for form, should_pass in test_cases:
        sentence_en_tokens[2]['form'] = form
        test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
        validator = ConlluValidator(level=4)
        errors = validator.validate_file(test_file)
        if should_pass:
            assert_no_errors_of_type(errors, 'invalid-word-with-space')
        else:
            assert_error_count(errors, 1, 'invalid-word-with-space')


def test_non_matching_patterns(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test patterns that should not match any exception."""
    test_cases = [
        'foo bar',  # Regular words
        'test word',  # Regular words
        'abc 123',  # Letters and numbers
        '12 abc',  # Number with letters
        'hello world',  # Common phrase
    ]

    for form in test_cases:
        sentence_en_tokens[2]['form'] = form
        test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
        validator = ConlluValidator(level=4)
        errors = validator.validate_file(test_file)
        assert_error_count(errors, 1, 'invalid-word-with-space')


def test_multiple_tokens_mixed_validity(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test sentence with mix of valid and invalid tokens."""
    sentence_en_tokens[0]['form'] = 'word1'
    sentence_en_tokens[1]['form'] = 'foo bar'
    sentence_en_tokens[2]['form'] = '12 345'
    sentence_en_tokens[3]['form'] = 'baz qux'
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=4)
    errors = validator.validate_file(test_file)
    # Should have 2 errors: tokens 2 and 4 have invalid spaces
    assert_error_count(errors, 2, 'invalid-word-with-space')


def test_ud_language_no_validation(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that 'ud' language doesn't validate whitespace (no exceptions loaded)."""
    sentence_en_tokens[0]['form'] = 'foo bar'
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(lang='ud', level=4)
    errors = validator.validate_file(test_file)
    # With lang='ud', no language-specific data is loaded
    # So whitespace validation should still happen but with empty exception list
    assert_error_count(errors, 1, 'invalid-word-with-space')


def test_empty_form_no_validation(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that empty FORM doesn't trigger validation."""
    sentence_en_tokens[0]['form'] = '_'
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=4)
    errors = validator.validate_file(test_file)
    # Empty node with _ should not trigger whitespace validation
    assert_no_errors_of_type(errors, 'invalid-word-with-space')
