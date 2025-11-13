"""Test validation of whitespace in FORM and LEMMA fields."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_contains, assert_error_count, assert_no_errors_of_type


def test_valid_word_no_whitespace(tmp_path: Path) -> None:
    """Test that words without whitespace are valid."""
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path)
    validator = ConlluValidator(level=4)
    errors = validator.validate_file(test_file)
    # Should not have invalid-word-with-space errors
    assert_no_errors_of_type(errors, 'invalid-word-with-space')


def test_valid_number_with_space_form(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that numbers with spaces in FORM are allowed (matches exception)."""
    sentence_en_tokens[2]['form'] = '12 345'  # Allowed: matches exception
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    # Should pass - matches pattern [0-9 ]+ in tokens_w_space
    assert_no_errors_of_type(errors, 'invalid-word-with-space')


def test_valid_decimal_with_space_form(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that decimals with spaces in FORM are allowed (matches exception)."""
    sentence_en_tokens[2]['form'] = '345,67'  # Allowed: matches exception
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=4)
    errors = validator.validate_file(test_file)
    # Should pass - matches pattern [0-9 ]+[,.][0-9]+ in tokens_w_space
    assert_no_errors_of_type(errors, 'invalid-word-with-space')


def test_invalid_word_with_space_form(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that words with spaces in FORM are invalid (not in exceptions)."""
    sentence_en_tokens[2]['form'] = 'foo bar'  # Invalid: does not match exception
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=4)
    errors = validator.validate_file(test_file)
    assert_error_count(errors, 1, 'invalid-word-with-space')
    assert_error_contains(errors, 'invalid-word-with-space', 'foo bar')
    assert_error_contains(errors, 'invalid-word-with-space', 'FORM')


def test_invalid_word_with_space_lemma(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that words with spaces in LEMMA are invalid (not in exceptions)."""
    sentence_en_tokens[2]['lemma'] = 'foo bar'  # Invalid: does not match exception
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=4)
    errors = validator.validate_file(test_file)
    assert_error_count(errors, 1, 'invalid-word-with-space')
    assert_error_contains(errors, 'invalid-word-with-space', 'foo bar')
    assert_error_contains(errors, 'invalid-word-with-space', 'LEMMA')


def test_invalid_word_with_space_both(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that words with spaces in both FORM and LEMMA produce two errors."""
    sentence_en_tokens[2]['form'] = 'foo bar'  # Invalid: does not match exception
    sentence_en_tokens[2]['lemma'] = 'foo bar'  # Invalid: does not match exception
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=4)
    errors = validator.validate_file(test_file)
    assert_error_count(errors, 2, 'invalid-word-with-space')
    assert_error_contains(errors, 'invalid-word-with-space', 'FORM')
    assert_error_contains(errors, 'invalid-word-with-space', 'LEMMA')


def test_valid_underscore_form(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that underscore in FORM doesn't trigger validation."""
    sentence_en_tokens[2]['form'] = 'foo_bar'  # Should not trigger validation
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=4)
    errors = validator.validate_file(test_file)
    # Multiword token is skipped, no errors for the MWT FORM
    assert_no_errors_of_type(errors, 'invalid-word-with-space')


def test_multiword_token_skipped(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that multiword tokens are skipped in whitespace validation."""
    sentence_en_tokens[1]['id'] = '1-2'  # Make token 1 a multiword token
    sentence_en_tokens[1]['form'] = 'invalid space'  # Invalid: does not match exception
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=4)
    errors = validator.validate_file(test_file)
    # Multiword token with space should be skipped
    # (Note: MWT should have _ in LEMMA, but that's a different validation)
    assert_no_errors_of_type(errors, 'invalid-word-with-space')
