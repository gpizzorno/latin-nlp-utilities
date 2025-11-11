"""Tests for DEPS (enhanced dependencies) character format validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


def test_valid_deps(tmp_path: Path) -> None:
    """Test that valid DEPS values are accepted."""
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    # Should not have invalid-edeprel errors
    error_text = '\n'.join(errors)
    assert 'invalid-edeprel' not in error_text


def test_valid_deps_with_subtype(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that DEPS with subtype is accepted."""
    sentence_en_tokens[2]['deps'] = '3:cc:pass'  # pass as subtype
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    # Should not have invalid-edeprel errors
    error_text = '\n'.join(errors)
    assert 'invalid-edeprel' not in error_text


def test_valid_deps_with_unicode_preposition(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that DEPS with Unicode preposition is accepted."""
    sentence_en_tokens[2]['deps'] = '3:cc:σύν'  # σύν as unicode subtype
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    # Should not have invalid-edeprel errors
    error_text = '\n'.join(errors)
    assert 'invalid-edeprel' not in error_text


def test_invalid_deps_uppercase(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that uppercase DEPS relation is rejected."""
    sentence_en_tokens[2]['deps'] = '3:CC'  # Invalid: uppercase
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    # Should have invalid-edeprel error
    error_text = '\n'.join(errors)
    assert 'invalid-edeprel' in error_text
    assert 'CC' in error_text


def test_invalid_deps_with_numbers(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that DEPS with numbers is rejected."""
    sentence_en_tokens[2]['deps'] = '2:nsubj1'  # Invalid: numbers
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    # Should have invalid-edeprel error
    error_text = '\n'.join(errors)
    assert 'invalid-edeprel' in error_text


def test_multiple_deps_relations(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that multiple DEPS relations are validated."""
    sentence_en_tokens[2]['deps'] = '2:nsubj|3:obj'  # Multiple valid relations
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    # Should not have invalid-edeprel errors
    error_text = '\n'.join(errors)
    assert 'invalid-edeprel' not in error_text


def test_invalid_multiple_deps_relations(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that invalid DEPS among multiple relations is detected."""
    sentence_en_tokens[2]['deps'] = '2:nsubj|3:OBJ'  # Invalid: uppercase
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    # Should have invalid-edeprel error for OBJ
    error_text = '\n'.join(errors)
    assert 'invalid-edeprel' in error_text
    assert 'OBJ' in error_text
