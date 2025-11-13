"""Tests for basic CoNLL-U to BRAT conversion."""

from __future__ import annotations

from pathlib import Path

from nlp_utilities.brat.conllu_to_brat import conllu_to_brat


def test_simple_sentence_conversion(
    temp_dir: Path,
    simple_conllu_content: str,
) -> None:
    """Test conversion of a simple single-sentence CoNLL-U file."""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(simple_conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(conllu_file), str(output_dir))

    ann_file = output_dir / 'test.ann'
    txt_file = output_dir / 'test.txt'

    assert ann_file.exists()
    assert txt_file.exists()


def test_entities_extracted_correctly(
    temp_dir: Path,
    simple_conllu_content: str,
) -> None:
    """Test that entities are extracted with correct attributes."""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(simple_conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(conllu_file), str(output_dir))

    ann_content = (output_dir / 'test.ann').read_text(encoding='utf-8')

    # Should have ROOT (T1), Word (T2), and test (T3)
    assert 'ROOT 0 4\tROOT' in ann_content
    assert 'T2\tNOUN' in ann_content
    assert 'Word' in ann_content
    assert 'T3\tVERB' in ann_content
    assert 'test' in ann_content


def test_relations_extracted_correctly(
    temp_dir: Path,
    simple_conllu_content: str,
) -> None:
    """Test that relations are extracted with correct IDs."""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(simple_conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(conllu_file), str(output_dir))

    ann_content = (output_dir / 'test.ann').read_text(encoding='utf-8')

    # Should have nsubj relation
    assert 'R1\tnsubj' in ann_content
    assert 'Arg1:T3' in ann_content  # head is T3 (test, was T2 before ROOT got sequential ID)
    assert 'Arg2:T2' in ann_content  # dep is T2 (Word, was T1 before ROOT got sequential ID)


def test_text_file_generated(
    temp_dir: Path,
    simple_conllu_content: str,
) -> None:
    """Test that text file is generated correctly."""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(simple_conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(conllu_file), str(output_dir))

    txt_content = (output_dir / 'test.txt').read_text(encoding='utf-8')

    assert 'Word test' in txt_content


def test_sequential_ids_assigned(
    temp_dir: Path,
    simple_conllu_content: str,
) -> None:
    """Test that sequential IDs are assigned to entities and relations."""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(simple_conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(conllu_file), str(output_dir))

    ann_content = (output_dir / 'test.ann').read_text(encoding='utf-8')

    # Entity IDs should be T1 (ROOT), T2, T3 (sequential IDs starting from 1)
    assert 'T1\t' in ann_content
    assert 'T2\t' in ann_content
    assert 'T3\t' in ann_content

    # Relation ID should be R1
    assert 'R1\t' in ann_content
