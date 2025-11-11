"""Test orphan relation validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


def test_valid_orphan_with_conj_parent(tmp_path: Path) -> None:
    """Test that orphan with conj parent is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'John',
            'lemma': 'John',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'eats',
            'lemma': 'eats',
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
            'form': 'apples',
            'lemma': 'apples',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'obj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'and',
            'lemma': 'and',
            'upostag': 'CCONJ',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'cc',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 5,
            'form': 'Mary',
            'lemma': 'Mary',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'conj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 6,
            'form': 'vegetables',
            'lemma': 'vegetables',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'orphan',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(
        lang='en',
        tmp_path=tmp_path,
        tokens=tokens,
        text='John eats apples and Mary vegetables',
    )
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    orphan_errors = [e for e in errors if 'orphan-parent' in e]
    assert len(orphan_errors) == 0


def test_valid_orphan_with_parataxis_parent(tmp_path: Path) -> None:
    """Test that orphan with parataxis parent is valid."""
    tokens = [
        {
            'id': 1,
            'form': 'John',
            'lemma': 'John',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'eats',
            'lemma': 'eats',
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
            'form': 'apples',
            'lemma': 'apples',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'obj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': ';',
            'lemma': ';',
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
            'form': 'Mary',
            'lemma': 'Mary',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'parataxis',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 6,
            'form': 'vegetables',
            'lemma': 'vegetables',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'orphan',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(
        lang='en',
        tmp_path=tmp_path,
        tokens=tokens,
        text='John eats apples ; Mary vegetables',
    )
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    orphan_errors = [e for e in errors if 'orphan-parent' in e]
    assert len(orphan_errors) == 0


def test_valid_orphan_with_csubj_parent(tmp_path: Path) -> None:
    """Test that orphan with csubj parent is valid."""
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
            'form': 'Mary',
            'lemma': 'Mary',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'csubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'vegetables',
            'lemma': 'vegetables',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'orphan',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens, text='he thinks Mary vegetables')
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    orphan_errors = [e for e in errors if 'orphan-parent' in e]
    assert len(orphan_errors) == 0


def test_invalid_orphan_with_nsubj_parent(tmp_path: Path) -> None:
    """Test that orphan with nsubj parent is invalid."""
    tokens = [
        {
            'id': 1,
            'form': 'John',
            'lemma': 'John',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'eats',
            'lemma': 'eats',
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
            'form': 'apples',
            'lemma': 'apples',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'obj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'Mary',
            'lemma': 'Mary',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 5,
            'form': 'vegetables',
            'lemma': 'vegetables',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'orphan',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(
        lang='en',
        tmp_path=tmp_path,
        tokens=tokens,
        text='John eats apples Mary vegetables',
    )
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    orphan_errors = [e for e in errors if 'orphan-parent' in e]
    assert len(orphan_errors) == 1
    assert any('nsubj' in e for e in orphan_errors)


def test_invalid_orphan_with_obj_parent(tmp_path: Path) -> None:
    """Test that orphan with obj parent is invalid."""
    tokens = [
        {
            'id': 1,
            'form': 'John',
            'lemma': 'John',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'eats',
            'lemma': 'eats',
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
            'form': 'apples',
            'lemma': 'apples',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'obj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'Mary',
            'lemma': 'Mary',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'obj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 5,
            'form': 'vegetables',
            'lemma': 'vegetables',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'orphan',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(
        lang='en',
        tmp_path=tmp_path,
        tokens=tokens,
        text='John eats apples Mary vegetables',
    )
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    orphan_errors = [e for e in errors if 'orphan-parent' in e]
    assert len(orphan_errors) == 1
    assert any('obj' in e for e in orphan_errors)


def test_orphan_with_subtype(tmp_path: Path) -> None:
    """Test that validation works with orphan subtypes."""
    tokens = [
        {
            'id': 1,
            'form': 'John',
            'lemma': 'John',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'eats',
            'lemma': 'eats',
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
            'form': 'apples',
            'lemma': 'apples',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'obj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'and',
            'lemma': 'and',
            'upostag': 'CCONJ',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'cc',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 5,
            'form': 'Mary',
            'lemma': 'Mary',
            'upostag': 'PROPN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'conj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 6,
            'form': 'vegetables',
            'lemma': 'vegetables',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'orphan:obj',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(
        lang='en',
        tmp_path=tmp_path,
        tokens=tokens,
        text='John eats apples and Mary vegetables',
    )
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    # Should not have orphan-parent error (base relation is orphan, parent is conj)
    orphan_errors = [e for e in errors if 'orphan-parent' in e]
    assert len(orphan_errors) == 0
