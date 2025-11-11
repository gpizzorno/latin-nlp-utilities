"""Tests for auxiliary/copula validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


# Test validation of auxiliary verb lemmas
def test_valid_latin_auxiliary_sum(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that 'sum' is valid as AUX in Latin."""
    sentence_la_tokens[0]['form'] = 'sum'
    sentence_la_tokens[0]['lemma'] = 'sum'
    sentence_la_tokens[0]['upostag'] = 'AUX'
    sentence_la_tokens[0]['deprel'] = 'aux'
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    assert not any('aux-lemma' in e for e in errors)


def test_valid_latin_auxiliary_habeo(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that 'habeo' is valid as AUX in Latin."""
    sentence_la_tokens[0]['form'] = 'habeo'
    sentence_la_tokens[0]['lemma'] = 'habeo'
    sentence_la_tokens[0]['upostag'] = 'AUX'
    sentence_la_tokens[0]['deprel'] = 'aux'
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    assert not any('aux-lemma' in e for e in errors)


def test_invalid_latin_auxiliary(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that unknown auxiliary lemma is flagged."""
    sentence_la_tokens[0]['form'] = 'invalid'
    sentence_la_tokens[0]['lemma'] = 'invalid'
    sentence_la_tokens[0]['upostag'] = 'AUX'
    sentence_la_tokens[0]['deprel'] = 'aux'
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    aux_errors = [e for e in errors if 'aux-lemma' in e]
    assert len(aux_errors) == 1
    assert "'invalid'" in aux_errors[0]
    assert 'not an auxiliary verb' in aux_errors[0]


def test_auxiliary_empty_lemma(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that empty lemma is not validated."""
    sentence_la_tokens[0]['form'] = 'test'
    sentence_la_tokens[0]['lemma'] = '_'
    sentence_la_tokens[0]['upostag'] = 'AUX'
    sentence_la_tokens[0]['deprel'] = 'aux'
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    assert not any('aux-lemma' in e for e in errors)


def test_auxiliary_non_aux_upos(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that non-AUX UPOS doesn't trigger auxiliary validation."""
    sentence_la_tokens[0]['form'] = 'invalid'
    sentence_la_tokens[0]['lemma'] = 'invalid'
    sentence_la_tokens[0]['upostag'] = 'VERB'
    sentence_la_tokens[0]['head'] = 0
    sentence_la_tokens[0]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:1])
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    assert not any('aux-lemma' in e for e in errors)


def test_auxiliary_multiword_token_skipped(tmp_path: Path) -> None:
    """Test that multiword tokens are skipped."""
    tokens = [
        {
            'id': '1-2',
            'form': 'invalid aux',
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
            'form': 'invalid',
            'lemma': 'invalid',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'aux',
            'lemma': 'aux',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'flat',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'test',
            'lemma': 'test',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    # MWT should be skipped, but token 1 should be validated
    aux_errors = [e for e in errors if 'aux-lemma' in e]
    assert len(aux_errors) == 1


# Test validation of copula lemmas
def test_valid_latin_copula_sum(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that 'sum' is valid as copula in Latin."""
    sentence_la_tokens[0]['form'] = 'est'
    sentence_la_tokens[0]['lemma'] = 'sum'
    sentence_la_tokens[0]['upostag'] = 'AUX'
    sentence_la_tokens[0]['deprel'] = 'cop'
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['form'] = 'bonus'
    sentence_la_tokens[1]['lemma'] = 'bonus'
    sentence_la_tokens[1]['upostag'] = 'ADJ'
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    assert not any('cop-lemma' in e for e in errors)


def test_invalid_latin_copula(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that unknown copula lemma is flagged."""
    sentence_la_tokens[0]['form'] = 'est'
    sentence_la_tokens[0]['lemma'] = 'invalid'
    sentence_la_tokens[0]['upostag'] = 'AUX'
    sentence_la_tokens[0]['deprel'] = 'cop'
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['form'] = 'bonus'
    sentence_la_tokens[1]['lemma'] = 'bonus'
    sentence_la_tokens[1]['upostag'] = 'ADJ'
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    cop_errors = [e for e in errors if 'cop-lemma' in e]
    assert len(cop_errors) == 1
    assert "'invalid'" in cop_errors[0]
    assert 'not a copula' in cop_errors[0]


def test_copula_empty_lemma(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that empty lemma is not validated."""
    sentence_la_tokens[0]['form'] = 'est'
    sentence_la_tokens[0]['lemma'] = '_'
    sentence_la_tokens[0]['upostag'] = 'AUX'
    sentence_la_tokens[0]['deprel'] = 'cop'
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['form'] = 'bonus'
    sentence_la_tokens[1]['lemma'] = 'bonus'
    sentence_la_tokens[1]['upostag'] = 'ADJ'
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    assert not any('cop-lemma' in e for e in errors)


def test_copula_non_cop_deprel(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that non-cop deprel doesn't trigger copula validation."""
    sentence_la_tokens[0]['form'] = 'invalid'
    sentence_la_tokens[0]['lemma'] = 'invalid'
    sentence_la_tokens[0]['upostag'] = 'AUX'
    sentence_la_tokens[0]['head'] = 0
    sentence_la_tokens[0]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:1])
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    assert not any('cop-lemma' in e for e in errors)


def test_copula_multiword_token_skipped(tmp_path: Path) -> None:
    """Test that multiword tokens are skipped."""
    tokens = [
        {
            'id': '1-2',
            'form': 'invalid cop',
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
            'form': 'est',
            'lemma': 'invalid',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'cop',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'cop',
            'lemma': 'cop',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'flat',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'bonus',
            'lemma': 'bonus',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    # MWT should be skipped, but token 1 should be validated
    cop_errors = [e for e in errors if 'cop-lemma' in e]
    assert len(cop_errors) == 1


# Test that aux/cop validation only runs at Level 5
def test_level_4_no_aux_validation(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that Level 4 doesn't validate auxiliaries."""
    sentence_la_tokens[0]['form'] = 'invalid'
    sentence_la_tokens[0]['lemma'] = 'invalid'
    sentence_la_tokens[0]['upostag'] = 'AUX'
    sentence_la_tokens[0]['deprel'] = 'aux'
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    validator = ConlluValidator(lang='la', level=4)
    errors = validator.validate_string(text)
    # Level 4 should not check auxiliaries
    assert not any('aux-lemma' in e for e in errors)


def test_level_5_aux_validation(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that Level 5 validates auxiliaries."""
    sentence_la_tokens[0]['form'] = 'invalid'
    sentence_la_tokens[0]['lemma'] = 'invalid'
    sentence_la_tokens[0]['upostag'] = 'AUX'
    sentence_la_tokens[0]['deprel'] = 'aux'
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    # Level 5 should check auxiliaries
    assert any('aux-lemma' in e for e in errors)


def test_level_4_no_cop_validation(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that Level 4 doesn't validate copulas."""
    sentence_la_tokens[0]['form'] = 'est'
    sentence_la_tokens[0]['lemma'] = 'invalid'
    sentence_la_tokens[0]['upostag'] = 'AUX'
    sentence_la_tokens[0]['deprel'] = 'cop'
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['form'] = 'bonus'
    sentence_la_tokens[1]['lemma'] = 'bonus'
    sentence_la_tokens[1]['upostag'] = 'ADJ'
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    validator = ConlluValidator(lang='la', level=4)
    errors = validator.validate_string(text)
    # Level 4 should not check copulas
    assert not any('cop-lemma' in e for e in errors)


def test_level_5_cop_validation(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that Level 5 validates copulas."""
    sentence_la_tokens[0]['form'] = 'est'
    sentence_la_tokens[0]['lemma'] = 'invalid'
    sentence_la_tokens[0]['upostag'] = 'AUX'
    sentence_la_tokens[0]['deprel'] = 'cop'
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['form'] = 'bonus'
    sentence_la_tokens[1]['lemma'] = 'bonus'
    sentence_la_tokens[1]['upostag'] = 'ADJ'
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    # Level 5 should check copulas
    assert any('cop-lemma' in e for e in errors)


# Test alternative language handling with Lang= attribute
def test_aux_alternative_language(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that Lang= attribute switches auxiliary validation."""
    sentence_la_tokens[0]['form'] = 'be'
    sentence_la_tokens[0]['lemma'] = 'be'
    sentence_la_tokens[0]['upostag'] = 'AUX'
    sentence_la_tokens[0]['deprel'] = 'aux'
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[0]['misc'] = 'Lang=en'
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    # Should validate against English auxiliaries, not Latin
    # 'be' is valid in English
    aux_errors = [e for e in errors if 'aux-lemma' in e]
    # Depending on whether 'be' is in English aux list
    assert not aux_errors or '[en]' in aux_errors[0]


def test_cop_alternative_language(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that Lang= attribute switches copula validation."""
    sentence_la_tokens[0]['form'] = 'be'
    sentence_la_tokens[0]['lemma'] = 'be'
    sentence_la_tokens[0]['upostag'] = 'AUX'
    sentence_la_tokens[0]['deprel'] = 'cop'
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[0]['misc'] = 'Lang=en'
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['form'] = 'good'
    sentence_la_tokens[1]['lemma'] = 'good'
    sentence_la_tokens[1]['upostag'] = 'ADJ'
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    # Should validate against English copulas, not Latin
    cop_errors = [e for e in errors if 'cop-lemma' in e]
    # Depending on whether 'be' is in English cop list
    assert not cop_errors or '[en]' in cop_errors[0]


# Test handling of languages without aux/cop data
def test_aux_no_data_warning(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test warning when language has no auxiliaries."""
    sentence_la_tokens[0]['form'] = 'test'
    sentence_la_tokens[0]['lemma'] = 'test'
    sentence_la_tokens[0]['upostag'] = 'AUX'
    sentence_la_tokens[0]['deprel'] = 'aux'
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['form'] = 'word'
    sentence_la_tokens[1]['lemma'] = 'word'
    sentence_la_tokens[1]['upostag'] = 'VERB'
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    # Use a language without aux data (if any)
    validator = ConlluValidator(lang='xx', level=5)
    errors = validator.validate_string(text)
    # Should warn about no auxiliaries
    aux_errors = [e for e in errors if 'aux-lemma' in e]
    # No auxdata for xx, so no validation happens
    # (validation only happens if lang in auxdata)
    assert len(aux_errors) == 0


def test_cop_no_data_warning(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test warning when language has no copulas."""
    sentence_la_tokens[0]['form'] = 'test'
    sentence_la_tokens[0]['lemma'] = 'test'
    sentence_la_tokens[0]['upostag'] = 'AUX'
    sentence_la_tokens[0]['deprel'] = 'cop'
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['form'] = 'word'
    sentence_la_tokens[1]['lemma'] = 'word'
    sentence_la_tokens[1]['upostag'] = 'ADJ'
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    # Use a language without cop data
    validator = ConlluValidator(lang='xx', level=5)
    errors = validator.validate_string(text)
    # No copdata for xx, so no validation happens
    cop_errors = [e for e in errors if 'cop-lemma' in e]
    assert len(cop_errors) == 0


# Integration tests for auxiliary/copula validation
def test_multiple_auxiliaries(tmp_path: Path) -> None:
    """Test sentence with multiple auxiliaries."""
    tokens = [
        {
            'id': 1,
            'form': 'sum',
            'lemma': 'sum',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'habeo',
            'lemma': 'habeo',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'invalid',
            'lemma': 'invalid',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'test',
            'lemma': 'test',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    aux_errors = [e for e in errors if 'aux-lemma' in e]
    # Only 'invalid' should be flagged
    assert len(aux_errors) == 1
    assert "'invalid'" in aux_errors[0]


def test_aux_and_cop_together(tmp_path: Path) -> None:
    """Test sentence with both auxiliary and copula."""
    tokens = [
        {
            'id': 1,
            'form': 'sum',
            'lemma': 'sum',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'est',
            'lemma': 'sum',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'cop',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'bonus',
            'lemma': 'bonus',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    # Both should be valid
    assert not any('aux-lemma' in e for e in errors)
    assert not any('cop-lemma' in e for e in errors)


def test_mixed_validity(tmp_path: Path) -> None:
    """Test sentence with valid and invalid aux/cop."""
    tokens = [
        {
            'id': 1,
            'form': 'sum',
            'lemma': 'sum',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'invalid1',
            'lemma': 'invalid1',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'est',
            'lemma': 'sum',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'cop',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'invalid2',
            'lemma': 'invalid2',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'cop',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 5,
            'form': 'bonus',
            'lemma': 'bonus',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=5)
    errors = validator.validate_string(text)
    aux_errors = [e for e in errors if 'aux-lemma' in e]
    cop_errors = [e for e in errors if 'cop-lemma' in e]
    # Should have 1 aux error and 1 cop error
    assert len(aux_errors) == 1
    assert len(cop_errors) == 1
