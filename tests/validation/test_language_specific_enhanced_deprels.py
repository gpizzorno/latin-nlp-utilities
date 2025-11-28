"""Test validation of language-specific enhanced DEPRELs (DEPS column) at Level 4+."""

from pathlib import Path

from conllu_tools.validation.validator import ConlluValidator
from tests.factories import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_contains, assert_error_count, assert_no_errors_of_type


def test_enhanced_global_deprel_passes_level4(tmp_path: Path) -> None:
    """Global enhanced DEPRELs should pass at Level 4."""
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
            'deps': '0:root',
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
            'deps': '1:obl:arg',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=4)
    errors = validator.validate_file(test_file)
    assert_no_errors_of_type(errors, 'unknown-edeprel')
    assert_no_errors_of_type(errors, 'unpermitted-edeprel')


def test_enhanced_local_deprel_passes_level4(tmp_path: Path) -> None:
    """Local enhanced DEPRELs should pass at Level 4."""
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
            'deps': '0:root',
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
            'deps': '1:advcl:abs',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=4)
    errors = validator.validate_file(test_file)
    assert_no_errors_of_type(errors, 'unknown-edeprel')
    assert_no_errors_of_type(errors, 'unpermitted-edeprel')


def test_enhanced_lspec_unpermitted_deprel_fails_level4(tmp_path: Path) -> None:
    """Enhanced DEPRELs with type=lspec and permitted=0 should fail at Level 4."""
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
            'deps': '0:root',
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
            'deps': '1:acl:appos',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=4)
    errors = validator.validate_file(test_file)
    # Should have an error about unpermitted enhanced deprel
    assert_error_count(errors, 1, 'unpermitted-edeprel')
    assert_error_contains(errors, 'unpermitted-edeprel', 'acl:appos')


def test_enhanced_unknown_deprel_fails_level4(tmp_path: Path) -> None:
    """Unknown enhanced DEPRELs should fail at Level 4."""
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
            'deps': '0:root',
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
            'deps': '1:obl:fakerelation',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=4)
    errors = validator.validate_file(test_file)
    # Should have an error about unknown enhanced deprel
    assert_error_count(errors, 1, 'unknown-edeprel-subtype')
    assert_error_contains(errors, 'unknown-edeprel-subtype', 'obl:fakerelation')


def test_enhanced_ref_relation_allowed(tmp_path: Path) -> None:
    """'ref' is a special relation only allowed in enhanced dependencies."""
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
            'deps': '0:root',
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
            'deps': '1:ref',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=4)
    errors = validator.validate_file(test_file)
    # 'ref' should be allowed
    assert_no_errors_of_type(errors, 'unknown-edeprel')
    assert_no_errors_of_type(errors, 'unpermitted-edeprel')


def test_enhanced_deprel_level2_only_checks_universal(tmp_path: Path) -> None:
    """At Level 2, only universal enhanced DEPRELs are checked."""
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
            'deps': '0:root',
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
            'deps': '1:obl:arg',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=2)
    errors = validator.validate_file(test_file)
    assert_no_errors_of_type(errors, 'unknown-edeprel')


def test_multiple_enhanced_deps_with_mixed_validity(tmp_path: Path) -> None:
    """Test sentence with both valid and invalid enhanced DEPRELs."""
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
            'deps': '0:root',
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
            'deps': '1:obl:arg|1:acl:appos',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='la', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(lang='la', level=4)
    errors = validator.validate_file(test_file)
    # obl:arg should pass (global, permitted)
    # acl:appos should fail (lspec, not permitted)
    assert_error_count(errors, 1, 'unpermitted-edeprel')
    assert_error_contains(errors, 'unpermitted-edeprel', 'acl:appos')
