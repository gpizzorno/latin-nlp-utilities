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
        output_root=True,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    assert output_file.exists()

    # Load and verify
    with open(output_file, encoding='utf-8') as file:
        sentences = conllu.parse(file.read())

    assert len(sentences) == 1
    assert len(sentences[0]) == 8  # 8 tokens in the simple sentence


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
        output_root=True,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    with open(output_file, encoding='utf-8') as file:
        sentences = conllu.parse(file.read())

    # Check token forms match (case-insensitive)
    assert sentences[0][0]['form'].lower() == 'gallia'
    assert sentences[0][1]['form'].lower() == 'est'
    assert sentences[0][2]['form'].lower() == 'omnis'
    assert sentences[0][3]['form'].lower() == 'divisa'
    assert sentences[0][4]['form'].lower() == 'in'
    assert sentences[0][5]['form'].lower() == 'partes'
    assert sentences[0][6]['form'].lower() == 'tres'
    assert sentences[0][7]['form'].lower() == '.'


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
        output_root=True,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    with open(output_file, encoding='utf-8') as file:
        sentences = conllu.parse(file.read())

    assert sentences[0][0]['upos'] == 'PROPN'
    assert sentences[0][1]['upos'] == 'AUX'
    assert sentences[0][2]['upos'] == 'ADJ'
    assert sentences[0][3]['upos'] == 'VERB'
    assert sentences[0][4]['upos'] == 'ADP'
    assert sentences[0][5]['upos'] == 'NOUN'
    assert sentences[0][6]['upos'] == 'NUM'
    assert sentences[0][7]['upos'] == 'PUNCT'


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
        output_root=True,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    with open(output_file, encoding='utf-8') as file:
        sentences = conllu.parse(file.read())

    assert sentences[0][0]['head'] == 4
    assert sentences[0][1]['head'] == 4
    assert sentences[0][2]['head'] == 1
    assert sentences[0][3]['head'] == 0
    assert sentences[0][4]['head'] == 6
    assert sentences[0][5]['head'] == 4
    assert sentences[0][6]['head'] == 6
    assert sentences[0][7]['head'] == 4


def test_deprels_mapped(
    brat_input_dir: Path,
    reference_conllu_file: Path,
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test that dependency relations are mapped correctly."""
    brat_to_conllu(
        brat_input_dir,
        temp_dir / 'output',
        feature_set,
        ref_conllu=reference_conllu_file,
        sents_per_doc=1,
        output_root=True,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    with open(output_file, encoding='utf-8') as file:
        sentences = conllu.parse(file.read())

    assert sentences[0][0]['deprel'] == 'nsubj:pass'
    assert sentences[0][1]['deprel'] == 'aux:pass'
    assert sentences[0][2]['deprel'] == 'amod'
    assert sentences[0][3]['deprel'] == 'root'
    assert sentences[0][4]['deprel'] == 'case'
    assert sentences[0][5]['deprel'] == 'obl'
    assert sentences[0][6]['deprel'] == 'nummod'
    assert sentences[0][7]['deprel'] == 'punct'


def test_deps_transferred(
    brat_input_dir: Path,
    reference_conllu_file: Path,
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test that extended deps are transferred correctly."""
    brat_to_conllu(
        brat_input_dir,
        temp_dir / 'output',
        feature_set,
        ref_conllu=reference_conllu_file,
        sents_per_doc=1,
        output_root=True,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    with open(output_file, encoding='utf-8') as file:
        sentences = conllu.parse(file.read())

    assert sentences[0][0]['deps'] == [('nsubj:pass', 4)]
    assert sentences[0][1]['deps'] == [('aux:pass', 4)]
    assert sentences[0][2]['deps'] == [('amod', 1)]
    assert sentences[0][3]['deps'] == [('root', 0)]
    assert sentences[0][4]['deps'] == [('case', 6)]
    assert sentences[0][5]['deps'] == [('obl', 4)]
    assert sentences[0][6]['deps'] == [('nummod', 6)]
    assert sentences[0][7]['deps'] == [('punct', 4)]


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
        output_root=True,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    with open(output_file, encoding='utf-8') as file:
        sentences = conllu.parse(file.read())

    assert 'sent_id' in sentences[0].metadata
    assert sentences[0].metadata['sent_id'] == '1'
    assert 'text' in sentences[0].metadata
    assert sentences[0].metadata['text'] == 'Gallia est omnis divisa in partes tres .'
