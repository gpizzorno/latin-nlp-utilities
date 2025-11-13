"""Tests for handling special characters in labels."""

from __future__ import annotations

from pathlib import Path

from nlp_utilities.brat.conllu_to_brat import conllu_to_brat


def test_upos_with_special_chars_converted(temp_dir: Path) -> None:
    """Test that UPOS with special characters is converted to safe type."""
    conllu_content = """# sent_id = 1
1	test	test	NOUN:special	n	_	0	root	_	_

"""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(conllu_file), str(output_dir))

    ann_content = (output_dir / 'test.ann').read_text(encoding='utf-8')

    # Colon should be converted to _colon_
    assert 'NOUN_colon_special' in ann_content


def test_deprel_with_special_chars_converted(temp_dir: Path) -> None:
    """Test that deprel with special characters is converted to safe type."""
    conllu_content = """# sent_id = 1
1	Word	word	NOUN	n	_	2	nsubj:pass	_	_
2	test	test	VERB	v	_	0	root	_	_

"""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(conllu_file), str(output_dir))

    ann_content = (output_dir / 'test.ann').read_text(encoding='utf-8')

    # Colon should be converted to _colon_
    assert 'nsubj_colon_pass' in ann_content
