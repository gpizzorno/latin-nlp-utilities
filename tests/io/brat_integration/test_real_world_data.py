"""Test conversions with real-world corpus data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from conllu_tools.io import brat_to_conllu, conllu_to_brat


def test_conllu_to_brat_matches_expected_output(temp_dir: Path) -> None:
    """Test that brat_test.conllu converts to match test_output exactly."""
    # Path to test data
    test_data_dir = Path('tests/test_data/brat')
    source_conllu = test_data_dir / 'brat_test.conllu'
    expected_output_dir = test_data_dir / 'test_output'

    # Convert CoNLL-U to BRAT
    actual_output_dir = temp_dir / 'brat_output'
    conllu_to_brat(
        conllu_filename=str(source_conllu),
        output_directory=str(actual_output_dir),
        output_root=True,
        sents_per_doc=10,
    )

    # Compare each expected file with actual output
    expected_files = sorted(
        [f for f in expected_output_dir.iterdir() if f.suffix in {'.ann', '.txt'} and not f.name.startswith('.')],
    )

    for expected_file in expected_files:
        actual_file = actual_output_dir / expected_file.name
        assert actual_file.exists(), f'Missing file: {expected_file.name}'

        expected_content = expected_file.read_text(encoding='utf-8')
        actual_content = actual_file.read_text(encoding='utf-8')

        assert actual_content == expected_content, (
            f'Content mismatch in {expected_file.name}\n'
            f'Expected:\n{expected_content[:200]}...\n'
            f'Got:\n{actual_content[:200]}...'
        )

    # Verify all expected files were created (5 docs with .ann and .txt each)
    expected_file_count = 10
    assert len(expected_files) == expected_file_count


def test_brat_to_conllu_matches_original(temp_dir: Path, feature_set: dict[str, Any]) -> None:
    """Test that test_output converts back to match brat_test.conllu exactly."""
    # Path to test data
    test_data_dir = Path('tests/test_data/brat')
    brat_input_dir = test_data_dir / 'test_output'
    expected_conllu = test_data_dir / 'brat_test.conllu'

    # Convert BRAT to CoNLL-U
    brat_to_conllu(
        input_directory=str(brat_input_dir),
        output_directory=str(temp_dir),
        ref_conllu=str(expected_conllu),
        feature_set=feature_set,
        output_root=True,
        sents_per_doc=10,
    )

    # The output file will be named brat_test-from_brat.conllu
    actual_conllu = temp_dir / 'brat_test-from_brat.conllu'
    assert actual_conllu.exists(), 'Output CoNLL-U file was not created'

    # Read both files
    expected_content = expected_conllu.read_text(encoding='utf-8')
    actual_content = actual_conllu.read_text(encoding='utf-8')

    # Compare line by line (ignoring blank lines and comments for flexibility)
    expected_lines = [line for line in expected_content.split('\n') if line.strip() and not line.startswith('#')]
    actual_lines = [line for line in actual_content.split('\n') if line.strip() and not line.startswith('#')]

    assert len(expected_lines) == len(actual_lines), (
        f'Line count mismatch: expected {len(expected_lines)}, got {len(actual_lines)}'
    )

    # Compare key fields (ID, FORM, LEMMA, UPOS, HEAD, DEPREL)
    for i, (expected_line, actual_line) in enumerate(zip(expected_lines, actual_lines), 1):
        expected_fields = expected_line.split('\t')
        actual_fields = actual_line.split('\t')

        # ID (field 0)
        assert expected_fields[0] == actual_fields[0], f'Line {i}: ID mismatch'
        # FORM (field 1)
        assert expected_fields[1] == actual_fields[1], f'Line {i}: FORM mismatch'
        # LEMMA (field 2)
        assert expected_fields[2] == actual_fields[2], f'Line {i}: LEMMA mismatch'
        # UPOS (field 3)
        assert expected_fields[3] == actual_fields[3], f'Line {i}: UPOS mismatch'
        # XPOS (field 4)
        assert expected_fields[4] == actual_fields[4], f'Line {i}: XPOS mismatch'
        # FEATS (field 5)
        assert expected_fields[5] == actual_fields[5], f'Line {i}: FEATS mismatch'
        # HEAD (field 6)
        assert expected_fields[6] == actual_fields[6], f'Line {i}: HEAD mismatch'
        # DEPREL (field 7)
        assert expected_fields[7] == actual_fields[7], f'Line {i}: DEPREL mismatch'
        # DEPS (field 8)
        assert expected_fields[8] == actual_fields[8], f'Line {i}: DEPS mismatch'
        # MISC (field 9)
        assert expected_fields[9] == actual_fields[9], f'Line {i}: MISC mismatch'
