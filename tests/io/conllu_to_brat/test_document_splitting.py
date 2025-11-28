"""Tests for multi-document splitting logic."""

from __future__ import annotations

from pathlib import Path

from conllu_tools.io import conllu_to_brat


def test_single_document_no_splitting(
    temp_dir: Path,
    multi_sentence_conllu: Path,
) -> None:
    """Test that all sentences go to one document when sents_per_doc=None."""
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(multi_sentence_conllu), str(output_dir), sents_per_doc=None)

    # Should have one .ann file without doc number
    ann_files = list(output_dir.glob('*.ann'))
    assert len(ann_files) == 1
    assert 'doc-' not in ann_files[0].name


def test_splitting_with_sents_per_doc(
    temp_dir: Path,
    multi_sentence_conllu: Path,
) -> None:
    """Test that documents are split when sents_per_doc is set."""
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(multi_sentence_conllu), str(output_dir), sents_per_doc=1)

    # Should have two .ann files with doc numbers
    ann_files = sorted(output_dir.glob('*doc-*.ann'))
    assert len(ann_files) == 2
    assert 'doc-001' in ann_files[0].name
    assert 'doc-002' in ann_files[1].name


def test_file_naming_with_doc_numbers(
    temp_dir: Path,
    multi_sentence_conllu: Path,
) -> None:
    """Test that files are named correctly with doc numbers."""
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(multi_sentence_conllu), str(output_dir), sents_per_doc=1)

    # Check specific file names
    assert (output_dir / 'multi-doc-001.ann').exists()
    assert (output_dir / 'multi-doc-001.txt').exists()
    assert (output_dir / 'multi-doc-002.ann').exists()
    assert (output_dir / 'multi-doc-002.txt').exists()
