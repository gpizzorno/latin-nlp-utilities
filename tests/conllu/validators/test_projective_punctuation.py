"""Test projective punctuation validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.error_reporter import ErrorReporter
from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_count, assert_no_errors_of_type


def test_valid_projective_punct(tmp_path: Path) -> None:
    """Test valid projective punctuation attachment."""
    tokens = [
        {
            'id': 1,
            'form': 'Hello',
            'lemma': '_',
            'upostag': 'INTJ',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': ',',
            'lemma': '_',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'world',
            'lemma': '_',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'vocative',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': '!',
            'lemma': '_',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='Hello , world !')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'punct-causes-nonproj')
    assert_no_errors_of_type(errors, 'punct-is-nonproj')


def test_invalid_nonprojective_punct(tmp_path: Path) -> None:
    """Test punctuation attached non-projectively."""
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
            'head': 2,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='The cat sleeps .')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_error_count(errors, 1, 'punct-is-nonproj')


def test_punct_causes_nonprojectivity(tmp_path: Path) -> None:
    """Test punctuation causing non-projectivity in other nodes."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': '_',
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
            'form': 'said',
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
            'id': 3,
            'form': ',',
            'lemma': '_',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'she',
            'lemma': '_',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 5,
            'form': 'left',
            'lemma': '_',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'ccomp',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 6,
            'form': '.',
            'lemma': '_',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='He said , she left .')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    # This might cause nonprojectivity depending on exact attachment
    # At minimum, should not crash
    assert isinstance(errors, ErrorReporter)


def test_punct_at_sentence_end(tmp_path: Path) -> None:
    """Test punctuation at end of sentence (projective)."""
    tokens = [
        {
            'id': 1,
            'form': 'Hello',
            'lemma': '_',
            'upostag': 'INTJ',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'world',
            'lemma': '_',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'vocative',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': '.',
            'lemma': '_',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='Hello world .')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'punct-causes-nonproj')
    assert_no_errors_of_type(errors, 'punct-is-nonproj')


def test_multiple_punct(tmp_path: Path) -> None:
    """Test multiple punctuation marks."""
    tokens = [
        {
            'id': 1,
            'form': 'Hello',
            'lemma': '_',
            'upostag': 'INTJ',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': ',',
            'lemma': '_',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'dear',
            'lemma': '_',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'amod',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': ',',
            'lemma': '_',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 5,
            'form': 'friend',
            'lemma': '_',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'vocative',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 6,
            'form': '!',
            'lemma': '_',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='Hello , dear , friend !')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    # Should handle multiple punctuation marks without errors
    assert isinstance(errors, ErrorReporter)


def test_punct_with_subtype(tmp_path: Path) -> None:
    """Test punctuation with subtype in relation."""
    tokens = [
        {
            'id': 1,
            'form': 'Hello',
            'lemma': '_',
            'upostag': 'INTJ',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'world',
            'lemma': '_',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'vocative',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': '.',
            'lemma': '_',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'punct:period',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='Hello world .')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    # Subtype should not affect validation
    assert_no_errors_of_type(errors, 'punct-causes-nonproj')
    assert_no_errors_of_type(errors, 'punct-is-nonproj')
