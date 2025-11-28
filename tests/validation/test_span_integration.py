"""Test integration of span validations."""

from pathlib import Path

from conllu_tools.validation.validator import ConlluValidator
from tests.factories import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_count, assert_no_errors_of_type


def test_multiple_span_issues(tmp_path: Path) -> None:
    """Test sentence with multiple span validation issues."""
    tokens = [
        {
            'id': 1,
            'form': 'so',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': 'SpaceAfter=No',
        },
        {
            'id': 2,
            'form': 'me',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'other',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'thing',
            'lemma': '_',
            'upostag': 'ADV',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'goeswith',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='something')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    # Should detect both goeswith issues
    assert_error_count(errors, 1, 'goeswith-nospace')
    assert_error_count(errors, 1, 'goeswith-gap')


def test_no_span_issues(tmp_path: Path) -> None:
    """Test sentence with no span validation issues."""
    tokens = [
        {
            'id': 1,
            'form': 'The',
            'lemma': '_',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'cat',
            'lemma': '_',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'sleeps',
            'lemma': '_',
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
            'lemma': '_',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='The cat sleeps .')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'goeswith-gap')
    assert_no_errors_of_type(errors, 'goeswith-nospace')
    assert_no_errors_of_type(errors, 'fixed-gap')
    assert_no_errors_of_type(errors, 'punct-causes-nonproj')
    assert_no_errors_of_type(errors, 'punct-is-nonproj')
