"""Tests for DEPREL validation (#14 DEPREL Validation Enhancement)."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


# Test basic DEPREL validation at Level 4
def test_valid_universal_deprel(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test valid universal DEPREL."""
    sentence_la_tokens[0]['head'] = 0
    sentence_la_tokens[0]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:1])
    validator = ConlluValidator(level=4, lang='la')
    errors = validator.validate_string(text)
    # Should not report DEPREL errors for valid universal relation
    assert not any('deprel' in err.lower() for err in errors)


def test_valid_latin_subtype(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test valid Latin-specific DEPREL subtype."""
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[0]['deprel'] = 'nsubj'
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['upostag'] = 'VERB'
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    sentence_la_tokens[2]['id'] = 3
    sentence_la_tokens[2]['form'] = 'absolute'
    sentence_la_tokens[2]['lemma'] = 'absolute'
    sentence_la_tokens[2]['upostag'] = 'ADJ'
    sentence_la_tokens[2]['head'] = 2
    sentence_la_tokens[2]['deprel'] = 'advcl:abs'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:3])
    validator = ConlluValidator(level=4, lang='la')
    errors = validator.validate_string(text)
    # advcl:abs is a valid Latin subtype
    error_str = '\n'.join(errors)
    assert 'unknown-deprel' not in error_str


def test_unknown_deprel(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test unknown DEPREL."""
    sentence_la_tokens[0]['head'] = 0
    sentence_la_tokens[0]['deprel'] = 'fakedeprel'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:1])
    validator = ConlluValidator(level=4, lang='la')
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    assert 'unknown-deprel' in error_str
    assert 'fakedeprel' in error_str


def test_unknown_deprel_subtype(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test unknown DEPREL subtype."""
    sentence_la_tokens[0]['head'] = 0
    sentence_la_tokens[0]['deprel'] = 'nmod:fakesubtype'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:1])
    validator = ConlluValidator(level=4, lang='la')
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    # Should report unknown subtype (base nmod exists, but nmod:fakesubtype doesn't)
    assert 'unknown-deprel' in error_str or 'subtype' in error_str.lower()


def test_deprel_not_permitted(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test DEPREL with permitted=0."""
    # Find a relation in deprels.json for Latin that has permitted=0
    # For example, acl:appos has permitted=0 for Latin
    sentence_la_tokens[0]['head'] = 2
    sentence_la_tokens[0]['deprel'] = 'acl:appos'
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['head'] = 0
    sentence_la_tokens[1]['deprel'] = 'root'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    validator = ConlluValidator(level=4, lang='la')
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    # Should report that acl:appos is not permitted
    assert 'deprel-not-permitted' in error_str or 'not permitted' in error_str.lower()


# Test difference between Level 2 and Level 4 DEPREL validation
def test_level_2_no_subtype_check(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that Level 2 doesn't check subtypes."""
    sentence_la_tokens[0]['head'] = 0
    sentence_la_tokens[0]['deprel'] = 'nmod:fakesubtype'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:1])
    validator = ConlluValidator(level=2, lang='la')
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    # At Level 2, should not report unknown subtype
    assert 'unknown-deprel' not in error_str


def test_level_4_checks_subtypes(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that Level 4 checks subtypes."""
    sentence_la_tokens[0]['head'] = 0
    sentence_la_tokens[0]['deprel'] = 'nmod:fakesubtype'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:1])
    validator = ConlluValidator(level=4, lang='la')
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    # At Level 4, should report unknown subtype
    assert 'unknown-deprel' in error_str or 'subtype' in error_str.lower()


# Test various valid Latin DEPREL subtypes
def test_valid_advcl_subtypes(tmp_path: Path) -> None:
    """Test valid advcl subtypes for Latin."""
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'sentence',
            'lemma': 'sentence',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'abs',
            'lemma': 'abs',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'advcl:abs',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'cmpr',
            'lemma': 'cmpr',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'advcl:cmpr',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 5,
            'form': 'pred',
            'lemma': 'pred',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'advcl:pred',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=4, lang='la')
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    # These are all valid Latin subtypes
    assert 'unknown-deprel' not in error_str


def test_valid_advmod_subtypes(tmp_path: Path) -> None:
    """Test valid advmod subtypes for Latin."""
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'sentence',
            'lemma': 'sentence',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'emph',
            'lemma': 'emph',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'advmod:emph',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'lmod',
            'lemma': 'lmod',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'advmod:lmod',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 5,
            'form': 'neg',
            'lemma': 'neg',
            'upostag': 'PART',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'advmod:neg',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 6,
            'form': 'tmod',
            'lemma': 'tmod',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'advmod:tmod',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=4, lang='la')
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    # These are all valid Latin subtypes
    assert 'unknown-deprel' not in error_str


def test_valid_aux_pass_subtype(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test valid aux:pass subtype."""
    sentence_la_tokens[0]['upostag'] = 'VERB'
    sentence_la_tokens[0]['head'] = 0
    sentence_la_tokens[0]['deprel'] = 'root'
    sentence_la_tokens[1]['id'] = 2
    sentence_la_tokens[1]['form'] = 'be'
    sentence_la_tokens[1]['lemma'] = 'be'
    sentence_la_tokens[1]['upostag'] = 'AUX'
    sentence_la_tokens[1]['head'] = 1
    sentence_la_tokens[1]['deprel'] = 'aux:pass'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:2])
    validator = ConlluValidator(level=4, lang='la')
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    # aux:pass is a valid universal subtype
    assert 'unknown-deprel' not in error_str


# Integration tests for DEPREL validation
def test_multiple_tokens_with_subtypes(tmp_path: Path) -> None:
    """Test validation across multiple tokens with different subtypes."""
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'sentence',
            'lemma': 'sentence',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'valid',
            'lemma': 'valid',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'advcl:abs',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'invalid',
            'lemma': 'invalid',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'advcl:fakesubtype',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=4, lang='la')
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    # Should report error for token 4 but not token 3
    assert 'unknown-deprel' in error_str or 'subtype' in error_str.lower()
    # Error should reference the invalid subtype
    assert 'fakesubtype' in error_str


def test_skip_multiword_tokens(tmp_path: Path) -> None:
    """Test that multiword tokens are skipped in DEPREL validation."""
    tokens = [
        {
            'id': '1-2',
            'form': 'cannot',
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
            'form': 'can',
            'lemma': 'can',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'not',
            'lemma': 'not',
            'upostag': 'PART',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'advmod:neg',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=4, lang='la')
    errors = validator.validate_string(text)
    # Should not crash or report errors for MWT range (1-2)
    error_str = '\n'.join(errors)
    # Valid Latin subtype advmod:neg should not trigger errors
    assert 'unknown-deprel' not in error_str


def test_empty_deprel(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test handling of empty DEPREL column."""
    # This is actually invalid CoNLL-U but we test graceful handling
    sentence_la_tokens[0]['head'] = 0
    sentence_la_tokens[0]['deprel'] = '_'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:1])
    validator = ConlluValidator(level=4, lang='la')
    _ = validator.validate_string(text)
    # Should not crash, but may report other errors


def test_universal_deprels_always_valid(tmp_path: Path) -> None:
    """Test that universal DEPRELs are valid in any language."""
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'sentence',
            'lemma': 'sentence',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'with',
            'lemma': 'with',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'multiple',
            'lemma': 'multiple',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'amod',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 5,
            'form': 'relations',
            'lemma': 'relation',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'obl',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=4, lang='la')
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    # All universal relations should be valid
    assert 'unknown-deprel' not in error_str


def test_base_deprel_exists_message(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that error message mentions base relation when it exists."""
    sentence_la_tokens[0]['head'] = 0
    sentence_la_tokens[0]['deprel'] = 'nmod:invalidsubtype'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:1])
    validator = ConlluValidator(level=4, lang='la')
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    # Should mention that base relation exists
    assert 'nmod' in error_str or 'base' in error_str.lower() or 'subtype' in error_str.lower()


def test_completely_unknown_deprel(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test error message for completely unknown DEPREL."""
    sentence_la_tokens[0]['head'] = 0
    sentence_la_tokens[0]['deprel'] = 'totallyfake'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:1])
    validator = ConlluValidator(level=4, lang='la')
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    # Should report as unknown
    assert 'unknown-deprel' in error_str
    assert 'totallyfake' in error_str


def test_extract_base_deprel(tmp_path: Path, sentence_la_tokens: list[dict[str, str | int]]) -> None:
    """Test that base DEPREL is correctly extracted from subtypes."""
    # This is more of an implementation detail test
    # We test it indirectly by checking error messages
    sentence_la_tokens[0]['head'] = 0
    sentence_la_tokens[0]['deprel'] = 'obl:fake:extra'
    text = ConlluSentenceFactory.as_text(lang='la', tmp_path=tmp_path, tokens=sentence_la_tokens[:1])
    validator = ConlluValidator(level=4, lang='la')
    errors = validator.validate_string(text)
    error_str = '\n'.join(errors)
    # Should handle complex subtypes (obl:fake:extra -> obl)
    assert 'unknown-deprel' in error_str or 'subtype' in error_str.lower()
