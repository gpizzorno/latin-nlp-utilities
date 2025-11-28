"""Test single subject validation."""

from pathlib import Path

from conllu_tools.validation.validator import ConlluValidator
from tests.factories import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_contains, assert_error_count, assert_no_errors_of_type


def test_valid_single_subject(tmp_path: Path) -> None:
    """Test that a predicate with one subject is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'cat',
            'lemma': 'cat',
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
            'form': 'runs',
            'lemma': 'runs',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='cat runs')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'too-many-subjects')


def test_valid_two_subjects(tmp_path: Path) -> None:
    """Test that a predicate with two subjects is valid (special case)."""
    tokens = [
        {
            'id': 1,
            'form': 'he',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'thinks',
            'lemma': 'thinks',
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
            'form': 'cat',
            'lemma': 'cat',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'runs',
            'lemma': 'runs',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'csubj',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='he thinks cat runs')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'too-many-subjects')


def test_invalid_three_subjects(tmp_path: Path) -> None:
    """Test that a predicate with three subjects is invalid."""
    tokens = [
        {
            'id': 1,
            'form': 'cat',
            'lemma': 'cat',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'dog',
            'lemma': 'dog',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'bird',
            'lemma': 'bird',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'run',
            'lemma': 'run',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='cat dog bird run')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_error_count(errors, 1, 'too-many-subjects')
    assert_error_contains(errors, 'too-many-subjects', '[1, 2, 3]')


def test_csubj_counted_as_subject(tmp_path: Path) -> None:
    """Test that csubj is counted as a subject."""
    tokens = [
        {
            'id': 1,
            'form': 'he',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'knows',
            'lemma': 'knows',
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
            'form': 'cat',
            'lemma': 'cat',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'runs',
            'lemma': 'runs',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'csubj',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='he knows cat runs')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    # Should not have too-many-subjects error (nsubj + csubj = 2)
    assert_no_errors_of_type(errors, 'too-many-subjects')
