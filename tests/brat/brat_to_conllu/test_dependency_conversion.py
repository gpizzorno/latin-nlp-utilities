"""Tests for dependency conversion features."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import conllu

from nlp_utilities.brat.brat_to_conllu import brat_to_conllu


def test_aux_deprel_changes_upos_to_aux(
    temp_dir: Path,
    reference_conllu_file: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test that aux deprel changes UPOS to AUX."""
    # Create BRAT with aux relation
    brat_dir = temp_dir / 'brat_aux'
    brat_dir.mkdir()
    ann_content = """T0\tROOT 0 0\tROOT
T1\tVERB 0 4\tWord
T2\tVERB 5 9\ttest
R1\taux Arg1:T2 Arg2:T1
"""
    (brat_dir / 'test.ann').write_text(ann_content, encoding='utf-8')
    (brat_dir / 'test.txt').write_text('Word test', encoding='utf-8')

    brat_to_conllu(
        brat_dir,
        temp_dir / 'output',
        feature_set,
        ref_conllu=reference_conllu_file,
        sents_per_doc=1,
        output_root=False,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    with open(output_file, encoding='utf-8') as f:
        sentences = conllu.parse(f.read())

    # First token should be changed to AUX
    assert sentences[0][0]['upos'] == 'AUX'


def test_safe_typed_labels_converted(
    temp_dir: Path,
    reference_conllu_file: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test that safe-typed labels are converted back to special chars."""
    # Create BRAT with safe-typed deprel
    brat_dir = temp_dir / 'brat_safe'
    brat_dir.mkdir()
    ann_content = """T0\tROOT 0 0\tROOT
T1\tNOUN 0 4\tWord
T2\tVERB 5 9\ttest
R1\tnsubj_colon_pass Arg1:T2 Arg2:T1
"""
    (brat_dir / 'test.ann').write_text(ann_content, encoding='utf-8')
    (brat_dir / 'test.txt').write_text('Word test', encoding='utf-8')

    brat_to_conllu(
        brat_dir,
        temp_dir / 'output',
        feature_set,
        ref_conllu=reference_conllu_file,
        sents_per_doc=1,
        output_root=False,
    )

    output_file = temp_dir / 'output' / f'{reference_conllu_file.stem}-from_brat.conllu'
    with open(output_file, encoding='utf-8') as f:
        sentences = conllu.parse(f.read())

    # Should be converted back to nsubj:pass
    assert sentences[0][0]['deprel'] == 'nsubj:pass'
