"""Tests for BRAT file I/O operations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from nlp_utilities.brat.utils import (
    read_annotations,
    read_text_lines,
    write_annotations,
    write_auxiliary_files,
    write_text,
)


def test_read_annotations_with_entities_only(temp_dir: Path) -> None:
    """Test reading .ann file with entities only."""
    ann_file = temp_dir / 'test.ann'
    content = 'T1\tNOUN 0 5\tWord\nT2\tVERB 6 10\ttest\n'
    ann_file.write_text(content, encoding='utf-8')

    annotations = read_annotations(str(ann_file))
    assert len(annotations) == 2  # noqa: PLR2004
    assert annotations[0]['type'] == 'T'
    assert annotations[1]['type'] == 'T'


def test_read_annotations_with_relations_only(temp_dir: Path) -> None:
    """Test reading .ann file with relations only."""
    ann_file = temp_dir / 'test.ann'
    content = 'R1\tnsubj Arg1:T2 Arg2:T1\nR2\troot Arg1:T0 Arg2:T2\n'
    ann_file.write_text(content, encoding='utf-8')

    annotations = read_annotations(str(ann_file))
    assert len(annotations) == 2  # noqa: PLR2004
    assert annotations[0]['type'] == 'R'
    assert annotations[1]['type'] == 'R'


def test_read_annotations_mixed(temp_dir: Path) -> None:
    """Test reading .ann file with mixed entities and relations."""
    ann_file = temp_dir / 'test.ann'
    content = 'T1\tNOUN 0 5\tWord\nR1\tnsubj Arg1:T2 Arg2:T1\nT2\tVERB 6 10\ttest\n'
    ann_file.write_text(content, encoding='utf-8')

    annotations = read_annotations(str(ann_file))
    assert len(annotations) == 3  # noqa: PLR2004


def test_read_annotations_empty_file(temp_dir: Path) -> None:
    """Test reading empty .ann file."""
    ann_file = temp_dir / 'empty.ann'
    ann_file.write_text('', encoding='utf-8')

    annotations = read_annotations(str(ann_file))
    assert len(annotations) == 0


def test_read_annotations_with_blank_lines(temp_dir: Path) -> None:
    """Test reading .ann file with blank lines."""
    ann_file = temp_dir / 'test.ann'
    content = 'T1\tNOUN 0 5\tWord\n\nT2\tVERB 6 10\ttest\n'
    ann_file.write_text(content, encoding='utf-8')

    annotations = read_annotations(str(ann_file))
    assert len(annotations) == 2  # noqa: PLR2004


def test_read_annotations_with_malformed_lines(temp_dir: Path) -> None:
    """Test reading .ann file with malformed lines (should skip gracefully)."""
    ann_file = temp_dir / 'test.ann'
    content = 'T1\tNOUN 0 5\tWord\nBADLINE\nT2\tVERB 6 10\ttest\n'
    ann_file.write_text(content, encoding='utf-8')

    annotations = read_annotations(str(ann_file))
    assert len(annotations) == 2  # noqa: PLR2004


def test_read_annotations_with_unicode(temp_dir: Path) -> None:
    """Test reading .ann file with Unicode characters."""
    ann_file = temp_dir / 'unicode.ann'
    content = 'T1\tNOUN 0 5\tναός\n'  # noqa: RUF001
    ann_file.write_text(content, encoding='utf-8')

    annotations = read_annotations(str(ann_file))
    assert len(annotations) == 1
    assert annotations[0]['form'] == 'ναός'


def test_read_annotations_nonexistent_file() -> None:
    """Test reading non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        read_annotations('/nonexistent/file.ann')


def test_read_text_lines_valid(temp_dir: Path) -> None:
    """Test reading valid .txt file."""
    txt_file = temp_dir / 'test.txt'
    content = 'Word test'
    txt_file.write_text(content, encoding='utf-8')

    lines = read_text_lines(str(txt_file))
    assert len(lines) == 1
    assert lines[0] == 'Word test'


def test_read_text_lines_empty(temp_dir: Path) -> None:
    """Test reading empty .txt file."""
    txt_file = temp_dir / 'empty.txt'
    txt_file.write_text('', encoding='utf-8')

    lines = read_text_lines(str(txt_file))
    assert len(lines) == 0


def test_read_text_lines_multiline(temp_dir: Path) -> None:
    """Test reading multi-line .txt file."""
    txt_file = temp_dir / 'multi.txt'
    content = 'Line one\nLine two\nLine three'
    txt_file.write_text(content, encoding='utf-8')

    lines = read_text_lines(str(txt_file))
    assert len(lines) == 3  # noqa: PLR2004


def test_read_text_lines_unicode(temp_dir: Path) -> None:
    """Test reading .txt file with Unicode text."""
    txt_file = temp_dir / 'unicode.txt'
    content = 'ναός τέμπλο'
    txt_file.write_text(content, encoding='utf-8')

    lines = read_text_lines(str(txt_file))
    assert lines[0] == 'ναός τέμπλο'


def test_read_text_lines_nonexistent_file() -> None:
    """Test reading non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        read_text_lines('/nonexistent/file.txt')


def test_write_annotations_entities(temp_dir: Path) -> None:
    """Test writing entities to new file."""
    annotations: list[dict[str, Any]] = [
        {'type': 'T', 'id': 1, 'upos': 'NOUN', 'start': 0, 'end': 5, 'form': 'Word'},
        {'type': 'T', 'id': 2, 'upos': 'VERB', 'start': 6, 'end': 10, 'form': 'test'},
    ]
    output_file = temp_dir / 'output.ann'

    write_annotations(output_file, annotations)

    assert output_file.exists()
    content = output_file.read_text(encoding='utf-8')
    assert 'T1\tNOUN 0 5\tWord' in content
    assert 'T2\tVERB 6 10\ttest' in content


def test_write_annotations_relations(temp_dir: Path) -> None:
    """Test writing relations to new file."""
    annotations: list[dict[str, Any]] = [
        {'type': 'R', 'id': 1, 'deprel': 'nsubj', 'head': 2, 'dep': 1},
    ]
    output_file = temp_dir / 'output.ann'

    write_annotations(output_file, annotations)

    assert output_file.exists()
    content = output_file.read_text(encoding='utf-8')
    assert 'R1\tnsubj Arg1:T2 Arg2:T1' in content


def test_write_annotations_mixed(temp_dir: Path) -> None:
    """Test writing mixed annotations to new file."""
    annotations: list[dict[str, Any]] = [
        {'type': 'T', 'id': 1, 'upos': 'NOUN', 'start': 0, 'end': 5, 'form': 'Word'},
        {'type': 'R', 'id': 1, 'deprel': 'nsubj', 'head': 'T2', 'dep': 'T1'},
        {'type': 'T', 'id': 2, 'upos': 'VERB', 'start': 6, 'end': 10, 'form': 'test'},
    ]
    output_file = temp_dir / 'output.ann'

    write_annotations(output_file, annotations)

    # Verify annotations are sorted (T before R)
    lines = output_file.read_text(encoding='utf-8').strip().split('\n')
    assert lines[0].startswith('T1')
    assert lines[1].startswith('T2')
    assert lines[2].startswith('R1')


def test_write_annotations_with_path_object(temp_dir: Path) -> None:
    """Test writing with Path object."""
    annotations: list[dict[str, Any]] = [
        {'type': 'T', 'id': 1, 'upos': 'NOUN', 'start': 0, 'end': 5, 'form': 'Word'},
    ]
    output_file = temp_dir / 'output.ann'

    write_annotations(output_file, annotations)

    assert output_file.exists()


def test_write_annotations_with_string_path(temp_dir: Path) -> None:
    """Test writing with string path."""
    annotations: list[dict[str, Any]] = [
        {'type': 'T', 'id': 1, 'upos': 'NOUN', 'start': 0, 'end': 5, 'form': 'Word'},
    ]
    output_file = temp_dir / 'output.ann'

    write_annotations(str(output_file), annotations)

    assert output_file.exists()


def test_write_text_simple(temp_dir: Path) -> None:
    """Test writing simple text."""
    doctext = ['Word', 'test']
    output_file = temp_dir / 'output.txt'
    write_text(output_file, doctext)
    assert output_file.exists()
    content = output_file.read_text(encoding='utf-8')
    assert content == 'Word\ntest\n'


def test_write_text_empty(temp_dir: Path) -> None:
    """Test writing empty text list."""
    doctext: list[str] = []
    output_file = temp_dir / 'output.txt'

    write_text(output_file, doctext)

    assert output_file.exists()
    content = output_file.read_text(encoding='utf-8')
    assert content == '\n'


def test_write_text_with_path_object(temp_dir: Path) -> None:
    """Test writing text with Path object."""
    doctext = ['test']
    output_file = temp_dir / 'output.txt'

    write_text(output_file, doctext)

    assert output_file.exists()


def test_write_text_with_string_path(temp_dir: Path) -> None:
    """Test writing text with string path."""
    doctext = ['test']
    output_file = temp_dir / 'output.txt'

    write_text(str(output_file), doctext)

    assert output_file.exists()


def test_write_auxiliary_files(temp_dir: Path) -> None:
    """Test writing auxiliary files to output directory."""
    metadata = {
        'conllu_filename': 'test.conllu',
        'sents_per_doc': 5,
        'output_root': True,
    }

    write_auxiliary_files(str(temp_dir), metadata)

    # Check configuration files
    assert (temp_dir / 'annotation.conf').exists()
    assert (temp_dir / 'tools.conf').exists()
    assert (temp_dir / 'visual.conf').exists()

    # Check metadata file
    metadata_file = temp_dir / 'metadata.json'
    assert metadata_file.exists()
    loaded_metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
    assert loaded_metadata['conllu_filename'] == 'test.conllu'
    assert loaded_metadata['sents_per_doc'] == 5  # noqa: PLR2004
    assert loaded_metadata['output_root'] is True


def test_write_auxiliary_files_requires_existing_directory(temp_dir: Path) -> None:
    """Test that write_auxiliary_files requires directory to exist."""
    new_dir = temp_dir / 'new_output'
    metadata = {
        'conllu_filename': 'test.conllu',
        'sents_per_doc': 1,
        'output_root': False,
    }

    # Directory doesn't exist - should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        write_auxiliary_files(str(new_dir), metadata)
