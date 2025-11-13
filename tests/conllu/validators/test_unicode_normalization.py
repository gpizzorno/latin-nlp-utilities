"""Tests for Unicode normalization validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_contains, assert_error_count, assert_no_errors_of_type


# Test Unicode normalization for FORM column
def test_form_normalized(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that normalized FORM passes validation."""
    sentence_en_tokens[2]['form'] = 'café'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'unicode-normalization')


def test_form_not_normalized(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that non-normalized FORM is flagged."""
    # Use NFD decomposed form (é = e + combining acute)
    sentence_en_tokens[2]['form'] = 'cafe\u0301'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    assert_error_count(errors, 1, 'unicode-normalization')
    assert_error_contains(errors, 'unicode-normalization', 'FORM')


def test_form_ascii_no_error(tmp_path: Path) -> None:
    """Test that ASCII FORM has no normalization issues."""
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'unicode-normalization')


# Test Unicode normalization for LEMMA column
def test_lemma_normalized(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that normalized LEMMA passes validation."""
    sentence_en_tokens[2]['lemma'] = 'café'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'unicode-normalization')


def test_lemma_not_normalized(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that non-normalized LEMMA is flagged."""
    # Use NFD decomposed form (é = e + combining acute)
    sentence_en_tokens[2]['lemma'] = 'cafe\u0301'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    assert_error_count(errors, 1, 'unicode-normalization')
    assert_error_contains(errors, 'unicode-normalization', 'LEMMA')


def test_lemma_underscore_skipped(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that underscore LEMMA is not validated."""
    sentence_en_tokens[1]['id'] = '3-4'  # Multiword token
    sentence_en_tokens[2]['lemma'] = '_'  # Underscore lemma for Multiword token
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'unicode-normalization')


def test_lemma_empty_skipped(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that empty LEMMA is not validated."""
    sentence_en_tokens[2]['lemma'] = '_'  # Empty lemma
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    # Should not have unicode-normalization error
    assert_no_errors_of_type(errors, 'unicode-normalization')


def test_lemma_ascii_no_error(tmp_path: Path) -> None:
    """Test that ASCII LEMMA has no normalization issues."""
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'unicode-normalization')


# Test Unicode normalization for both FORM and LEMMA
def test_both_normalized(tmp_path: Path) -> None:
    """Test that both FORM and LEMMA normalized pass."""
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'unicode-normalization')


def test_both_not_normalized(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that both FORM and LEMMA non-normalized are flagged."""
    # Use NFD decomposed form (é = e + combining acute)
    sentence_en_tokens[2]['form'] = 'cafe\u0301'
    sentence_en_tokens[2]['lemma'] = 'cafe\u0301'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    # Should have 2 errors: one for FORM, one for LEMMA
    assert_error_count(errors, 2, 'unicode-normalization')
    assert_error_contains(errors, 'unicode-normalization', 'FORM')
    assert_error_contains(errors, 'unicode-normalization', 'LEMMA')


def test_form_normalized_lemma_not(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test FORM normalized but LEMMA not normalized."""
    sentence_en_tokens[2]['form'] = 'café'
    sentence_en_tokens[2]['lemma'] = 'cafe\u0301'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    # Should have only LEMMA error
    assert_error_count(errors, 1, 'unicode-normalization')
    assert_error_contains(errors, 'unicode-normalization', 'LEMMA')


def test_form_not_normalized_lemma_normalized(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test FORM not normalized but LEMMA normalized."""
    sentence_en_tokens[2]['lemma'] = 'café'
    sentence_en_tokens[2]['form'] = 'cafe\u0301'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    # Should have only FORM error
    assert_error_count(errors, 1, 'unicode-normalization')
    assert_error_contains(errors, 'unicode-normalization', 'FORM')


# Test Unicode normalization with multiple tokens
def test_multiple_tokens_mixed(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test sentence with some normalized and some not."""
    sentence_en_tokens[2]['lemma'] = 'café'
    sentence_en_tokens[2]['form'] = 'café'
    sentence_en_tokens[3]['lemma'] = 'naive\u0308'
    sentence_en_tokens[3]['form'] = 'nai\u0308ve'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    # Token at index 2 (café) is normalized (0 errors)
    # Token at index 3 (naïve with decomposed diacritics) has non-normalized FORM and LEMMA (2 errors)
    assert_error_count(errors, 2, 'unicode-normalization')
    # Both errors should mention Unicode normalization issues
    assert_error_contains(errors, 'unicode-normalization', 'LATIN SMALL LETTER I')
    assert_error_contains(errors, 'unicode-normalization', 'LATIN SMALL LETTER E')


def test_all_tokens_normalized(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that all normalized tokens pass."""
    sentence_en_tokens[3]['form'] = 'café'
    sentence_en_tokens[3]['lemma'] = 'café'
    sentence_en_tokens[4]['form'] = 'naïve'
    sentence_en_tokens[4]['lemma'] = 'naïf'
    sentence_en_tokens[5]['form'] = 'résumé'
    sentence_en_tokens[5]['lemma'] = 'résumé'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'unicode-normalization')
