"""Tests for input validation in brat_to_conllu."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from nlp_utilities.brat.brat_to_conllu import brat_to_conllu


def test_missing_input_directory(temp_dir: Path, feature_set: dict[str, Any]) -> None:
    """Test error when input_directory is None."""
    with pytest.raises(FileNotFoundError, match='Must provide input directory'):
        brat_to_conllu('', temp_dir / 'output', feature_set)


def test_missing_output_directory(temp_dir: Path, feature_set: dict[str, Any]) -> None:
    """Test error when output_directory is None."""
    with pytest.raises(FileNotFoundError, match='Must provide output directory'):
        brat_to_conllu(temp_dir / 'input', '', feature_set)


def test_input_directory_not_exists(temp_dir: Path, feature_set: dict[str, Any]) -> None:
    """Test error when input_directory doesn't exist."""
    nonexistent = temp_dir / 'nonexistent'
    with pytest.raises(FileNotFoundError, match='Input directory not found'):
        brat_to_conllu(nonexistent, temp_dir / 'output', feature_set)


def test_no_ann_files_found(temp_dir: Path, feature_set: dict[str, Any]) -> None:
    """Test error when no .ann files found in directory."""
    empty_dir = temp_dir / 'empty'
    empty_dir.mkdir()
    with pytest.raises(FileNotFoundError, match='No annotation files found'):
        brat_to_conllu(empty_dir, temp_dir / 'output', feature_set)


def test_reference_conllu_not_exists(
    brat_input_dir: Path,
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test error when reference CoNLL-U file doesn't exist."""
    with pytest.raises(FileNotFoundError, match='Reference CONLLU file not found'):
        brat_to_conllu(
            brat_input_dir,
            temp_dir / 'output',
            feature_set,
            ref_conllu=temp_dir / 'nonexistent.conllu',
            sents_per_doc=1,
            output_root=False,
        )


def test_creates_output_directory(
    brat_input_dir: Path,
    reference_conllu_file: Path,
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test that output directory is created if it doesn't exist."""
    output_dir = temp_dir / 'new_output'
    assert not output_dir.exists()

    brat_to_conllu(
        brat_input_dir,
        output_dir,
        feature_set,
        ref_conllu=reference_conllu_file,
        sents_per_doc=1,
        output_root=False,
    )

    assert output_dir.exists()
