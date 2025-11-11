"""Tests for Unicode normalization validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


# Test Unicode normalization for FORM column
def test_form_normalized(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that normalized FORM passes validation."""
    sentence_en_tokens[2]['form'] = 'café'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    unicode_errors = [e for e in errors if 'unicode-normalization' in e]
    assert len(unicode_errors) == 0


def test_form_not_normalized(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that non-normalized FORM is flagged."""
    # Use NFD decomposed form (é = e + combining acute)
    sentence_en_tokens[2]['form'] = 'cafe\u0301'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    unicode_errors = [e for e in errors if 'unicode-normalization' in e and 'FORM' in e]
    assert len(unicode_errors) == 1
    assert 'cafe\u0301' in unicode_errors[0] or 'FORM' in unicode_errors[0]


def test_form_ascii_no_error(tmp_path: Path) -> None:
    """Test that ASCII FORM has no normalization issues."""
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    unicode_errors = [e for e in errors if 'unicode-normalization' in e]
    assert len(unicode_errors) == 0


# Test Unicode normalization for LEMMA column
def test_lemma_normalized(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that normalized LEMMA passes validation."""
    sentence_en_tokens[2]['lemma'] = 'café'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    unicode_errors = [e for e in errors if 'unicode-normalization' in e and 'LEMMA' in e]
    assert len(unicode_errors) == 0


def test_lemma_not_normalized(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that non-normalized LEMMA is flagged."""
    # Use NFD decomposed form (é = e + combining acute)
    sentence_en_tokens[2]['lemma'] = 'cafe\u0301'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    unicode_errors = [e for e in errors if 'unicode-normalization' in e and 'LEMMA' in e]
    assert len(unicode_errors) == 1
    assert 'cafe\u0301' in unicode_errors[0] or 'LEMMA' in unicode_errors[0]


def test_lemma_underscore_skipped(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that underscore LEMMA is not validated."""
    sentence_en_tokens[1]['id'] = '3-4'  # Multiword token
    sentence_en_tokens[2]['lemma'] = '_'  # Underscore lemma for Multiword token
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    unicode_errors = [e for e in errors if 'unicode-normalization' in e and 'LEMMA' in e]
    assert len(unicode_errors) == 0


def test_lemma_empty_skipped(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that empty LEMMA is not validated."""
    sentence_en_tokens[2]['lemma'] = ''  # Empty lemma
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    # Should have empty-lemma error but not unicode-normalization
    unicode_errors = [e for e in errors if 'unicode-normalization' in e and 'LEMMA' in e]
    assert len(unicode_errors) == 0


def test_lemma_ascii_no_error(tmp_path: Path) -> None:
    """Test that ASCII LEMMA has no normalization issues."""
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    unicode_errors = [e for e in errors if 'unicode-normalization' in e and 'LEMMA' in e]
    assert len(unicode_errors) == 0


# Test Unicode normalization for both FORM and LEMMA
def test_both_normalized(tmp_path: Path) -> None:
    """Test that both FORM and LEMMA normalized pass."""
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    unicode_errors = [e for e in errors if 'unicode-normalization' in e]
    assert len(unicode_errors) == 0


def test_both_not_normalized(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that both FORM and LEMMA non-normalized are flagged."""
    # Use NFD decomposed form (é = e + combining acute)
    sentence_en_tokens[2]['form'] = 'cafe\u0301'
    sentence_en_tokens[2]['lemma'] = 'cafe\u0301'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    unicode_errors = [e for e in errors if 'unicode-normalization' in e]
    # Should have 2 errors: one for FORM, one for LEMMA
    assert len(unicode_errors) == 2  # noqa: PLR2004
    form_errors = [e for e in unicode_errors if 'FORM' in e]
    lemma_errors = [e for e in unicode_errors if 'LEMMA' in e]
    assert len(form_errors) == 1
    assert len(lemma_errors) == 1


def test_form_normalized_lemma_not(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test FORM normalized but LEMMA not normalized."""
    sentence_en_tokens[2]['form'] = 'café'
    sentence_en_tokens[2]['lemma'] = 'cafe\u0301'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    unicode_errors = [e for e in errors if 'unicode-normalization' in e]
    # Should have only LEMMA error
    assert len(unicode_errors) == 1
    assert 'LEMMA' in unicode_errors[0]


def test_form_not_normalized_lemma_normalized(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test FORM not normalized but LEMMA normalized."""
    sentence_en_tokens[2]['lemma'] = 'café'
    sentence_en_tokens[2]['form'] = 'cafe\u0301'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    unicode_errors = [e for e in errors if 'unicode-normalization' in e]
    # Should have only FORM error
    assert len(unicode_errors) == 1
    assert 'FORM' in unicode_errors[0]


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
    unicode_errors = [e for e in errors if 'unicode-normalization' in e]
    # Token 1 is normalized (0 errors)
    # Token 2 has non-normalized FORM and LEMMA (2 errors)
    assert len(unicode_errors) == 2  # noqa: PLR2004
    # Both errors should be for token 2
    assert all('2' in e or 'nai' in e for e in unicode_errors)


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
    unicode_errors = [e for e in errors if 'unicode-normalization' in e]
    assert len(unicode_errors) == 0
