"""Tests for _get_annotations helper function."""

from __future__ import annotations

from pathlib import Path

from nlp_utilities.brat.brat_to_conllu import _get_annotations


def test_single_file_processing(temp_dir: Path) -> None:
    """Test loading annotations from single file."""
    ann_file = temp_dir / 'test.ann'
    ann_content = """T1\tNOUN 0 4\tWord
R1\tnsubj Arg1:T2 Arg2:T1
"""
    ann_file.write_text(ann_content, encoding='utf-8')
    txt_file = temp_dir / 'test.txt'
    txt_file.write_text('Word', encoding='utf-8')

    annotations, lines = _get_annotations([str(ann_file)])

    assert len(annotations) == 2
    assert len(lines) == 1


def test_multiple_file_processing(temp_dir: Path) -> None:
    """Test combining annotations from multiple files."""
    # Create first file
    ann1 = temp_dir / 'test1.ann'
    ann1.write_text('T1\tNOUN 0 4\tWord\n', encoding='utf-8')
    txt1 = temp_dir / 'test1.txt'
    txt1.write_text('Word', encoding='utf-8')

    # Create second file
    ann2 = temp_dir / 'test2.ann'
    ann2.write_text('T1\tVERB 0 4\ttest\n', encoding='utf-8')
    txt2 = temp_dir / 'test2.txt'
    txt2.write_text('test', encoding='utf-8')

    annotations, lines = _get_annotations([str(ann1), str(ann2)])

    assert len(annotations) == 2
    # Note: lines are concatenated
    assert len(lines) == 2


def test_offset_adjustment_multiple_files(temp_dir: Path) -> None:
    """Test that offsets are adjusted for multiple files."""
    # Create first file
    ann1 = temp_dir / 'test1.ann'
    ann1.write_text('T1\tNOUN 0 4\tWord\n', encoding='utf-8')
    txt1 = temp_dir / 'test1.txt'
    txt1.write_text('Word', encoding='utf-8')

    # Create second file
    ann2 = temp_dir / 'test2.ann'
    ann2.write_text('T1\tVERB 0 4\ttest\n', encoding='utf-8')
    txt2 = temp_dir / 'test2.txt'
    txt2.write_text('test', encoding='utf-8')

    annotations, _ = _get_annotations([str(ann1), str(ann2)])

    # First file should have original offsets
    t_anns = [a for a in annotations if a['type'] == 'T']
    assert t_anns[0]['start'] == 0
    assert t_anns[0]['end'] == 4

    # Second file should have adjusted offsets (4 chars from first file)
    assert t_anns[1]['start'] == 4
    assert t_anns[1]['end'] == 8


def test_id_collision_remapping(temp_dir: Path) -> None:
    """Test that ID collisions are detected and remapped."""
    # Create files with same IDs
    ann1 = temp_dir / 'test1.ann'
    ann1.write_text('T1\tNOUN 0 4\tWord\nR1\tnsubj Arg1:T2 Arg2:T1\n', encoding='utf-8')
    txt1 = temp_dir / 'test1.txt'
    txt1.write_text('Word', encoding='utf-8')

    ann2 = temp_dir / 'test2.ann'
    ann2.write_text('T1\tVERB 0 4\ttest\nR1\troot Arg1:T0 Arg2:T1\n', encoding='utf-8')
    txt2 = temp_dir / 'test2.txt'
    txt2.write_text('test', encoding='utf-8')

    annotations, _ = _get_annotations([str(ann1), str(ann2)])

    # Should have 4 annotations total (2 T, 2 R)
    t_anns = [a for a in annotations if a['type'] == 'T']
    r_anns = [a for a in annotations if a['type'] == 'R']

    assert len(t_anns) == 2
    assert len(r_anns) == 2

    # IDs should be unique
    t_ids = [a['id'] for a in t_anns]
    assert len(t_ids) == len(set(t_ids))


def test_relation_references_updated(temp_dir: Path) -> None:
    """Test that relation references are updated after ID remapping."""
    # Create files where second file has colliding IDs
    ann1 = temp_dir / 'test1.ann'
    ann1.write_text('T1\tNOUN 0 4\tWord\nT2\tVERB 5 9\ttest\nR1\tnsubj Arg1:T2 Arg2:T1\n', encoding='utf-8')
    txt1 = temp_dir / 'test1.txt'
    txt1.write_text('Word test', encoding='utf-8')

    ann2 = temp_dir / 'test2.ann'
    ann2.write_text('T1\tNOUN 0 3\tNew\nT2\tVERB 4 8\tword\nR1\tnsubj Arg1:T2 Arg2:T1\n', encoding='utf-8')
    txt2 = temp_dir / 'test2.txt'
    txt2.write_text('New word', encoding='utf-8')

    annotations, _ = _get_annotations([str(ann1), str(ann2)])

    # Get relations
    r_anns = [a for a in annotations if a['type'] == 'R']
    assert len(r_anns) == 2

    # Each relation should have valid head/dep references
    t_ids = {a['id'] for a in annotations if a['type'] == 'T'}
    for r_ann in r_anns:
        assert r_ann['head'] in t_ids
        assert r_ann['dep'] in t_ids


def test_empty_annotation_file(temp_dir: Path) -> None:
    """Test handling of empty annotation file."""
    ann_file = temp_dir / 'empty.ann'
    ann_file.write_text('', encoding='utf-8')
    txt_file = temp_dir / 'empty.txt'
    txt_file.write_text('', encoding='utf-8')

    annotations, lines = _get_annotations([str(ann_file)])

    assert len(annotations) == 0
    assert len(lines) == 0


def test_only_entities_no_relations(temp_dir: Path) -> None:
    """Test file with only entities (no relations)."""
    ann_file = temp_dir / 'entities.ann'
    ann_file.write_text('T1\tNOUN 0 4\tWord\nT2\tVERB 5 9\ttest\n', encoding='utf-8')
    txt_file = temp_dir / 'entities.txt'
    txt_file.write_text('Word test', encoding='utf-8')

    annotations, _ = _get_annotations([str(ann_file)])

    assert len(annotations) == 2
    assert all(a['type'] == 'T' for a in annotations)
