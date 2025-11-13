"""Tests for basic BRAT to CoNLL-U conversion."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import conllu

from nlp_utilities.brat.brat_to_conllu import brat_to_conllu


def test_simple_sentence_conversion(
    brat_input_dir: Path,
    reference_conllu_file: Path,
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test converting a simple sentence correctly."""
    brat_to_conllu(
        brat_input_dir,
        temp_dir / 'output',
        feature_set,
        ref_conllu=reference_conllu_file,
        sents_per_doc=1,
        output_root=False,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    assert output_file.exists()

    # Load and verify
    with open(output_file, encoding='utf-8') as f:
        sentences = conllu.parse(f.read())

    assert len(sentences) == 1
    assert len(sentences[0]) == 2


def test_token_alignment(
    brat_input_dir: Path,
    reference_conllu_file: Path,
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test that tokens are aligned correctly between BRAT and reference."""
    brat_to_conllu(
        brat_input_dir,
        temp_dir / 'output',
        feature_set,
        ref_conllu=reference_conllu_file,
        sents_per_doc=1,
        output_root=False,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    with open(output_file, encoding='utf-8') as f:
        sentences = conllu.parse(f.read())

    # Check token forms match (case-insensitive)
    assert sentences[0][0]['form'].lower() == 'word'
    assert sentences[0][1]['form'].lower() == 'test'


def test_upos_tags_transferred(
    brat_input_dir: Path,
    reference_conllu_file: Path,
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test that UPOS tags are transferred from BRAT annotations."""
    brat_to_conllu(
        brat_input_dir,
        temp_dir / 'output',
        feature_set,
        ref_conllu=reference_conllu_file,
        sents_per_doc=1,
        output_root=False,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    with open(output_file, encoding='utf-8') as f:
        sentences = conllu.parse(f.read())

    assert sentences[0][0]['upos'] == 'NOUN'
    assert sentences[0][1]['upos'] == 'VERB'


def test_dependency_heads_mapped(
    brat_input_dir: Path,
    reference_conllu_file: Path,
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test that dependency heads are mapped correctly."""
    brat_to_conllu(
        brat_input_dir,
        temp_dir / 'output',
        feature_set,
        ref_conllu=reference_conllu_file,
        sents_per_doc=1,
        output_root=False,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    with open(output_file, encoding='utf-8') as f:
        sentences = conllu.parse(f.read())

    # Token 1 (Word) should point to token 2 (test)
    assert sentences[0][0]['head'] == 2
    assert sentences[0][0]['deprel'] == 'nsubj'


def test_deprel_labels_transferred(
    brat_input_dir: Path,
    reference_conllu_file: Path,
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test that deprel labels are transferred correctly."""
    brat_to_conllu(
        brat_input_dir,
        temp_dir / 'output',
        feature_set,
        ref_conllu=reference_conllu_file,
        sents_per_doc=1,
        output_root=False,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    with open(output_file, encoding='utf-8') as f:
        sentences = conllu.parse(f.read())

    assert sentences[0][0]['deprel'] == 'nsubj'


def test_sentence_metadata_preserved(
    brat_input_dir: Path,
    reference_conllu_file: Path,
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test that sentence metadata is preserved."""
    brat_to_conllu(
        brat_input_dir,
        temp_dir / 'output',
        feature_set,
        ref_conllu=reference_conllu_file,
        sents_per_doc=1,
        output_root=False,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    with open(output_file, encoding='utf-8') as f:
        sentences = conllu.parse(f.read())

    assert sentences[0].metadata.get('sent_id') == '1'
    assert 'text' in sentences[0].metadata
