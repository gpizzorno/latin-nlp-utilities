"""Tests for multiword token validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


def test_valid_multiword_token(tmp_path: Path) -> None:
    """Test that a properly formatted multiword token passes validation."""
    tokens = [
        {
            'id': '1-2',
            'form': "He'll",
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
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': "'ll",
            'lemma': 'will',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'come',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    mwt_errors = [e for e in errors if 'mwt-nonempty' in e or 'overlapping-mwt' in e]
    assert len(mwt_errors) == 0


def test_multiword_token_with_lemma(tmp_path: Path) -> None:
    """Test that multiword token with LEMMA value generates error."""
    tokens = [
        {
            'id': '1-2',
            'form': "He'll",
            'lemma': "he'll",
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
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': "'ll",
            'lemma': 'will',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'come',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    lemma_errors = [e for e in errors if 'mwt-nonempty-lemma' in e or 'must have _ in LEMMA' in e]
    assert len(lemma_errors) == 1


def test_multiword_token_with_upos(tmp_path: Path) -> None:
    """Test that multiword token with UPOS value generates error."""
    tokens = [
        {
            'id': '1-2',
            'form': "He'll",
            'lemma': '_',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': "'ll",
            'lemma': 'will',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'come',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    upos_errors = [e for e in errors if 'mwt-nonempty-upos' in e or 'must have _ in UPOS' in e]
    assert len(upos_errors) == 1


def test_multiword_token_with_head(tmp_path: Path) -> None:
    """Test that multiword token with HEAD value generates error."""
    tokens = [
        {
            'id': '1-2',
            'form': "He'll",
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': "'ll",
            'lemma': 'will',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'come',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    head_errors = [e for e in errors if 'mwt-nonempty-head' in e or 'must have _ in HEAD' in e]
    assert len(head_errors) == 1


def test_multiword_token_with_deprel(tmp_path: Path) -> None:
    """Test that multiword token with DEPREL value generates error."""
    tokens = [
        {
            'id': '1-2',
            'form': "He'll",
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': "'ll",
            'lemma': 'will',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'come',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    deprel_errors = [e for e in errors if 'mwt-nonempty-deprel' in e or 'must have _ in DEPREL' in e]
    assert len(deprel_errors) == 1


def test_multiword_token_reversed_range(tmp_path: Path) -> None:
    """Test that multiword token with reversed range (end < start) generates error."""
    tokens = [
        {
            'id': '2-1',
            'form': "He'll",
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
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': "'ll",
            'lemma': 'will',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'come',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    # The conllu library catches this during parsing and raises a ParseException
    # which is reported as a parse-error
    assert len(errors) == 1
    assert 'parse-error' in errors[0] or 'not a valid ID' in errors[0]


def test_overlapping_multiword_tokens(tmp_path: Path) -> None:
    """Test that overlapping multiword token ranges generate error."""
    tokens = [
        {
            'id': '1-2',
            'form': 'test1',
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
            'form': 'test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'overlapping',
            'lemma': 'overlap',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'acl',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': '2-3',
            'form': 'test2',
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
            'id': 3,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    overlap_errors = [e for e in errors if 'overlapping-mwt' in e or 'overlaps with other ranges' in e]
    assert len(overlap_errors) == 1


def test_multiword_token_invalid_word_reference(tmp_path: Path) -> None:
    """Test that multiword token referencing non-existent word generates error."""
    tokens = [
        {
            'id': '1-3',
            'form': 'Test',
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
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=1)
    errors = validator.validate_string(text)
    invalid_errors = [e for e in errors if 'mwt-invalid-range' in e or 'non-existent word ID' in e]
    assert len(invalid_errors) == 1


def test_multiword_token_with_misc(tmp_path: Path) -> None:
    """Test that multiword token with MISC content is allowed."""
    tokens = [
        {
            'id': '1-2',
            'form': "He'll",
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': 'SpaceAfter=No',
        },
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': "'ll",
            'lemma': 'will',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'come',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    # MISC can have content for multiword tokens
    nonempty_errors = [e for e in errors if 'mwt-nonempty-lemma' in e or 'mwt-nonempty-upos' in e]
    assert len(nonempty_errors) == 0


def test_multiple_multiword_tokens_valid(tmp_path: Path) -> None:
    """Test multiple non-overlapping multiword tokens."""
    tokens = [
        {
            'id': '1-2',
            'form': "He'll",
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
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': "'ll",
            'lemma': 'will',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'go',
            'lemma': 'go',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': ',',
            'lemma': ',',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 6,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': '5-6',
            'form': "they'll",
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
            'id': 5,
            'form': 'they',
            'lemma': 'they',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 7,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 6,
            'form': "'ll",
            'lemma': 'will',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 7,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 7,
            'form': 'stay',
            'lemma': 'stay',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'conj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 8,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    mwt_errors = [e for e in errors if 'overlapping-mwt' in e or 'mwt-invalid-range' in e]
    assert len(mwt_errors) == 0
