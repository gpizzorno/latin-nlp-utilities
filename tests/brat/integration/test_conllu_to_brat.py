"""Integration tests for BRAT module round-trip conversions: CoNLL-U → BRAT."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from nlp_utilities.brat.brat_to_conllu import brat_to_conllu
from nlp_utilities.brat.conllu_to_brat import conllu_to_brat


def test_simple_sentence_preserves_structure(
    temp_dir: Path,
    simple_conllu_content: str,
    feature_set: dict[str, Any],
) -> None:
    """Test that a simple sentence converts and back without changes."""
    # Create original CoNLL-U file
    original_conllu = temp_dir / 'original.conllu'
    original_conllu.write_text(simple_conllu_content, encoding='utf-8')

    # Convert CoNLL-U → BRAT
    brat_dir = temp_dir / 'brat'
    conllu_to_brat(
        conllu_filename=str(original_conllu),
        output_directory=str(brat_dir),
        output_root=True,
        sents_per_doc=None,
    )

    # Verify BRAT files were created
    assert (brat_dir / 'original.ann').exists()
    assert (brat_dir / 'original.txt').exists()

    # Convert BRAT → CoNLL-U
    roundtrip_conllu = temp_dir / 'original.conllu'
    brat_to_conllu(
        input_directory=str(brat_dir),
        output_directory=str(temp_dir),
        ref_conllu=str(original_conllu),
        feature_set=feature_set,
        output_root=True,
        sents_per_doc=None,
    )

    # Read both CoNLL-U files
    original_text = original_conllu.read_text(encoding='utf-8')
    roundtrip_text = roundtrip_conllu.read_text(encoding='utf-8')

    # Parse and compare (ignoring formatting differences)
    original_lines = [line.strip() for line in original_text.split('\n') if line.strip() and not line.startswith('#')]
    roundtrip_lines = [line.strip() for line in roundtrip_text.split('\n') if line.strip() and not line.startswith('#')]

    # Compare structure
    assert len(original_lines) == len(roundtrip_lines)

    # Compare content line by line
    for orig, rtrip in zip(original_lines, roundtrip_lines):
        # Split into fields and compare
        orig_fields = orig.split('\t')
        rtrip_fields = rtrip.split('\t')
        assert len(orig_fields) == len(rtrip_fields)
        # Compare ID, FORM, UPOS, HEAD, DEPREL
        assert orig_fields[0] == rtrip_fields[0]  # ID
        assert orig_fields[1] == rtrip_fields[1]  # FORM
        assert orig_fields[3] == rtrip_fields[3]  # UPOS
        assert orig_fields[6] == rtrip_fields[6]  # HEAD
        assert orig_fields[7] == rtrip_fields[7]  # DEPREL


def test_multi_sentence_preserves_all_sentences(
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test that multiple sentences are preserved in round-trip conversion."""
    # Create multi-sentence CoNLL-U
    multi_conllu_content = """# sent_id = 1
1	Word	word	NOUN	_	_	2	nsubj	_	_
2	test	test	VERB	_	_	0	root	_	_

# sent_id = 2
1	Another	another	DET	_	_	2	det	_	_
2	sentence	sentence	NOUN	_	_	0	root	_	_

"""
    original_conllu = temp_dir / 'multi.conllu'
    original_conllu.write_text(multi_conllu_content, encoding='utf-8')

    # Convert CoNLL-U → BRAT
    brat_dir = temp_dir / 'brat'
    conllu_to_brat(
        conllu_filename=str(original_conllu),
        output_directory=str(brat_dir),
        output_root=True,
        sents_per_doc=None,
    )

    # Convert BRAT → CoNLL-U
    roundtrip_conllu = temp_dir / 'multi.conllu'
    brat_to_conllu(
        input_directory=str(brat_dir),
        output_directory=str(temp_dir),
        ref_conllu=str(original_conllu),
        feature_set=feature_set,
        output_root=True,
        sents_per_doc=None,
    )

    # Count sentences in both files
    original_sent_count = multi_conllu_content.count('# sent_id =')
    roundtrip_text = roundtrip_conllu.read_text(encoding='utf-8')
    roundtrip_sent_count = roundtrip_text.count('# sent_id =')

    assert original_sent_count == roundtrip_sent_count


def test_without_root_preserves_dependencies(
    temp_dir: Path,
    simple_conllu_content: str,
    feature_set: dict[str, Any],
) -> None:
    """Test round-trip conversion without ROOT nodes."""
    # Create original CoNLL-U file
    original_conllu = temp_dir / 'no_root.conllu'
    original_conllu.write_text(simple_conllu_content, encoding='utf-8')

    # Convert CoNLL-U → BRAT (no ROOT)
    brat_dir = temp_dir / 'brat'
    conllu_to_brat(
        conllu_filename=str(original_conllu),
        output_directory=str(brat_dir),
        output_root=False,
        sents_per_doc=None,
    )

    # Verify ROOT is not in BRAT annotations
    ann_text = (brat_dir / 'no_root.ann').read_text(encoding='utf-8')
    assert 'ROOT' not in ann_text

    # Convert BRAT → CoNLL-U (no ROOT)
    roundtrip_conllu = temp_dir / 'no_root.conllu'
    brat_to_conllu(
        input_directory=str(brat_dir),
        output_directory=str(temp_dir),
        ref_conllu=str(original_conllu),
        feature_set=feature_set,
        output_root=False,
        sents_per_doc=None,
    )

    # Read and compare
    original_text = original_conllu.read_text(encoding='utf-8')
    roundtrip_text = roundtrip_conllu.read_text(encoding='utf-8')

    # Parse dependencies
    original_lines = [line for line in original_text.split('\n') if line and not line.startswith('#')]
    roundtrip_lines = [line for line in roundtrip_text.split('\n') if line and not line.startswith('#')]

    # Compare HEAD and DEPREL columns
    for orig, rtrip in zip(original_lines, roundtrip_lines):
        orig_fields = orig.split('\t')
        rtrip_fields = rtrip.split('\t')
        assert orig_fields[6] == rtrip_fields[6]  # HEAD
        assert orig_fields[7] == rtrip_fields[7]  # DEPREL


def test_with_document_splitting(
    temp_dir: Path,
    feature_set: dict[str, Any],
) -> None:
    """Test round-trip conversion with document splitting."""
    # Create multi-sentence CoNLL-U file
    multi_conllu_content = """# sent_id = 1
1	Word	word	NOUN	_	_	0	root	_	_

# sent_id = 2
1	Test	test	NOUN	_	_	0	root	_	_

"""
    original_conllu = temp_dir / 'split.conllu'
    original_conllu.write_text(multi_conllu_content, encoding='utf-8')

    # Convert CoNLL-U → BRAT with splitting
    brat_dir = temp_dir / 'brat'
    conllu_to_brat(
        conllu_filename=str(original_conllu),
        output_directory=str(brat_dir),
        output_root=True,
        sents_per_doc=1,  # One sentence per document
    )

    # Verify multiple BRAT files were created
    brat_files = list(brat_dir.glob('*.ann'))
    assert len(brat_files) > 1

    # Convert BRAT → CoNLL-U
    roundtrip_conllu = temp_dir / 'split.conllu'
    brat_to_conllu(
        input_directory=str(brat_dir),
        output_directory=str(temp_dir),
        ref_conllu=str(original_conllu),
        feature_set=feature_set,
        output_root=True,
        sents_per_doc=1,
    )

    # Count sentences
    original_sent_count = multi_conllu_content.count('# sent_id =')
    roundtrip_text = roundtrip_conllu.read_text(encoding='utf-8')
    roundtrip_sent_count = roundtrip_text.count('# sent_id =')

    assert original_sent_count == roundtrip_sent_count
