"""Tests for _write_document helper function."""

from __future__ import annotations

from pathlib import Path

import pytest

from nlp_utilities.brat.conllu_to_brat import _write_document


def test_file_naming_without_doc_number(temp_dir: Path) -> None:
    """Test file naming when docnum=0."""
    sentences: list[tuple[str, list[dict[str, str | int]], list[dict[str, str | int]]]] = [
        (
            '1',
            [
                {'type': 'T', 'id': 1, 'form': 'Word', 'upos': 'NOUN'},
            ],
            [],
        ),
    ]

    _write_document(sentences, 'test.conllu', str(temp_dir), docnum=0)

    assert (temp_dir / 'test.ann').exists()
    assert (temp_dir / 'test.txt').exists()


def test_file_naming_with_doc_number(temp_dir: Path) -> None:
    """Test file naming when docnum > 0."""
    sentences: list[tuple[str, list[dict[str, str | int]], list[dict[str, str | int]]]] = [
        (
            '1',
            [
                {'type': 'T', 'id': 1, 'form': 'Word', 'upos': 'NOUN'},
            ],
            [],
        ),
    ]

    _write_document(sentences, 'test.conllu', str(temp_dir), docnum=5)

    assert (temp_dir / 'test-doc-005.ann').exists()
    assert (temp_dir / 'test-doc-005.txt').exists()


def test_offset_calculation(temp_dir: Path) -> None:
    """Test that offsets are calculated correctly for entities."""
    sentences: list[tuple[str, list[dict[str, str | int]], list[dict[str, str | int]]]] = [
        (
            '1',
            [
                {'type': 'T', 'id': 1, 'form': 'Word', 'upos': 'NOUN'},
                {'type': 'T', 'id': 2, 'form': 'test', 'upos': 'VERB'},
            ],
            [],
        ),
    ]

    _write_document(sentences, 'test.conllu', str(temp_dir), docnum=0)

    ann_content = (temp_dir / 'test.ann').read_text(encoding='utf-8')

    # First token: start=0, end=4 (length of "Word" is 4)
    assert 'T1\tNOUN 0 4\tWord' in ann_content
    # Second token: start=5 (4+1 for space), end=9 (5+4=9)
    assert 'T2\tVERB 5 9\ttest' in ann_content


def test_id_mapping_for_relations(temp_dir: Path) -> None:
    """Test that relation IDs are mapped correctly."""
    sentences: list[tuple[str, list[dict[str, str | int]], list[dict[str, str | int]]]] = [
        (
            '1',
            [
                {'type': 'T', 'id': 1, 'form': 'Word', 'upos': 'NOUN'},
                {'type': 'T', 'id': 2, 'form': 'test', 'upos': 'VERB'},
            ],
            [
                {'type': 'R', 'id': 1, 'head': 2, 'deprel': 'nsubj'},
            ],
        ),
    ]

    _write_document(sentences, 'test.conllu', str(temp_dir), docnum=0)

    ann_content = (temp_dir / 'test.ann').read_text(encoding='utf-8')

    # Relation should map head:2 → T2, dep:1 → T1
    assert 'R1\tnsubj Arg1:T2 Arg2:T1' in ann_content


def test_error_on_duplicate_entity_id(temp_dir: Path) -> None:
    """Test that ValueError is raised for duplicate entity IDs."""
    sentences: list[tuple[str, list[dict[str, str | int]], list[dict[str, str | int]]]] = [
        (
            '1',
            [
                {'type': 'T', 'id': 1, 'form': 'Word', 'upos': 'NOUN'},
                {'type': 'T', 'id': 1, 'form': 'test', 'upos': 'VERB'},  # Duplicate ID
            ],
            [],
        ),
    ]

    with pytest.raises(ValueError, match='Duplicate entity ID'):
        _write_document(sentences, 'test.conllu', str(temp_dir), docnum=0)


def test_error_on_missing_form(temp_dir: Path) -> None:
    """Test that ValueError is raised for missing form."""
    sentences: list[tuple[str, list[dict[str, str | int]], list[dict[str, str | int]]]] = [
        (
            '1',
            [
                {'type': 'T', 'id': 1, 'upos': 'NOUN'},  # Missing form
            ],
            [],
        ),
    ]

    with pytest.raises(ValueError, match='Missing FORM'):
        _write_document(sentences, 'test.conllu', str(temp_dir), docnum=0)


def test_error_on_invalid_relation_ids(temp_dir: Path) -> None:
    """Test that ValueError is raised for invalid relation IDs."""
    sentences: list[tuple[str, list[dict[str, str | int]], list[dict[str, str | int]]]] = [
        (
            '1',
            [
                {'type': 'T', 'id': 1, 'form': 'Word', 'upos': 'NOUN'},
            ],
            [
                {'type': 'R', 'id': 1, 'head': 999, 'deprel': 'nsubj'},  # Invalid head
            ],
        ),
    ]

    with pytest.raises(ValueError, match='Invalid relation IDs'):
        _write_document(sentences, 'test.conllu', str(temp_dir), docnum=0)


def test_text_generation_with_multiple_tokens(temp_dir: Path) -> None:
    """Test that text file contains correctly joined tokens."""
    sentences: list[tuple[str, list[dict[str, str | int]], list[dict[str, str | int]]]] = [
        (
            '1',
            [
                {'type': 'T', 'id': 1, 'form': 'Word', 'upos': 'NOUN'},
                {'type': 'T', 'id': 2, 'form': 'test', 'upos': 'VERB'},
                {'type': 'T', 'id': 3, 'form': 'sentence', 'upos': 'NOUN'},
            ],
            [],
        ),
    ]

    _write_document(sentences, 'test.conllu', str(temp_dir), docnum=0)

    txt_content = (temp_dir / 'test.txt').read_text(encoding='utf-8')

    assert 'Word test sentence' in txt_content
