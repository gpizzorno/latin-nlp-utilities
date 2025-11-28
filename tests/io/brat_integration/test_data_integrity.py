"""Test that conversions don't lose or corrupt data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from conllu_tools.io import brat_to_conllu, conllu_to_brat


def test_no_data_loss_in_token_count(
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test that token count is preserved through conversions."""
    # Create single-sentence CoNLL-U (multi-sentence without ROOT delimiters would lose sentence boundaries)
    single_conllu_content = """# sent_id = 1
1	Word	word	NOUN	_	_	0	root	_	_
2	test	test	VERB	_	_	1	nsubj	_	_
3	sentence	sentence	NOUN	_	_	1	obj	_	_

"""
    original_conllu = temp_dir / 'original.conllu'
    original_conllu.write_text(single_conllu_content, encoding='utf-8')

    # Count tokens in original
    original_lines = [
        line for line in single_conllu_content.split('\n') if line and not line.startswith('#') and '\t' in line
    ]
    original_token_count = len(original_lines)

    # Round-trip: CoNLL-U → BRAT → CoNLL-U
    brat_dir = temp_dir / 'brat'
    conllu_to_brat(
        conllu_filename=str(original_conllu),
        output_directory=str(brat_dir),
        output_root=False,  # Don't add ROOT tokens
        sents_per_doc=None,
    )

    roundtrip_conllu = temp_dir / 'original.conllu'
    brat_to_conllu(
        input_directory=str(brat_dir),
        output_directory=str(temp_dir),
        ref_conllu=str(original_conllu),
        feature_set=feature_set,
        output_root=False,
        sents_per_doc=None,
    )

    # Count tokens in roundtrip
    roundtrip_text = roundtrip_conllu.read_text(encoding='utf-8')
    roundtrip_lines = [
        line for line in roundtrip_text.split('\n') if line and not line.startswith('#') and '\t' in line
    ]
    roundtrip_token_count = len(roundtrip_lines)

    assert original_token_count == roundtrip_token_count


def test_no_data_loss_in_dependency_count(
    temp_dir: Path,
    simple_conllu_content: str,
    feature_set: dict[str, Any],
) -> None:
    """Test that all dependencies are preserved."""
    # Create original CoNLL-U
    original_conllu = temp_dir / 'deps.conllu'
    original_conllu.write_text(simple_conllu_content, encoding='utf-8')

    # Count dependencies in original
    original_deps = [
        line.split('\t')[6]
        for line in simple_conllu_content.split('\n')
        if line and not line.startswith('#') and '\t' in line
    ]
    original_dep_count = sum(1 for dep in original_deps if dep != '0')

    # Round-trip
    brat_dir = temp_dir / 'brat'
    conllu_to_brat(
        conllu_filename=str(original_conllu),
        output_directory=str(brat_dir),
        output_root=True,
        sents_per_doc=None,
    )

    roundtrip_conllu = temp_dir / 'deps.conllu'
    brat_to_conllu(
        input_directory=str(brat_dir),
        output_directory=str(temp_dir),
        ref_conllu=str(original_conllu),
        feature_set=feature_set,
        output_root=True,
        sents_per_doc=None,
    )

    # Count dependencies in roundtrip
    roundtrip_text = roundtrip_conllu.read_text(encoding='utf-8')
    roundtrip_deps = [
        line.split('\t')[6] for line in roundtrip_text.split('\n') if line and not line.startswith('#') and '\t' in line
    ]
    roundtrip_dep_count = sum(1 for dep in roundtrip_deps if dep != '0')

    assert original_dep_count == roundtrip_dep_count


def test_metadata_preserved_through_conversions(
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test that metadata is preserved when round-tripping."""
    # Create CoNLL-U with metadata
    conllu_with_metadata = """# sent_id = test_1
# text = Word test
1	Word	word	NOUN	_	_	2	nsubj	_	_
2	test	test	VERB	_	_	0	root	_	_

"""
    original_conllu = temp_dir / 'meta.conllu'
    original_conllu.write_text(conllu_with_metadata, encoding='utf-8')

    # Round-trip
    brat_dir = temp_dir / 'brat'
    conllu_to_brat(
        conllu_filename=str(original_conllu),
        output_directory=str(brat_dir),
        output_root=True,
        sents_per_doc=None,
    )

    # Check metadata.json was created
    assert (brat_dir / 'metadata.json').exists()

    roundtrip_conllu = temp_dir / 'meta.conllu'
    brat_to_conllu(
        input_directory=str(brat_dir),
        output_directory=str(temp_dir),
        ref_conllu=str(original_conllu),
        feature_set=feature_set,
        output_root=True,
        sents_per_doc=None,
    )

    # Verify sent_id is preserved
    roundtrip_text = roundtrip_conllu.read_text(encoding='utf-8')
    assert 'sent_id' in roundtrip_text
