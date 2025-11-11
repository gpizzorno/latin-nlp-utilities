"""Test validation of language-specific enhanced DEPRELs (DEPS column) at Level 4+."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


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

    edeprel_errors = [
        e
        for e in errors
        if 'enhanced' in e.lower() and 'obl:arg' in e.lower() and ('unknown' in e.lower() or 'permitted' in e.lower())
    ]
    assert len(edeprel_errors) == 0


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

    edeprel_errors = [
        e
        for e in errors
        if 'enhanced' in e.lower() and 'advcl:abs' in e.lower() and ('unknown' in e.lower() or 'permitted' in e.lower())
    ]
    assert len(edeprel_errors) == 0


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
    unpermitted_errors = [
        e for e in errors if 'enhanced' in e.lower() and 'permitted' in e.lower() and 'acl:appos' in e.lower()
    ]
    assert len(unpermitted_errors) == 1


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
    unknown_errors = [
        e for e in errors if 'enhanced' in e.lower() and 'unknown' in e.lower() and 'obl:fakerelation' in e.lower()
    ]
    assert len(unknown_errors) == 1


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
    ref_errors = [e for e in errors if 'ref' in e.lower() and ('unknown' in e.lower() or 'permitted' in e.lower())]
    assert len(ref_errors) == 0


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

    edeprel_errors = [
        e for e in errors if 'enhanced' in e.lower() and 'obl:arg' in e.lower() and 'unknown' in e.lower()
    ]
    assert len(edeprel_errors) == 0


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
    unpermitted_errors = [
        e for e in errors if 'enhanced' in e.lower() and 'acl:appos' in e.lower() and 'permitted' in e.lower()
    ]
    assert len(unpermitted_errors) == 1
    # obl:arg should not have errors
    obl_arg_errors = [
        e for e in errors if 'obl:arg' in e.lower() and ('unknown' in e.lower() or 'permitted' in e.lower())
    ]
    assert len(obl_arg_errors) == 0
