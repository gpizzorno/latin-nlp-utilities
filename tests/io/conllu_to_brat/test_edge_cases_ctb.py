"""Tests for edge cases and error conditions."""

from __future__ import annotations

from pathlib import Path

from conllu_tools.io import conllu_to_brat


def test_empty_conllu_file(temp_dir: Path) -> None:
    """Test handling of empty CoNLL-U file."""
    conllu_file = temp_dir / 'empty.conllu'
    conllu_file.write_text('', encoding='utf-8')
    output_dir = temp_dir / 'output'

    # Should not crash
    conllu_to_brat(str(conllu_file), str(output_dir))

    # Should create metadata but no annotation files
    assert (output_dir / 'metadata.json').exists()


def test_sentence_with_no_dependencies(temp_dir: Path) -> None:
    """Test sentence where all tokens have HEAD='_'."""
    conllu_content = """# sent_id = 1
1	Word	word	NOUN	n	_	_	_	_	_

"""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(conllu_file), str(output_dir))

    ann_content = (output_dir / 'test.ann').read_text(encoding='utf-8')

    # Should have entities but no relations (except maybe ROOT)
    # T1 is ROOT, T2 is the NOUN token
    assert 'T2\tNOUN' in ann_content
    # Count R entries - should be 0 or minimal
    r_count = ann_content.count('\nR')
    assert r_count == 0


def test_missing_upos_defaults_to_x(temp_dir: Path) -> None:
    """Test that missing UPOS defaults to 'X'."""
    conllu_content = """# sent_id = 1
1	test	test	_	_	_	0	root	_	_

"""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(conllu_file), str(output_dir))

    ann_content = (output_dir / 'test.ann').read_text(encoding='utf-8')

    # Should default to X for missing UPOS (T1 is ROOT, T2 is the token)
    assert 'T2\tX' in ann_content


def test_missing_deprel_defaults_to_x(temp_dir: Path) -> None:
    """Test that missing deprel defaults to 'X'."""
    conllu_content = """# sent_id = 1
1	test	test	NOUN	n	_	0	_	_	_

"""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(conllu_file), str(output_dir))

    ann_content = (output_dir / 'test.ann').read_text(encoding='utf-8')

    # Should default to X for missing deprel
    assert 'R1\tX' in ann_content or 'R2\tX' in ann_content  # R1 might be root relation
