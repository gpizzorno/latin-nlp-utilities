"""Tests for UDSpan class."""

from __future__ import annotations

import pytest

from nlp_utilities.conllu.evaluators.base import UDSpan


def test_udspan_creation(simple_udspan: UDSpan) -> None:
    """Test UDSpan creation with valid start/end."""
    assert simple_udspan.start == 0
    assert simple_udspan.end == 5


def test_udspan_immutability(simple_udspan: UDSpan) -> None:
    """Test UDSpan immutability (frozen dataclass)."""
    with pytest.raises(AttributeError):
        simple_udspan.start = 10  # type: ignore[misc]


def test_udspan_equality() -> None:
    """Test UDSpan equality."""
    span1 = UDSpan(start=0, end=5)
    span2 = UDSpan(start=0, end=5)
    span3 = UDSpan(start=0, end=10)

    assert span1 == span2
    assert span1 != span3


def test_udspan_empty(empty_udspan: UDSpan) -> None:
    """Test UDSpan with start=end (empty span)."""
    assert empty_udspan.start == empty_udspan.end
    assert empty_udspan.start == 5


def test_udspan_hash() -> None:
    """Test UDSpan hash for use in sets/dicts."""
    span1 = UDSpan(start=0, end=5)
    span2 = UDSpan(start=0, end=5)
    span3 = UDSpan(start=0, end=10)

    # Same spans should have same hash
    assert hash(span1) == hash(span2)

    # Can be used in sets
    span_set = {span1, span2, span3}
    assert len(span_set) == 2  # span1 and span2 are equal

    # Can be used as dict keys
    span_dict = {span1: 'first', span3: 'second'}
    assert span_dict[span2] == 'first'  # span2 equals span1
