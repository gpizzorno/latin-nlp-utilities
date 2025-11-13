"""Tests for ROOT node handling."""

from __future__ import annotations

from pathlib import Path

from nlp_utilities.brat.conllu_to_brat import conllu_to_brat


def test_root_node_added_when_enabled(
    temp_dir: Path,
    simple_conllu_content: str,
) -> None:
    """Test that explicit ROOT node is added when output_root=True."""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(simple_conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(conllu_file), str(output_dir), output_root=True)

    ann_content = (output_dir / 'test.ann').read_text(encoding='utf-8')

    # Should have ROOT node (with span 0 0, but gets sequential ID now)
    assert 'ROOT 0 4\tROOT' in ann_content


def test_root_node_skipped_when_disabled(
    temp_dir: Path,
    simple_conllu_content: str,
) -> None:
    """Test that ROOT node is not added when output_root=False."""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(simple_conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(conllu_file), str(output_dir), output_root=False)

    ann_content = (output_dir / 'test.ann').read_text(encoding='utf-8')

    # Should NOT have ROOT node
    assert 'ROOT' not in ann_content


def test_root_dependencies_skipped_when_disabled(
    temp_dir: Path,
    simple_conllu_content: str,
) -> None:
    """Test that dependencies to root are skipped when output_root=False."""
    conllu_file = temp_dir / 'test.conllu'
    conllu_file.write_text(simple_conllu_content, encoding='utf-8')
    output_dir = temp_dir / 'output'

    conllu_to_brat(str(conllu_file), str(output_dir), output_root=False)

    ann_content = (output_dir / 'test.ann').read_text(encoding='utf-8')

    # Should only have nsubj relation, not root relation
    assert 'nsubj' in ann_content
    assert 'root' not in ann_content.lower() or 'R' not in ann_content.split('root')[0][-5:]
