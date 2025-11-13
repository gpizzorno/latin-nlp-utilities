"""Tests for UDWord class."""

from __future__ import annotations

from nlp_utilities.conllu.evaluators.base import UDWord
from tests.helpers.generation import create_test_udword


def test_udword_creation(simple_udword: UDWord) -> None:
    """Test UDWord creation with required fields."""
    assert simple_udword.span.start == 0
    assert simple_udword.span.end == 5
    assert simple_udword.token['form'] == 'word'
    assert simple_udword.is_multiword is False
    assert simple_udword.enhanced_deps is None
    assert simple_udword.functional_children is None


def test_udword_with_multiword_flag(multiword_udword: UDWord) -> None:
    """Test UDWord with multiword flag."""
    assert multiword_udword.is_multiword is True
    assert multiword_udword.span.end == 10


def test_udword_with_enhanced_deps(udword_with_enhanced_deps: UDWord) -> None:
    """Test UDWord with enhanced_deps."""
    assert udword_with_enhanced_deps.enhanced_deps is not None
    assert len(udword_with_enhanced_deps.enhanced_deps) == 1
    assert udword_with_enhanced_deps.enhanced_deps[0] == (0, ['root'])


def test_udword_with_functional_children(udword_with_functional_children: UDWord) -> None:
    """Test UDWord with functional_children."""
    assert udword_with_functional_children.functional_children is not None
    assert len(udword_with_functional_children.functional_children) == 1
    child = udword_with_functional_children.functional_children[0]
    assert child.token['form'] == 'the'
    assert child.token['deprel'] == 'det'


def test_udword_hash() -> None:
    """Test UDWord hash for use in dictionaries."""
    word1 = create_test_udword('word', 'NOUN', 0, 'root', start=0, end=4)
    word2 = create_test_udword('word', 'NOUN', 0, 'root', start=0, end=4)

    # Can be used in sets (different objects have different hashes due to id(token))
    word_set = {word1, word2}
    assert len(word_set) == 2  # Different objects

    # Can be used as dict keys
    word_dict = {word1: 'first', word2: 'second'}
    assert word_dict[word1] == 'first'
    assert word_dict[word2] == 'second'


def test_udword_equality_not_implemented() -> None:
    """Test UDWord equality (uses dataclass equality)."""
    word1 = create_test_udword('word', 'NOUN', 0, 'root', start=0, end=4)
    word2 = create_test_udword('word', 'NOUN', 0, 'root', start=0, end=4)

    # Dataclasses with same values are equal
    assert word1 == word2
    assert word1 == word1  # Same object is equal to itself  # noqa: PLR0124
