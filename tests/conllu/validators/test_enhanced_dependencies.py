"""Tests for enhanced dependency validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


# Test enhanced dependency validation
def test_valid_enhanced_deps(tmp_path: Path) -> None:
    """Test valid enhanced dependencies."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '2:nsubj',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'came',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    assert len(errors) == 0, f'Expected no errors, got: {errors}'


def test_invalid_enhanced_head_reference(tmp_path: Path) -> None:
    """Test invalid enhanced head reference."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '99:nsubj',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'came',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    assert any('unknown-ehead' in e for e in errors), f'Expected unknown-ehead error, got: {errors}'
    assert any('99' in e for e in errors), f'Expected error about head 99, got: {errors}'


def test_self_loop_in_deps(tmp_path: Path) -> None:
    """Test self-loop detection in enhanced dependencies."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '1:nsubj',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'came',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    assert any('deps-self-loop' in e for e in errors), f'Expected deps-self-loop error, got: {errors}'


def test_root_consistency_in_deps(tmp_path: Path) -> None:
    """Test root consistency validation in enhanced dependencies."""
    # Test: head=0 but deprel != root
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '0:nsubj',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'came',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    assert any('enhanced-0-is-not-root' in e for e in errors), f'Expected enhanced-0-is-not-root error, got: {errors}'


def test_enhanced_deps_with_empty_nodes(tmp_path: Path) -> None:
    """Test enhanced dependencies with empty node references."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '2:nsubj|1.1:nsubj',
            'misc': '_',
        },
        {
            'id': '1.1',
            'form': 'was',
            'lemma': 'be',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '2:aux',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'came',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    # Should not have errors about unknown head 1.1
    assert not any('unknown-ehead' in e and '1.1' in e for e in errors), (
        f'Should not error on valid empty node reference, got: {errors}'
    )


def test_orphan_with_empty_nodes(tmp_path: Path) -> None:
    """Test that orphan relations are not allowed when empty nodes are present."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '2:orphan',
            'misc': '_',
        },
        {
            'id': '1.1',
            'form': 'was',
            'lemma': 'be',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '2:aux',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'came',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=3)
    errors = validator.validate_string(text)
    assert any('eorphan-with-empty-node' in e for e in errors), f'Expected eorphan-with-empty-node error, got: {errors}'


def test_multiple_enhanced_deps(tmp_path: Path) -> None:
    """Test multiple enhanced dependencies per token."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '2:nsubj|3:nsubj',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'came',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'went',
            'lemma': 'go',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'conj',
            'deps': '2:conj',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    # Should not have any errors - this is valid
    assert len(errors) == 0, f'Expected no errors for multiple enhanced deps, got: {errors}'


def test_enhanced_deps_underscore(tmp_path: Path) -> None:
    """Test that underscore in DEPS column is handled correctly."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
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
            'form': 'came',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    # Should not crash - underscore is valid (means no enhanced deps)
    # Filter out non-deps related errors
    deps_errors = [e for e in errors if 'deps' in e.lower() or 'enhanced' in e.lower()]
    assert len(deps_errors) == 0, f'Expected no deps errors, got: {deps_errors}'


def test_enhanced_deps_with_multiword_tokens(tmp_path: Path) -> None:
    """Test that multiword tokens are skipped in enhanced dependency validation."""
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
            'deps': '0:root',
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
            'deprel': 'advmod',
            'deps': '1:advmod',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    # Should not crash or report errors for MWT range (1-2)
    # Filter to deps-related errors
    deps_errors = [e for e in errors if 'deps' in e.lower() or 'enhanced' in e.lower()]
    assert len(deps_errors) == 0, f'Expected no deps errors, got: {deps_errors}'


def test_enhanced_deps_with_subtypes(tmp_path: Path) -> None:
    """Test enhanced dependencies with relation subtypes."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '2:nsubj:xsubj',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'came',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    # Should handle subtypes in DEPS
    assert len(errors) == 0, f'Expected no errors for deps with subtypes, got: {errors}'


def test_enhanced_deps_zero_head_with_root(tmp_path: Path) -> None:
    """Test that head=0 with deprel=root is valid in enhanced deps."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nsubj',
            'deps': '2:nsubj',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'came',
            'lemma': 'come',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
    ]
    text = ConlluSentenceFactory.as_text(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_string(text)
    # This should be valid
    assert len(errors) == 0, f'Expected no errors, got: {errors}'
