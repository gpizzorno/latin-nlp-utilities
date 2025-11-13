"""Tests for metadata handling in brat_to_conllu."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from nlp_utilities.brat.brat_to_conllu import brat_to_conllu


def test_load_metadata_from_file(
    brat_input_dir: Path,
    reference_conllu_file: Path,
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test loading metadata from metadata.json file."""
    # Create metadata file
    metadata = {
        'conllu_filename': str(reference_conllu_file),
        'sents_per_doc': 1,
        'output_root': False,
    }
    (brat_input_dir / 'metadata.json').write_text(json.dumps(metadata), encoding='utf-8')

    # Should succeed without passing parameters
    brat_to_conllu(brat_input_dir, temp_dir / 'output', feature_set)

    # Verify output was created
    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    assert output_file.exists()


def test_assert_error_no_ref_conllu(
    brat_input_dir: Path,
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test assertion error when ref_conllu is None and no metadata."""
    with pytest.raises(AssertionError, match='No ref_conllu value passed'):
        brat_to_conllu(brat_input_dir, temp_dir / 'output', feature_set)


def test_assert_error_no_output_root(
    brat_input_dir: Path,
    reference_conllu_file: Path,
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test assertion error when output_root is None and no metadata."""
    with pytest.raises(AssertionError, match='No output_root value passed'):
        brat_to_conllu(
            brat_input_dir,
            temp_dir / 'output',
            feature_set,
            ref_conllu=reference_conllu_file,
            sents_per_doc=1,
        )
