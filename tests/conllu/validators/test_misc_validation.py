"""Tests for MISC column validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


def test_valid_misc_spaceafter(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that valid SpaceAfter=No is accepted."""
    sentence_en_tokens[0]['misc'] = 'SpaceAfter=No'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    misc_errors = [e for e in errors if 'invalid-spaceafter-value' in e]
    assert len(misc_errors) == 0


def test_invalid_misc_spaceafter_yes(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that SpaceAfter=Yes is rejected."""
    sentence_en_tokens[0]['misc'] = 'SpaceAfter=Yes'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    misc_errors = [e for e in errors if 'invalid-spaceafter-value' in e]
    assert len(misc_errors) == 1
    assert 'Yes' in misc_errors[0]


def test_invalid_misc_spaceafter_wrong_value(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that SpaceAfter with wrong value is rejected."""
    sentence_en_tokens[0]['misc'] = 'SpaceAfter=False'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    misc_errors = [e for e in errors if 'invalid-spaceafter-value' in e]
    assert len(misc_errors) == 1
    assert 'False' in misc_errors[0]


def test_valid_misc_multiple_attributes(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that multiple valid MISC attributes are accepted."""
    sentence_en_tokens[0]['misc'] = 'SpaceAfter=No|Gloss=test|Translit=test'
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=sentence_en_tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    misc_errors = [e for e in errors if 'invalid-spaceafter-value' in e]
    assert len(misc_errors) == 0


def test_misc_underscore(tmp_path: Path) -> None:
    """Test that MISC with underscore is accepted."""
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    misc_errors = [e for e in errors if 'invalid-spaceafter-value' in e]
    assert len(misc_errors) == 0


def test_misc_empty_node(tmp_path: Path, sentence_en_tokens: list[dict[str, str | int]]) -> None:
    """Test that MISC validation works with empty nodes."""
    sentence_en_tokens[0]['misc'] = 'SpaceAfter=No'
    # Add empty node
    empty_node = {
        'id': '1.1',
        'form': '_',
        'lemma': '_',
        'upostag': '_',
        'xpostag': '_',
        'feats': '_',
        'head': '_',
        'deprel': '_',
        'deps': '_',
        'misc': 'Gloss=test',
    }
    tokens_with_empty = [sentence_en_tokens[0], empty_node, *sentence_en_tokens[1:]]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens_with_empty)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    misc_errors = [e for e in errors if 'invalid-spaceafter-value' in e]
    assert len(misc_errors) == 0


def test_misc_multiword_token(tmp_path: Path) -> None:
    """Test that MISC validation skips multiword tokens."""
    tokens = [
        {
            'id': '1-2',
            'form': 'del',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': 'SpaceAfter=Yes',
        },
        {
            'id': 1,
            'form': 'de',
            'lemma': 'de',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'el',
            'lemma': 'el',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'mundo',
            'lemma': 'mundo',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='es', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    misc_errors = [e for e in errors if 'invalid-spaceafter-value' in e]
    # MWT should be skipped, so no error about SpaceAfter=Yes
    assert len(misc_errors) == 0
