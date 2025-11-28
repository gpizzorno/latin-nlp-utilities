"""Tests for dependency conversion features."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import conllu

from conllu_tools.io import brat_to_conllu
from tests.test_data.load_data import SIMPLE_ANN_WITH_ROOT, SIMPLE_TXT_WITH_ROOT


def test_aux_deprel_changes_upos_to_aux(
    temp_dir: Path,
    reference_conllu_file: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test that aux deprel changes UPOS to AUX."""
    # Create BRAT with aux relation
    brat_dir = temp_dir / 'brat_aux'
    brat_dir.mkdir()
    ann_content = copy.deepcopy(SIMPLE_ANN_WITH_ROOT).replace('aux_colon_pass', 'aux')
    ann_content = ann_content.replace('AUX', 'VERB')
    (brat_dir / 'test.ann').write_text(ann_content, encoding='utf-8')
    (brat_dir / 'test.txt').write_text(SIMPLE_TXT_WITH_ROOT, encoding='utf-8')

    brat_to_conllu(
        brat_dir,
        temp_dir / 'output',
        feature_set,
        ref_conllu=reference_conllu_file,
        sents_per_doc=1,
        output_root=True,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    with open(output_file, encoding='utf-8') as f:
        sentences = conllu.parse(f.read())
    # Second token should be changed to AUX
    assert sentences[0][1]['upos'] == 'AUX'


def test_safe_typed_labels_converted(
    temp_dir: Path,
    brat_input_dir: Path,
    reference_conllu_file: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test that safe-typed labels are converted back to special chars."""
    brat_to_conllu(
        brat_input_dir,
        temp_dir / 'output',
        feature_set,
        ref_conllu=reference_conllu_file,
        sents_per_doc=1,
        output_root=True,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    with open(output_file, encoding='utf-8') as f:
        sentences = conllu.parse(f.read())

    # Should be converted back to nsubj:pass
    assert sentences[0][0]['deprel'] == 'nsubj:pass'
