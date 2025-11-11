"""Tests for enhanced graph connectivity validation."""

from pathlib import Path

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.factories.conllu import ConlluSentenceFactory


def test_connected_enhanced_graph(tmp_path: Path) -> None:
    """Test that a connected enhanced graph passes validation."""
    tokens = [
        {
            'id': 1,
            'form': 'Word1',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'Word2',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nmod',
            'deps': '1:nmod',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    connectivity_errors = [e for e in errors if 'unconnected' in e or 'not reachable' in e]
    assert len(connectivity_errors) == 0, f'Expected no connectivity errors, got: {connectivity_errors}'


def test_disconnected_enhanced_graph_single_node(tmp_path: Path) -> None:
    """Test that disconnected enhanced graph is caught (single unreachable node)."""
    # Word 2 has DEPS=_, so it's not in the enhanced graph
    tokens = [
        {
            'id': 1,
            'form': 'Word1',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'Word2',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nmod',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    assert any('unconnected-egraph' in e and "'2'" in e for e in errors), (
        f'Expected unconnected-egraph error for node 2, got: {errors}'
    )


def test_disconnected_enhanced_graph_multiple_nodes(tmp_path: Path) -> None:
    """Test that multiple disconnected nodes are reported."""
    # Words 2 and 3 have no DEPS
    tokens = [
        {
            'id': 1,
            'form': 'Word1',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'Word2',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nmod',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'Word3',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nmod',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    connectivity_errors = [e for e in errors if 'unconnected-egraph' in e]
    assert len(connectivity_errors) == 1, f'Expected 1 connectivity error, got: {len(connectivity_errors)}'
    # Should mention both nodes
    error_text = connectivity_errors[0]
    assert '2' in error_text, f'Expected error to mention node 2, got: {error_text}'
    assert '3' in error_text, f'Expected error to mention node 3, got: {error_text}'


def test_connected_with_empty_nodes(tmp_path: Path) -> None:
    """Test connected enhanced graph with empty nodes."""
    tokens = [
        {
            'id': 1,
            'form': 'Word1',
            'lemma': 'word',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root|1.1:aux',
            'misc': '_',
        },
        {
            'id': '1.1',
            'form': 'would',
            'lemma': 'would',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '0:aux',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'Word2',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nsubj',
            'deps': '1:nsubj|1.1:nsubj',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    connectivity_errors = [e for e in errors if 'unconnected-egraph' in e]
    assert len(connectivity_errors) == 0, f'Expected no connectivity errors, got: {connectivity_errors}'


def test_disconnected_empty_node(tmp_path: Path) -> None:
    """Test that disconnected empty node is caught."""
    # Empty node 1.1 has no DEPS
    tokens = [
        {
            'id': 1,
            'form': 'Word1',
            'lemma': 'word',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
        {
            'id': '1.1',
            'form': 'would',
            'lemma': 'would',
            'upostag': 'AUX',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'Word2',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nsubj',
            'deps': '1:nsubj',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    assert any('unconnected-egraph' in e and '1.1' in e for e in errors), (
        f'Expected unconnected-egraph error for empty node 1.1, got: {errors}'
    )


def test_no_enhanced_deps(tmp_path: Path) -> None:
    """Test that absence of enhanced dependencies doesn't trigger error."""
    # No DEPS at all - this is valid
    tokens = [
        {
            'id': 1,
            'form': 'Word1',
            'lemma': 'word',
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
            'form': 'Word2',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nmod',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    connectivity_errors = [e for e in errors if 'unconnected-egraph' in e]
    assert len(connectivity_errors) == 0, (
        f'Expected no connectivity errors when DEPS is absent, got: {connectivity_errors}'
    )


def test_partial_enhanced_deps(tmp_path: Path) -> None:
    """Test graph connectivity when only some tokens have enhanced deps."""
    # Word 1 has DEPS, word 2 doesn't - word 2 is unreachable
    tokens = [
        {
            'id': 1,
            'form': 'Word1',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'Word2',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nmod',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'Word3',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nmod',
            'deps': '1:nmod',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    # Should report node 2 as unreachable (word 3 is reachable)
    assert any('unconnected-egraph' in e and "'2'" in e for e in errors), (
        f'Expected unconnected-egraph error for node 2, got: {errors}'
    )


def test_complex_connected_graph(tmp_path: Path) -> None:
    """Test complex but connected enhanced graph."""
    tokens = [
        {
            'id': 1,
            'form': 'Word1',
            'lemma': 'word',
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
            'form': 'Word2',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nsubj',
            'deps': '1:nsubj|3:nmod',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'Word3',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'obj',
            'deps': '1:obj',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'Word4',
            'lemma': 'word',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'amod',
            'deps': '3:amod',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    connectivity_errors = [e for e in errors if 'unconnected-egraph' in e]
    assert len(connectivity_errors) == 0, f'Expected no connectivity errors, got: {connectivity_errors}'


def test_cycle_in_enhanced_graph(tmp_path: Path) -> None:
    """Test that cycles don't break connectivity checking."""
    # Cycle: 1 -> 2 -> 3 -> 2 (via enhanced deps)
    tokens = [
        {
            'id': 1,
            'form': 'Word1',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'Word2',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'nmod',
            'deps': '1:nmod',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'Word3',
            'lemma': 'word',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'nmod',
            'deps': '2:nmod|1:nmod',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(lang='en', tmp_path=tmp_path, tokens=tokens)
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)

    connectivity_errors = [e for e in errors if 'unconnected-egraph' in e]
    # Should not crash and should not report connectivity errors (all reachable)
    assert len(connectivity_errors) == 0, f'Expected no connectivity errors with cycle, got: {connectivity_errors}'
