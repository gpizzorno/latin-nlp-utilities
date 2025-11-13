"""Integration tests for error scenarios."""

from __future__ import annotations

from pathlib import Path

import pytest

from nlp_utilities.conllu.evaluators import UDEvaluator
from nlp_utilities.conllu.evaluators.base import UDError

# ============================================================================
# 6.3 Error Scenario Tests
# ============================================================================


def test_error_with_mismatched_sentence_counts(tmp_path: Path) -> None:
    """Test error is raised when sentence counts don't match."""
    # Create files with different sentence counts
    gold_file = tmp_path / 'gold.conllu'
    system_file = tmp_path / 'system.conllu'

    gold_text = """# sent_id = 1
# text = The cat.
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_
3\t.\t.\tPUNCT\t_\t_\t2\tpunct\t_\t_

# sent_id = 2
# text = A dog.
1\tA\ta\tDET\t_\t_\t2\tdet\t_\t_
2\tdog\tdog\tNOUN\t_\t_\t0\troot\t_\t_
3\t.\t.\tPUNCT\t_\t_\t2\tpunct\t_\t_

"""
    system_text = """# sent_id = 1
# text = The cat.
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_
3\t.\t.\tPUNCT\t_\t_\t2\tpunct\t_\t_

"""
    gold_file.write_text(gold_text, encoding='utf-8')
    system_file.write_text(system_text, encoding='utf-8')

    evaluator = UDEvaluator()

    with pytest.raises(UDError, match='Number of sentences mismatch'):
        evaluator.evaluate_files(gold_file, system_file)


def test_error_with_character_mismatch(tmp_path: Path) -> None:
    """Test error is raised when character sequences don't match."""
    # Create files with different text
    gold_file = tmp_path / 'gold.conllu'
    system_file = tmp_path / 'system.conllu'

    gold_text = """# sent_id = 1
# text = The cat.
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_
3\t.\t.\tPUNCT\t_\t_\t2\tpunct\t_\t_

"""
    system_text = """# sent_id = 1
# text = The dog.
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tdog\tdog\tNOUN\t_\t_\t0\troot\t_\t_
3\t.\t.\tPUNCT\t_\t_\t2\tpunct\t_\t_

"""
    gold_file.write_text(gold_text, encoding='utf-8')
    system_file.write_text(system_text, encoding='utf-8')

    evaluator = UDEvaluator()

    with pytest.raises(UDError, match='Text mismatch'):
        evaluator.evaluate_files(gold_file, system_file)


def test_error_messages_include_sentence_id(tmp_path: Path) -> None:
    """Test error messages include sentence ID for debugging."""
    gold_file = tmp_path / 'gold.conllu'
    system_file = tmp_path / 'system.conllu'

    gold_text = """# sent_id = sentence-001
# text = The cat.
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_
3\t.\t.\tPUNCT\t_\t_\t2\tpunct\t_\t_

"""
    system_text = """# sent_id = sentence-001
# text = The dog.
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tdog\tdog\tNOUN\t_\t_\t0\troot\t_\t_
3\t.\t.\tPUNCT\t_\t_\t2\tpunct\t_\t_

"""
    gold_file.write_text(gold_text, encoding='utf-8')
    system_file.write_text(system_text, encoding='utf-8')

    evaluator = UDEvaluator()

    with pytest.raises(UDError, match='sentence-001'):
        evaluator.evaluate_files(gold_file, system_file)


def test_error_message_shows_character_context(tmp_path: Path) -> None:
    """Test error message shows context around character mismatch."""
    gold_file = tmp_path / 'gold.conllu'
    system_file = tmp_path / 'system.conllu'

    gold_text = """# sent_id = 1
# text = The cat runs.
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t3\tnsubj\t_\t_
3\truns\trun\tVERB\t_\t_\t0\troot\t_\t_
4\t.\t.\tPUNCT\t_\t_\t3\tpunct\t_\t_

"""
    system_text = """# sent_id = 1
# text = The dog runs.
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tdog\tdog\tNOUN\t_\t_\t3\tnsubj\t_\t_
3\truns\trun\tVERB\t_\t_\t0\troot\t_\t_
4\t.\t.\tPUNCT\t_\t_\t3\tpunct\t_\t_

"""
    gold_file.write_text(gold_text, encoding='utf-8')
    system_file.write_text(system_text, encoding='utf-8')

    evaluator = UDEvaluator()

    with pytest.raises(UDError) as exc_info:
        evaluator.evaluate_files(gold_file, system_file)

    # Error message should show context
    error_msg = str(exc_info.value)
    assert 'cat' in error_msg or 'dog' in error_msg
