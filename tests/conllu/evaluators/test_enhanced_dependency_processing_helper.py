"""Tests for Enhanced Dependency processing helper functions."""

from __future__ import annotations

from nlp_utilities.conllu.evaluators.helpers import process_enhanced_deps


def test_process_enhanced_deps_with_simple_dependencies() -> None:
    """Test process_enhanced_deps with simple dependencies."""
    deps = [('nsubj', 1), ('obj', 1)]

    result = process_enhanced_deps(deps)

    assert len(result) == 2
    assert result[0] == (1, ['nsubj'])
    assert result[1] == (1, ['obj'])


def test_process_enhanced_deps_with_chained_dependencies() -> None:
    """Test process_enhanced_deps with chained dependencies (nmod>case)."""
    deps = [('nmod>case', 1)]

    result = process_enhanced_deps(deps)

    assert len(result) == 1
    assert result[0] == (1, ['nmod', 'case'])


def test_process_enhanced_deps_with_empty_input() -> None:
    """Test process_enhanced_deps with empty/None input."""
    result_none = process_enhanced_deps(None)
    result_empty = process_enhanced_deps([])

    assert result_none == []
    assert result_empty == []


def test_process_enhanced_deps_with_root_dependency() -> None:
    """Test process_enhanced_deps with root dependency (head=0)."""
    deps = [('root', 0)]

    result = process_enhanced_deps(deps)

    assert len(result) == 1
    assert result[0] == (0, ['root'])


def test_process_enhanced_deps_with_multiple_dependencies() -> None:
    """Test process_enhanced_deps with multiple dependencies."""
    deps = [
        ('nsubj', 1),
        ('obj', 1),
        ('obl>case', 1),
        ('conj', 3),
    ]

    result = process_enhanced_deps(deps)

    assert len(result) == 4
    assert result[0] == (1, ['nsubj'])
    assert result[1] == (1, ['obj'])
    assert result[2] == (1, ['obl', 'case'])
    assert result[3] == (3, ['conj'])
