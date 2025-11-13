"""File Loading Tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from nlp_utilities.conllu.evaluators import UDEvaluator
from nlp_utilities.conllu.evaluators.base import UDError

if TYPE_CHECKING:
    from _pytest.tmpdir import TempPathFactory


def test_evaluate_files_with_path_objects(tmp_path_factory: TempPathFactory) -> None:
    """Test evaluate_files with Path objects."""
    tmp_dir = tmp_path_factory.mktemp('test_files')

    gold_content = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    system_content = gold_content

    gold_file = tmp_dir / 'gold.conllu'
    system_file = tmp_dir / 'system.conllu'

    gold_file.write_text(gold_content)
    system_file.write_text(system_content)

    evaluator = UDEvaluator()
    scores = evaluator.evaluate_files(gold_file, system_file)

    assert isinstance(scores, dict)
    assert 'Tokens' in scores
    assert 'Words' in scores


def test_evaluate_files_with_string_paths(tmp_path_factory: TempPathFactory) -> None:
    """Test evaluate_files with string paths."""
    tmp_dir = tmp_path_factory.mktemp('test_files')

    gold_content = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    system_content = gold_content

    gold_file = tmp_dir / 'gold.conllu'
    system_file = tmp_dir / 'system.conllu'

    gold_file.write_text(gold_content)
    system_file.write_text(system_content)

    evaluator = UDEvaluator()
    scores = evaluator.evaluate_files(str(gold_file), str(system_file))

    assert isinstance(scores, dict)


def test_evaluate_files_with_nonexistent_file() -> None:
    """Test evaluate_files with non-existent file."""
    evaluator = UDEvaluator()

    with pytest.raises(FileNotFoundError):
        evaluator.evaluate_files('/nonexistent/gold.conllu', '/nonexistent/system.conllu')


def test_evaluate_files_with_empty_file(tmp_path_factory: TempPathFactory) -> None:
    """Test evaluate_files with empty files."""
    tmp_dir = tmp_path_factory.mktemp('test_files')

    gold_file = tmp_dir / 'gold.conllu'
    system_file = tmp_dir / 'system.conllu'

    gold_file.write_text('')
    system_file.write_text('')

    evaluator = UDEvaluator()
    scores = evaluator.evaluate_files(gold_file, system_file)

    # Empty files should have 0 sentences
    assert scores['Sentences'].gold_total == 0
    assert scores['Sentences'].system_total == 0


def test_evaluate_files_with_utf8_encoding(tmp_path_factory: TempPathFactory) -> None:
    """Test evaluate_files with UTF-8 encoded files."""
    tmp_dir = tmp_path_factory.mktemp('test_files')

    # Content with Latin characters and diacritics
    gold_content = """# sent_id = 1
# text = puella cantat
1\tpuella\tpuella\tNOUN\t_\tCase=Nom|Gender=Fem|Number=Sing\t2\tnsubj\t_\t_
2\tcantat\tcanto\tVERB\t_\tMood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act\t0\troot\t_\t_

"""
    system_content = gold_content

    gold_file = tmp_dir / 'gold.conllu'
    system_file = tmp_dir / 'system.conllu'

    gold_file.write_text(gold_content, encoding='utf-8')
    system_file.write_text(system_content, encoding='utf-8')

    evaluator = UDEvaluator()
    scores = evaluator.evaluate_files(gold_file, system_file)

    # Perfect match should have F1=1.0
    assert scores['Words'].f1 == 1.0


def test_evaluate_files_with_mismatched_sentence_counts(tmp_path_factory: TempPathFactory) -> None:
    """Test evaluate_files raises UDError when sentence counts don't match."""
    tmp_dir = tmp_path_factory.mktemp('test_files')

    gold_content = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    system_content = (
        gold_content
        + """# sent_id = 2
# text = The dog
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tdog\tdog\tNOUN\t_\t_\t0\troot\t_\t_

"""
    )

    gold_file = tmp_dir / 'gold.conllu'
    system_file = tmp_dir / 'system.conllu'

    gold_file.write_text(gold_content)
    system_file.write_text(system_content)

    evaluator = UDEvaluator()

    with pytest.raises(UDError, match=r'sentence.*mismatch'):
        evaluator.evaluate_files(gold_file, system_file)
