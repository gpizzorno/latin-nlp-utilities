"""Tests for UPOS-DEPREL compatibility validation."""

from __future__ import annotations

from typing import Any

import pytest

from conllu_tools.validation.validator import ConlluValidator
from tests.factories import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_contains, assert_error_count, assert_no_errors_of_type


def test_det_with_det_upos_valid(validator_level_3: ConlluValidator, root_token: dict[str, Any]) -> None:
    """Test that det deprel with DET UPOS is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'the',
            'lemma': 'the',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-det')


def test_det_with_pron_upos_valid(validator_level_3: ConlluValidator, root_token: dict[str, Any]) -> None:
    """Test that det deprel with PRON UPOS is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'this',
            'lemma': 'this',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-det')


@pytest.mark.parametrize(
    'upostag',
    ['NOUN', 'VERB', 'ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'INTJ', 'NUM', 'PART', 'PROPN', 'SCONJ', 'SYM', 'X'],
)
def test_det_with_invalid_upos(validator_level_3: ConlluValidator, upostag: str, root_token: dict[str, Any]) -> None:
    """Test that det deprel with non-DET/PRON UPOS triggers error."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_error_contains(errors, 'rel-upos-det', "should be 'DET' or 'PRON'")
    assert_error_contains(errors, 'rel-upos-det', upostag)


def test_det_with_punct_upos_invalid(validator_level_3: ConlluValidator, root_token: dict[str, Any]) -> None:
    """Test that det deprel with PUNCT UPOS triggers error."""
    tokens = [
        {
            'id': 1,
            'form': ',',
            'lemma': ',',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_error_contains(errors, 'rel-upos-det', "should be 'DET' or 'PRON'")


def test_aux_with_aux_upos_valid(validator_level_3: ConlluValidator, root_token: dict[str, Any]) -> None:
    """Test that aux deprel with AUX UPOS is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'has',
            'lemma': 'have',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-aux')


@pytest.mark.parametrize(
    'upostag',
    [
        'NOUN',
        'VERB',
        'ADJ',
        'ADP',
        'ADV',
        'DET',
        'PRON',
        'CCONJ',
        'INTJ',
        'NUM',
        'PART',
        'PROPN',
        'PUNCT',
        'SCONJ',
        'SYM',
        'X',
    ],
)
def test_aux_with_invalid_upos(validator_level_3: ConlluValidator, upostag: str, root_token: dict[str, Any]) -> None:
    """Test that aux deprel with non-AUX UPOS triggers error."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_error_contains(errors, 'rel-upos-aux', "should be 'AUX'")
    assert_error_contains(errors, 'rel-upos-aux', upostag)


def test_punct_with_punct_upos_valid(validator_level_3: ConlluValidator, root_token: dict[str, Any]) -> None:
    """Test that punct deprel with PUNCT UPOS is valid."""
    tokens = [
        {
            'id': 1,
            'form': ',',
            'lemma': ',',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-punct')


@pytest.mark.parametrize(
    'upostag',
    [
        'NOUN',
        'VERB',
        'ADJ',
        'ADP',
        'ADV',
        'AUX',
        'CCONJ',
        'DET',
        'INTJ',
        'NUM',
        'PART',
        'PRON',
        'PROPN',
        'SCONJ',
        'SYM',
        'X',
    ],
)
def test_punct_with_invalid_upos(validator_level_3: ConlluValidator, upostag: str, root_token: dict[str, Any]) -> None:
    """Test that punct deprel with non-PUNCT UPOS triggers error (strict)."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_error_contains(errors, 'rel-upos-punct', "must be 'PUNCT'")
    assert_error_contains(errors, 'rel-upos-punct', upostag)


@pytest.mark.parametrize('upostag', ['NUM', 'NOUN', 'SYM'])
def test_nummod_with_valid_upos(validator_level_3: ConlluValidator, upostag: str, root_token: dict[str, Any]) -> None:
    """Test that nummod deprel with NUM/NOUN/SYM UPOS is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'three',
            'lemma': 'three',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nummod',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-nummod')


@pytest.mark.parametrize(
    'upostag',
    ['VERB', 'ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 'INTJ', 'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'X'],
)
def test_nummod_with_invalid_upos(validator_level_3: ConlluValidator, upostag: str, root_token: dict[str, Any]) -> None:
    """Test that nummod deprel with non-NUM/NOUN/SYM UPOS triggers error."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nummod',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_error_contains(errors, 'rel-upos-nummod', "should be 'NUM'")
    assert_error_contains(errors, 'rel-upos-nummod', upostag)


@pytest.mark.parametrize('upostag', ['ADV', 'ADJ', 'CCONJ', 'DET', 'PART', 'SYM'])
def test_advmod_with_valid_upos(validator_level_3: ConlluValidator, upostag: str, root_token: dict[str, Any]) -> None:
    """Test that advmod deprel with ADV/ADJ/CCONJ/DET/PART/SYM UPOS is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'quickly',
            'lemma': 'quickly',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'advmod',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-advmod')


@pytest.mark.parametrize('upostag', ['NOUN', 'PROPN', 'VERB', 'AUX'])
def test_advmod_with_invalid_upos_no_children(
    validator_level_3: ConlluValidator,
    upostag: str,
    root_token: dict[str, Any],
) -> None:
    """Test that advmod deprel with non-allowed UPOS triggers error without fixed/goeswith child."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'advmod',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_error_contains(errors, 'rel-upos-advmod', "should be 'ADV'")


@pytest.mark.parametrize('child_deprel', ['fixed', 'goeswith'])
@pytest.mark.parametrize('upostag', ['NOUN', 'PROPN'])
def test_advmod_with_invalid_upos_but_fixed_child_valid(
    validator_level_3: ConlluValidator,
    upostag: str,
    child_deprel: str,
    root_token: dict[str, Any],
) -> None:
    """Test that advmod deprel with non-allowed UPOS is valid when it has fixed/goeswith child."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'advmod',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'child',
            'lemma': 'child',
            'upostag': 'X',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': child_deprel,
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    root_token['id'] = 3
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-advmod')


def test_advmod_with_invalid_upos_other_child_still_invalid(
    validator_level_3: ConlluValidator,
    root_token: dict[str, Any],
) -> None:
    """Test that advmod deprel with non-allowed UPOS is still invalid with non-fixed child."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'advmod',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'child',
            'lemma': 'child',
            'upostag': 'X',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'compound',  # Not fixed or goeswith
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    root_token['id'] = 3
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_error_contains(errors, 'rel-upos-advmod', "should be 'ADV'")


@pytest.mark.parametrize('upostag', ['PRON', 'DET', 'PART'])
def test_expl_with_valid_upos(validator_level_3: ConlluValidator, upostag: str, root_token: dict[str, Any]) -> None:
    """Test that expl deprel with PRON/DET/PART UPOS is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'it',
            'lemma': 'it',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'expl',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-expl')


@pytest.mark.parametrize(
    'upostag',
    ['NOUN', 'VERB', 'ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'INTJ', 'NUM', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'X'],
)
def test_expl_with_invalid_upos(validator_level_3: ConlluValidator, upostag: str, root_token: dict[str, Any]) -> None:
    """Test that expl deprel with non-PRON/DET/PART UPOS triggers error."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'expl',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_error_contains(errors, 'rel-upos-expl', "should normally be 'PRON'")


@pytest.mark.parametrize('upostag', ['AUX', 'PRON', 'DET', 'SYM'])
def test_cop_with_valid_upos(validator_level_3: ConlluValidator, upostag: str, root_token: dict[str, Any]) -> None:
    """Test that cop deprel with AUX/PRON/DET/SYM UPOS is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'is',
            'lemma': 'be',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'cop',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-cop')


@pytest.mark.parametrize(
    'upostag',
    ['NOUN', 'VERB', 'ADJ', 'ADP', 'ADV', 'CCONJ', 'INTJ', 'NUM', 'PART', 'PROPN', 'PUNCT', 'SCONJ', 'X'],
)
def test_cop_with_invalid_upos(validator_level_3: ConlluValidator, upostag: str, root_token: dict[str, Any]) -> None:
    """Test that cop deprel with non-AUX/PRON/DET/SYM UPOS triggers error."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'cop',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_error_contains(errors, 'rel-upos-cop', "should be 'AUX'")


@pytest.mark.parametrize('upostag', ['ADP', 'ADV', 'SCONJ', 'VERB'])
def test_case_with_valid_upos(validator_level_3: ConlluValidator, upostag: str, root_token: dict[str, Any]) -> None:
    """Test that case deprel with allowed UPOS is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'in',
            'lemma': 'in',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-case')


@pytest.mark.parametrize('upostag', ['PROPN', 'ADJ', 'PRON', 'DET', 'NUM', 'AUX'])
def test_case_with_invalid_upos_no_children(
    validator_level_3: ConlluValidator,
    upostag: str,
    root_token: dict[str, Any],
) -> None:
    """Test that case deprel with disallowed UPOS triggers error without fixed child."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_error_contains(errors, 'rel-upos-case', 'should not be')
    assert_error_contains(errors, 'rel-upos-case', upostag)


@pytest.mark.parametrize('upostag', ['PROPN', 'ADJ', 'PRON', 'DET', 'NUM', 'AUX'])
def test_case_with_invalid_upos_but_fixed_child_valid(
    validator_level_3: ConlluValidator,
    upostag: str,
    root_token: dict[str, Any],
) -> None:
    """Test that case deprel with disallowed UPOS is valid when it has fixed child."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'child',
            'lemma': 'child',
            'upostag': 'X',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    root_token['id'] = 3
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-case')


@pytest.mark.parametrize('upostag', ['SCONJ', 'ADP', 'ADV', 'PART'])
def test_mark_with_valid_upos(validator_level_3: ConlluValidator, upostag: str, root_token: dict[str, Any]) -> None:
    """Test that mark deprel with allowed UPOS is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'that',
            'lemma': 'that',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'mark',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-mark')


@pytest.mark.parametrize('upostag', ['NOUN', 'PROPN', 'ADJ', 'PRON', 'DET', 'NUM', 'VERB', 'AUX', 'INTJ'])
def test_mark_with_invalid_upos_no_children(
    validator_level_3: ConlluValidator,
    upostag: str,
    root_token: dict[str, Any],
) -> None:
    """Test that mark deprel with disallowed UPOS triggers error without fixed child."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'mark',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_error_contains(errors, 'rel-upos-mark', 'should not be')
    assert_error_contains(errors, 'rel-upos-mark', upostag)


@pytest.mark.parametrize('upostag', ['NOUN', 'PROPN', 'ADJ', 'PRON', 'DET', 'NUM', 'VERB', 'AUX', 'INTJ'])
def test_mark_with_invalid_upos_but_fixed_child_valid(
    validator_level_3: ConlluValidator,
    upostag: str,
    root_token: dict[str, Any],
) -> None:
    """Test that mark deprel with disallowed UPOS is valid when it has fixed child."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'mark',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'child',
            'lemma': 'child',
            'upostag': 'X',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    root_token['id'] = 3
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-mark')


@pytest.mark.parametrize('upostag', ['CCONJ', 'ADV', 'PART', 'ADP', 'SCONJ', 'SYM'])
def test_cc_with_valid_upos(validator_level_3: ConlluValidator, upostag: str, root_token: dict[str, Any]) -> None:
    """Test that cc deprel with allowed UPOS is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'and',
            'lemma': 'and',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'cc',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-cc')


@pytest.mark.parametrize('upostag', ['NOUN', 'PROPN', 'ADJ', 'PRON', 'DET', 'NUM', 'VERB', 'AUX', 'INTJ'])
def test_cc_with_invalid_upos_no_children(
    validator_level_3: ConlluValidator,
    upostag: str,
    root_token: dict[str, Any],
) -> None:
    """Test that cc deprel with disallowed UPOS triggers error without fixed child."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'cc',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_error_contains(errors, 'rel-upos-cc', 'should not be')
    assert_error_contains(errors, 'rel-upos-cc', upostag)


@pytest.mark.parametrize('upostag', ['NOUN', 'PROPN', 'ADJ', 'PRON', 'DET', 'NUM', 'VERB', 'AUX', 'INTJ'])
def test_cc_with_invalid_upos_but_fixed_child_valid(
    validator_level_3: ConlluValidator,
    upostag: str,
    root_token: dict[str, Any],
) -> None:
    """Test that cc deprel with disallowed UPOS is valid when it has fixed child."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'cc',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'child',
            'lemma': 'child',
            'upostag': 'X',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'fixed',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    root_token['id'] = 3
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-cc')


@pytest.mark.parametrize('deprel', ['punct', 'root'])
def test_punct_upos_with_valid_deprel(validator_level_3: ConlluValidator, deprel: str) -> None:
    """Test that PUNCT UPOS with punct or root deprel is valid."""
    tokens = [
        {
            'id': 1,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': deprel,
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_no_errors_of_type(errors, 'upos-rel-punct')


@pytest.mark.parametrize(
    'deprel',
    ['nsubj', 'obj', 'obl', 'advmod', 'det', 'aux', 'case', 'mark', 'cc', 'cop', 'nmod', 'amod'],
)
def test_punct_upos_with_invalid_deprel(
    validator_level_3: ConlluValidator,
    deprel: str,
    root_token: dict[str, Any],
) -> None:
    """Test that PUNCT UPOS with non-punct/root deprel triggers error."""
    tokens = [
        {
            'id': 1,
            'form': ',',
            'lemma': ',',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': deprel,
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    assert_error_contains(errors, 'upos-rel-punct', "must be 'punct'")
    assert_error_contains(errors, 'upos-rel-punct', deprel)


def test_upos_deprel_not_validated_at_level_1(root_token: dict[str, Any]) -> None:
    """Test that UPOS-DEPREL compatibility is not validated at level 1."""
    validator = ConlluValidator(level=1)
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',  # Invalid for det
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-det')


def test_upos_deprel_not_validated_at_level_2(root_token: dict[str, Any]) -> None:
    """Test that UPOS-DEPREL compatibility is not validated at level 2."""
    validator = ConlluValidator(level=2)
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',  # Invalid for det
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator.validate_string(text)
    assert_no_errors_of_type(errors, 'rel-upos-det')


def test_upos_deprel_validated_at_level_3(root_token: dict[str, Any]) -> None:
    """Test that UPOS-DEPREL compatibility is validated at level 3."""
    validator = ConlluValidator(level=3)
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',  # Invalid for det
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator.validate_string(text)
    assert_error_contains(errors, 'rel-upos-det')


def test_upos_deprel_validated_at_level_4(root_token: dict[str, Any]) -> None:
    """Test that UPOS-DEPREL compatibility is validated at level 4."""
    validator = ConlluValidator(level=4)
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',  # Invalid for det
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator.validate_string(text)
    assert_error_contains(errors, 'rel-upos-det')


def test_upos_deprel_validated_at_level_5(root_token: dict[str, Any]) -> None:
    """Test that UPOS-DEPREL compatibility is validated at level 5."""
    validator = ConlluValidator(level=5, lang='la')
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',  # Invalid for det
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator.validate_string(text)
    assert_error_contains(errors, 'rel-upos-det')


def test_deprel_subtype_ignored_for_compatibility(
    validator_level_3: ConlluValidator,
    root_token: dict[str, Any],
) -> None:
    """Test that deprel subtypes are stripped when checking compatibility."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'det:predet',  # det with subtype
            'deps': '_',
            'misc': '_',
        },
        root_token,
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)
    # Should still check base relation 'det'
    assert_error_contains(errors, 'rel-upos-det')


def test_multiple_invalid_combinations_in_sentence(validator_level_3: ConlluValidator) -> None:
    """Test sentence with multiple UPOS-DEPREL compatibility errors."""
    tokens = [
        {
            'id': 1,
            'form': 'the',
            'lemma': 'the',
            'upostag': 'NOUN',  # Invalid for det
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
            'lemma': 'cat',
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
            'form': 'has',
            'lemma': 'have',
            'upostag': 'VERB',  # Invalid for aux
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'aux',
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
        {
            'id': 5,
            'form': ',',
            'lemma': ',',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'nmod',  # Invalid for PUNCT
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)

    # Should have 4 errors
    assert_error_count(errors, 4)
    assert_error_contains(errors, 'rel-upos-det')
    assert_error_contains(errors, 'rel-upos-aux')
    assert_error_contains(errors, 'upos-rel-punct')
    assert_error_contains(errors, 'leaf-aux-cop')


def test_all_valid_combinations_no_errors(validator_level_3: ConlluValidator) -> None:
    """Test sentence with all valid UPOS-DEPREL combinations."""
    tokens = [
        {
            'id': 1,
            'form': 'The',
            'lemma': 'the',
            'upostag': 'DET',  # Valid for det
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
            'id': 3,
            'form': 'has',
            'lemma': 'have',
            'upostag': 'AUX',  # Valid for aux
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'aux',
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
        {
            'id': 5,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',  # Valid for punct
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)

    # Should have no UPOS-DEPREL errors
    assert_no_errors_of_type(errors, 'rel-upos-det')
    assert_no_errors_of_type(errors, 'rel-upos-aux')
    assert_no_errors_of_type(errors, 'rel-upos-punct')
    assert_no_errors_of_type(errors, 'upos-rel-punct')


def test_multiword_token_skipped(validator_level_3: ConlluValidator) -> None:
    """Test that multiword tokens don't trigger UPOS-DEPREL checks."""
    tokens = [
        {
            'id': '1-2',
            'form': 'cannot',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': None,
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 1,
            'form': 'can',
            'lemma': 'can',
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
            'form': 'not',
            'lemma': 'not',
            'upostag': 'PART',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'advmod',
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
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)

    # MWT should be skipped, word tokens should be validated
    assert_no_errors_of_type(errors, 'rel-upos-aux')
    assert_no_errors_of_type(errors, 'rel-upos-advmod')


def test_empty_node_validated(validator_level_3: ConlluValidator) -> None:
    """Test that empty nodes are validated for UPOS-DEPREL compatibility."""
    tokens = [
        {
            'id': 1,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': '1.1',
            'form': 'implied',
            'lemma': 'implied',
            'upostag': 'NOUN',  # Invalid for aux
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'aux',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(tokens=tokens)
    errors = validator_level_3.validate_string(text)

    # Empty node should be validated
    assert_error_contains(errors, 'rel-upos-aux')
