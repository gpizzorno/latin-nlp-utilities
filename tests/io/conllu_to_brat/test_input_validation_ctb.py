"""Tests for input validation in conllu_to_brat function."""

from __future__ import annotations

from pathlib import Path

import pytest

from conllu_tools.io import conllu_to_brat


def test_missing_conllu_file(temp_dir: Path) -> None:
    """Test that FileNotFoundError is raised for non-existent CoNLL-U file."""
    nonexistent = temp_dir / 'nonexistent.conllu'
    output_dir = temp_dir / 'output'

    with pytest.raises(FileNotFoundError, match='Input CONLLU file not found'):
        conllu_to_brat(str(nonexistent), str(output_dir))


def test_creates_output_directory(
    temp_dir: Path,
    simple_conllu_content: str,
) -> None:
    """Test that output directory is created if it doesn't exist."""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(simple_conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    assert not output_dir.exists()

    conllu_to_brat(str(conllu_file), str(output_dir))

    assert output_dir.exists()
    assert output_dir.is_dir()


def test_handles_string_paths(
    temp_dir: Path,
    simple_conllu_content: str,
) -> None:
    """Test that function accepts string paths."""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(simple_conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    # Should not raise any errors
    conllu_to_brat(str(conllu_file), str(output_dir))

    assert (output_dir / 'test.ann').exists()


def test_skip_tokens_with_underscore_head(temp_dir: Path) -> None:
    """Test that tokens with HEAD='_' are skipped in relations."""
    conllu_content = """# sent_id = 1
1	Word	word	NOUN	n	_	_	_	_	_
2	test	test	VERB	v	_	0	root	_	_

"""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(conllu_file), str(output_dir))

    ann_content = (output_dir / 'test.ann').read_text(encoding='utf-8')

    # Should only have root relation, not one for Word
    relation_count = ann_content.count('\nR')
    assert relation_count == 1  # Only R1 (root)
