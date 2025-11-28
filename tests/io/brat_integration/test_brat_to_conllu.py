"""Integration tests for BRAT module round-trip conversions: BRAT → CoNLL-U."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from conllu_tools.io import brat_to_conllu, conllu_to_brat


def test_simple_annotation_preserves_entities(
    temp_dir: Path,
    simple_conllu_content: str,
    feature_set: dict[str, Any],
) -> None:
    """Test that entities are preserved in BRAT → CoNLL-U → BRAT conversion."""
    # First create a BRAT file from CoNLL-U
    original_conllu = temp_dir / 'source.conllu'
    original_conllu.write_text(simple_conllu_content, encoding='utf-8')

    brat_dir_1 = temp_dir / 'brat1'
    conllu_to_brat(
        conllu_filename=str(original_conllu),
        output_directory=str(brat_dir_1),
        output_root=True,
        sents_per_doc=None,
    )

    # Read original BRAT annotations
    original_ann = (brat_dir_1 / 'source.ann').read_text(encoding='utf-8')
    original_entities = [line for line in original_ann.split('\n') if line.startswith('T')]

    # Convert BRAT → CoNLL-U
    intermediate_conllu = temp_dir / 'source.conllu'
    brat_to_conllu(
        input_directory=str(brat_dir_1),
        output_directory=str(temp_dir),
        ref_conllu=str(original_conllu),
        feature_set=feature_set,
        output_root=True,
        sents_per_doc=None,
    )

    # Convert CoNLL-U → BRAT again
    brat_dir_2 = temp_dir / 'brat2'
    conllu_to_brat(
        conllu_filename=str(intermediate_conllu),
        output_directory=str(brat_dir_2),
        output_root=True,
        sents_per_doc=None,
    )

    # Read roundtrip BRAT annotations
    roundtrip_ann = (brat_dir_2 / 'source.ann').read_text(encoding='utf-8')
    roundtrip_entities = [line for line in roundtrip_ann.split('\n') if line.startswith('T')]

    # Compare entity counts
    assert len(original_entities) == len(roundtrip_entities)

    # Compare entity forms (ignore IDs and offsets which may differ)
    for orig, rtrip in zip(sorted(original_entities), sorted(roundtrip_entities)):
        orig_parts = orig.split('\t')
        rtrip_parts = rtrip.split('\t')
        # Compare form (last part)
        assert orig_parts[-1] == rtrip_parts[-1]


def test_preserves_relation_structure(
    temp_dir: Path,
    simple_conllu_content: str,
    feature_set: dict[str, Any],
) -> None:
    """Test that relations are preserved in round-trip conversion."""
    # Create initial BRAT from CoNLL-U
    original_conllu = temp_dir / 'source.conllu'
    original_conllu.write_text(simple_conllu_content, encoding='utf-8')

    brat_dir_1 = temp_dir / 'brat1'
    conllu_to_brat(
        conllu_filename=str(original_conllu),
        output_directory=str(brat_dir_1),
        output_root=True,
        sents_per_doc=None,
    )

    # Read original relations
    original_ann = (brat_dir_1 / 'source.ann').read_text(encoding='utf-8')
    original_relations = [line for line in original_ann.split('\n') if line.startswith('R')]

    # Round-trip: BRAT → CoNLL-U → BRAT
    intermediate_conllu = temp_dir / 'source.conllu'
    brat_to_conllu(
        input_directory=str(brat_dir_1),
        output_directory=str(temp_dir),
        ref_conllu=str(original_conllu),
        feature_set=feature_set,
        output_root=True,
        sents_per_doc=None,
    )

    brat_dir_2 = temp_dir / 'brat2'
    conllu_to_brat(
        conllu_filename=str(intermediate_conllu),
        output_directory=str(brat_dir_2),
        output_root=True,
        sents_per_doc=None,
    )

    # Read roundtrip relations
    roundtrip_ann = (brat_dir_2 / 'source.ann').read_text(encoding='utf-8')
    roundtrip_relations = [line for line in roundtrip_ann.split('\n') if line.startswith('R')]

    # Compare relation counts
    assert len(original_relations) == len(roundtrip_relations)


def test_preserves_text_content(
    temp_dir: Path,
    simple_conllu_content: str,
    feature_set: dict[str, Any],
) -> None:
    """Test that text content is preserved exactly."""
    # Create initial BRAT from CoNLL-U
    original_conllu = temp_dir / 'source.conllu'
    original_conllu.write_text(simple_conllu_content, encoding='utf-8')

    brat_dir_1 = temp_dir / 'brat1'
    conllu_to_brat(
        conllu_filename=str(original_conllu),
        output_directory=str(brat_dir_1),
        output_root=True,
        sents_per_doc=None,
    )

    # Read original text
    original_txt = (brat_dir_1 / 'source.txt').read_text(encoding='utf-8')

    # Round-trip: BRAT → CoNLL-U → BRAT
    intermediate_conllu = temp_dir / 'source.conllu'
    brat_to_conllu(
        input_directory=str(brat_dir_1),
        output_directory=str(temp_dir),
        ref_conllu=str(original_conllu),
        feature_set=feature_set,
        output_root=True,
        sents_per_doc=None,
    )

    brat_dir_2 = temp_dir / 'brat2'
    conllu_to_brat(
        conllu_filename=str(intermediate_conllu),
        output_directory=str(brat_dir_2),
        output_root=True,
        sents_per_doc=None,
    )

    # Read roundtrip text
    roundtrip_txt = (brat_dir_2 / 'source.txt').read_text(encoding='utf-8')

    # Compare text (should be identical)
    assert original_txt.strip() == roundtrip_txt.strip()
