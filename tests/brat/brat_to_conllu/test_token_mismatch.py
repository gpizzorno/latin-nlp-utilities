"""Tests for token mismatch error handling."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest

from nlp_utilities.brat.brat_to_conllu import brat_to_conllu
from tests.test_data.load_data import SIMPLE_ANN, SIMPLE_TXT


def test_token_count_mismatch(
    temp_dir: Path,
    reference_conllu_file: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test error when token counts don't match."""
    # Create BRAT with wrong number of tokens
    brat_dir = temp_dir / 'brat_mismatch'
    brat_dir.mkdir()
    ann_content = """T1\tNOUN 0 4\tWord
"""
    (brat_dir / 'test.ann').write_text(ann_content, encoding='utf-8')
    (brat_dir / 'test.txt').write_text('Word', encoding='utf-8')

    with pytest.raises(ValueError, match='Sentence length mismatch'):
        brat_to_conllu(
            brat_dir,
            temp_dir / 'output',
            feature_set,
            ref_conllu=reference_conllu_file,
            sents_per_doc=1,
            output_root=False,
        )


def test_token_form_mismatch(
    temp_dir: Path,
    reference_conllu_file: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test error when token forms don't match."""
    # Create BRAT with different token
    brat_dir = temp_dir / 'brat_form_mismatch'
    brat_dir.mkdir()
    ann_content = copy.deepcopy(SIMPLE_ANN).replace('Gallia', 'Numidia')
    (brat_dir / 'test.ann').write_text(ann_content, encoding='utf-8')
    (brat_dir / 'test.txt').write_text(SIMPLE_TXT, encoding='utf-8')

    with pytest.raises(ValueError, match='Token mismatch'):
        brat_to_conllu(
            brat_dir,
            temp_dir / 'output',
            feature_set,
            ref_conllu=reference_conllu_file,
            sents_per_doc=1,
            output_root=False,
        )
