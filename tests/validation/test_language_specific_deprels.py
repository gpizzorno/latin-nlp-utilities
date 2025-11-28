"""Test validation of language-specific DEPRELs at Level 4+."""

from pathlib import Path

from conllu_tools.validation.validator import ConlluValidator
from tests.factories import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_count, assert_no_errors_of_type


def test_universal_deprel_passes_level4(tmp_path: Path) -> None:
    """Universal DEPRELs should pass at Level 4."""
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': 'NN',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': 'NN',
            'feats': '_',
            'head': 1,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=4)
    errors = validator.validate_file(test_file)
    assert_no_errors_of_type(errors, 'unknown-edeprel')
    assert_no_errors_of_type(errors, 'deprel-not-permitted')


def test_global_deprel_passes_level4(tmp_path: Path) -> None:
    """Global DEPRELs (type=global, permitted=1) should pass at Level 4."""
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': 'NN',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': 'NN',
            'feats': '_',
            'head': 1,
            'deprel': 'obl:arg',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=4)
    errors = validator.validate_file(test_file)
    assert_no_errors_of_type(errors, 'unknown-edeprel')
    assert_no_errors_of_type(errors, 'deprel-not-permitted')


def test_local_deprel_passes_level4(tmp_path: Path) -> None:
    """Local DEPRELs (type=local, permitted=1) should pass at Level 4."""
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': 'NN',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': 'NN',
            'feats': '_',
            'head': 1,
            'deprel': 'advcl:abs',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=4)
    errors = validator.validate_file(test_file)
    assert_no_errors_of_type(errors, 'unknown-deprel')
    assert_no_errors_of_type(errors, 'deprel-not-permitted')


def test_lspec_unpermitted_deprel_fails_level4(tmp_path: Path) -> None:
    """DEPRELs with type=lspec and permitted=0 should fail at Level 4."""
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': 'NN',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': 'NN',
            'feats': '_',
            'head': 1,
            'deprel': 'acl:appos',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=4)
    errors = validator.validate_file(test_file)
    # Should have an error about unpermitted deprel
    assert_error_count(errors, 1, 'deprel-not-permitted')


def test_unknown_deprel_fails_level4(tmp_path: Path) -> None:
    """Unknown DEPRELs should fail at Level 4."""
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': 'NN',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': 'NN',
            'feats': '_',
            'head': 1,
            'deprel': 'obl:fakerelation',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=4)
    errors = validator.validate_file(test_file)
    # Should have an error about unknown deprel
    assert_error_count(errors, 1, 'unknown-deprel-subtype')


def test_unknown_base_deprel_fails_level4(tmp_path: Path) -> None:
    """Completely unknown base DEPREL should fail at Level 4."""
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': 'NN',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': 'NN',
            'feats': '_',
            'head': 1,
            'deprel': 'fakebase:subtype',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=4)
    errors = validator.validate_file(test_file)
    # Should have an error about unknown deprel
    assert_error_count(errors, 1, 'unknown-deprel')


def test_deprel_validation_level2_only_checks_universal(tmp_path: Path) -> None:
    """At Level 2, only universal DEPRELs are checked (base part only)."""
    # obl:arg has base 'obl' which is universal, so should pass
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': 'NN',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': 'NN',
            'feats': '_',
            'head': 1,
            'deprel': 'obl:arg',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=2)
    errors = validator.validate_file(test_file)
    assert_no_errors_of_type(errors, 'unknown-deprel')


def test_deprel_validation_level3_only_checks_universal(tmp_path: Path) -> None:
    """At Level 3, still only universal DEPRELs are checked."""
    tokens = [
        {
            'id': 1,
            'form': 'Test',
            'lemma': 'test',
            'upostag': 'NOUN',
            'xpostag': 'NN',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'word',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': 'NN',
            'feats': '_',
            'head': 1,
            'deprel': 'obl:arg',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=3)
    errors = validator.validate_file(test_file)
    assert_no_errors_of_type(errors, 'unknown-deprel')
