"""Tests for BRAT annotation manipulation functions."""

from __future__ import annotations

from typing import Any

from conllu_tools.utils.brat import get_next_id_number, sort_annotations, sort_annotations_set


def test_sort_annotations_set_by_id() -> None:
    """Test sorting annotations by ID in ascending order."""
    annotations: list[dict[str, Any]] = [
        {'type': 'T', 'id': 3, 'form': 'c', 'start': 7, 'end': 11},
        {'type': 'T', 'id': 1, 'form': 'a', 'start': 0, 'end': 1},
        {'type': 'T', 'id': 2, 'form': 'b', 'start': 2, 'end': 6},
    ]
    sorted_anns = sort_annotations_set(annotations)
    assert sorted_anns[0]['id'] == 1
    assert sorted_anns[1]['id'] == 2
    assert sorted_anns[2]['id'] == 3


def test_sort_annotations_set_empty_list() -> None:
    """Test sorting empty list."""
    annotations: list[dict[str, Any]] = []
    sorted_anns = sort_annotations_set(annotations)
    assert len(sorted_anns) == 0


def test_sort_annotations_set_single_annotation() -> None:
    """Test sorting single annotation."""
    annotations: list[dict[str, Any]] = [
        {'type': 'T', 'id': 1, 'form': 'a', 'start': 7, 'end': 11},
    ]
    sorted_anns = sort_annotations_set(annotations)
    assert len(sorted_anns) == 1


def test_sort_annotations_set_already_sorted() -> None:
    """Test sorting pre-sorted list."""
    annotations: list[dict[str, Any]] = [
        {'type': 'T', 'id': 1, 'form': 'a', 'start': 0, 'end': 1},
        {'type': 'T', 'id': 2, 'form': 'b', 'start': 2, 'end': 6},
        {'type': 'T', 'id': 3, 'form': 'c', 'start': 7, 'end': 11},
    ]
    sorted_anns = sort_annotations_set(annotations)
    assert sorted_anns[0]['id'] == 1
    assert sorted_anns[2]['id'] == 3


def test_sort_annotations_set_reverse_sorted() -> None:
    """Test sorting reverse-sorted list."""
    annotations: list[dict[str, Any]] = [
        {'type': 'T', 'id': 3, 'form': 'c', 'start': 7, 'end': 11},
        {'type': 'T', 'id': 2, 'form': 'b', 'start': 2, 'end': 6},
        {'type': 'T', 'id': 1, 'form': 'a', 'start': 0, 'end': 1},
    ]
    sorted_anns = sort_annotations_set(annotations)
    assert sorted_anns[0]['id'] == 1
    assert sorted_anns[2]['id'] == 3


def test_sort_annotations_set_non_sequential() -> None:
    """Test sorting annotations with non-sequential IDs."""
    annotations: list[dict[str, Any]] = [
        {'type': 'T', 'id': 10, 'form': 'c', 'start': 20, 'end': 24},
        {'type': 'T', 'id': 5, 'form': 'b', 'start': 2, 'end': 6},
        {'type': 'T', 'id': 2, 'form': 'a', 'start': 0, 'end': 1},
    ]
    sorted_anns = sort_annotations_set(annotations)
    assert sorted_anns[0]['id'] == 2
    assert sorted_anns[1]['id'] == 5
    assert sorted_anns[2]['id'] == 10


def test_sort_annotations_by_type_and_id_range() -> None:
    """Test sorting by type first (T before R), then by ID/Range."""
    annotations: list[dict[str, Any]] = [
        {'type': 'R', 'id': 1, 'deprel': 'nsubj'},
        {'type': 'T', 'id': 2, 'form': 'b', 'start': 2, 'end': 6},
        {'type': 'T', 'id': 1, 'form': 'a', 'start': 0, 'end': 1},
        {'type': 'R', 'id': 2, 'deprel': 'root'},
    ]
    sorted_anns = sort_annotations(annotations)
    assert sorted_anns[0]['type'] == 'T'
    assert sorted_anns[0]['id'] == 1
    assert sorted_anns[1]['type'] == 'T'
    assert sorted_anns[1]['id'] == 2
    assert sorted_anns[2]['type'] == 'R'
    assert sorted_anns[2]['id'] == 1
    assert sorted_anns[3]['type'] == 'R'
    assert sorted_anns[3]['id'] == 2


def test_sort_annotations_only_entities() -> None:
    """Test sorting with only T annotations."""
    annotations: list[dict[str, Any]] = [
        {'type': 'T', 'id': 3, 'form': 'c', 'start': 7, 'end': 11},
        {'type': 'T', 'id': 1, 'form': 'a', 'start': 0, 'end': 1},
    ]
    sorted_anns = sort_annotations(annotations)
    assert len(sorted_anns) == 2
    assert sorted_anns[0]['id'] == 1


def test_sort_annotations_only_relations() -> None:
    """Test sorting with only R annotations."""
    annotations: list[dict[str, Any]] = [
        {'type': 'R', 'id': 3, 'deprel': 'c'},
        {'type': 'R', 'id': 1, 'deprel': 'a'},
    ]
    sorted_anns = sort_annotations(annotations)
    assert len(sorted_anns) == 2
    assert sorted_anns[0]['id'] == 1


def test_sort_annotations_empty_list() -> None:
    """Test sorting empty list."""
    annotations: list[dict[str, Any]] = []
    sorted_anns = sort_annotations(annotations)
    assert len(sorted_anns) == 0


def test_get_next_id_number_for_entities() -> None:
    """Test finding next ID for entities (T-type)."""
    annotations: list[dict[str, Any]] = [
        {'type': 'T', 'id': 1},
        {'type': 'T', 'id': 2},
        {'type': 'T', 'id': 3},
    ]
    next_id = get_next_id_number(annotations, 'T')
    assert next_id == 4


def test_get_next_id_number_for_relations() -> None:
    """Test finding next ID for relations (R-type)."""
    annotations: list[dict[str, Any]] = [
        {'type': 'R', 'id': 1},
        {'type': 'R', 'id': 2},
    ]
    next_id = get_next_id_number(annotations, 'R')
    assert next_id == 3


def test_get_next_id_number_empty_list() -> None:
    """Test finding next ID in empty annotation list (should return 1)."""
    annotations: list[dict[str, Any]] = []
    next_id = get_next_id_number(annotations, 'T')
    assert next_id == 1


def test_get_next_id_number_with_gaps() -> None:
    """Test finding next ID with gaps (e.g., T1, T3 → next is 4)."""
    annotations: list[dict[str, Any]] = [
        {'type': 'T', 'id': 1},
        {'type': 'T', 'id': 3},
    ]
    next_id = get_next_id_number(annotations, 'T')
    assert next_id == 4


def test_get_next_id_number_large_ids() -> None:
    """Test finding next ID with large ID numbers."""
    annotations: list[dict[str, Any]] = [
        {'type': 'T', 'id': 100},
        {'type': 'T', 'id': 200},
    ]
    next_id = get_next_id_number(annotations, 'T')
    assert next_id == 201


def test_get_next_id_number_only_one_type() -> None:
    """Test finding next ID when only one annotation type is present."""
    annotations: list[dict[str, Any]] = [
        {'type': 'T', 'id': 1},
        {'type': 'T', 'id': 2},
    ]
    next_id = get_next_id_number(annotations, 'R')
    assert next_id == 1  # No R types, so should start at 1
