"""Tests for metadata file generation."""

from __future__ import annotations

import json
from pathlib import Path

from nlp_utilities.brat.conllu_to_brat import conllu_to_brat


def test_metadata_file_created(
    temp_dir: Path,
    simple_conllu_content: str,
) -> None:
    """Test that metadata.json file is created."""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(simple_conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(conllu_file), str(output_dir))

    metadata_file = output_dir / 'metadata.json'
    assert metadata_file.exists()


def test_metadata_contains_all_parameters(
    temp_dir: Path,
    simple_conllu_content: str,
) -> None:
    """Test that metadata includes all conversion parameters."""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(simple_conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    conllu_to_brat(
        str(conllu_file),
        str(output_dir),
        sents_per_doc=10,
        output_root=True,
    )

    with open(output_dir / 'metadata.json', encoding='utf-8') as f:
        metadata = json.load(f)

    assert 'conllu_filename' in metadata
    assert 'sents_per_doc' in metadata
    assert 'output_root' in metadata
    assert metadata['sents_per_doc'] == 10
    assert metadata['output_root'] is True
