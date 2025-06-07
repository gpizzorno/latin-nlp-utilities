import io

import pytest

from utilities import evaluate_conllu


def test_process_enhanced_deps_basic():
    deps = '2:nsubj|0:root'
    result = evaluate_conllu.process_enhanced_deps(deps)
    assert result == [('2', ['nsubj']), ('0', ['root'])]


def test_process_enhanced_deps_multi_step():
    deps = '3:conj:en>obl:voor'
    result = evaluate_conllu.process_enhanced_deps(deps)
    assert result == [('3', ['conj:en', 'obl:voor'])]


def test_load_conllu_basic_sentence(conllu_stream, treebank_type):
    ud = evaluate_conllu.load_conllu(conllu_stream, treebank_type, eval_deprels=True)
    assert len(ud.words) == 4  # noqa: PLR2004
    assert len(ud.tokens) == 4  # noqa: PLR2004
    assert len(ud.sentences) == 1
    assert ud.characters == list('necabalio:')  # Should match the actual text in your fixture


def test_load_conllu_invalid_columns(treebank_type):
    file = io.StringIO('1\t \t_\t_\t_\t0\troot\t0:root\t_\n\n')
    with pytest.raises(evaluate_conllu.UDError):
        evaluate_conllu.load_conllu(file, treebank_type, eval_deprels=True)


def test_load_conllu_empty_form(treebank_type):
    file = io.StringIO('1\t \t_\t_\t_\t_\t0\troot\t0:root\t_\n\n')
    with pytest.raises(evaluate_conllu.UDError):
        evaluate_conllu.load_conllu(file, treebank_type, eval_deprels=True)


def test_load_conllu_invalid_head(treebank_type):
    file = io.StringIO('1\tI\t_\t_\t_\t_\t-1\troot\t0:root\t_\n\n')
    treebank_type = None
    with pytest.raises(evaluate_conllu.UDError):
        evaluate_conllu.load_conllu(file, treebank_type, eval_deprels=True)


def test_evaluate_identical_files(conllu_sentence, treebank_type):
    file1 = io.StringIO(conllu_sentence)
    file2 = io.StringIO(conllu_sentence)
    gold = evaluate_conllu.load_conllu(file1, treebank_type, eval_deprels=True)
    system = evaluate_conllu.load_conllu(file2, treebank_type, eval_deprels=True)
    scores = evaluate_conllu.evaluate(gold, system, eval_deprels=True)
    for _metric, score in scores.items():
        assert score.f1 == pytest.approx(1.0)


def test_evaluate_tokenization_mismatch(treebank_type):
    gold = io.StringIO('1\tHello\t_\t_\t_\t_\t0\troot\t0:root\t_\n\n')
    system = io.StringIO('1\tHelo\t_\t_\t_\t_\t0\troot\t0:root\t_\n\n')  # Different characters
    gold_ud = evaluate_conllu.load_conllu(gold, treebank_type, eval_deprels=True)
    system_ud = evaluate_conllu.load_conllu(system, treebank_type, eval_deprels=True)
    with pytest.raises(evaluate_conllu.UDError):
        evaluate_conllu.evaluate(gold_ud, system_ud, eval_deprels=True)


def test_evaluate_different_tokenization_same_chars(treebank_type):
    gold = io.StringIO('1\tHello\t_\t_\t_\t_\t0\troot\t0:root\t_\n\n')
    system = io.StringIO('1\tHel\t_\t_\t_\t_\t0\troot\t0:root\t_\n2\tlo\t_\t_\t_\t_\t1\tdep\t1:dep\t_\n\n')
    gold_ud = evaluate_conllu.load_conllu(gold, treebank_type, eval_deprels=True)
    system_ud = evaluate_conllu.load_conllu(system, treebank_type, eval_deprels=True)
    # This should not raise an error, just give low scores
    scores = evaluate_conllu.evaluate(gold_ud, system_ud, eval_deprels=True)
    assert scores['Tokens'].f1 < 1.0  # Different tokenization should give low token score


def test_evaluate_ud_files(tmp_path, conllu_sentence):
    # Write two identical files
    gold_path = tmp_path / 'gold.conllu'
    system_path = tmp_path / 'system.conllu'
    gold_path.write_text(conllu_sentence, encoding='utf-8')
    system_path.write_text(conllu_sentence, encoding='utf-8')
    scores = evaluate_conllu.evaluate_ud_files(str(gold_path), str(system_path), tb_type='0', eval_deprels=True)
    assert scores['Tokens'].f1 == pytest.approx(1.0)
    assert scores['Words'].f1 == pytest.approx(1.0)
    assert scores['UPOS'].f1 == pytest.approx(1.0)


def test_evaluate_ud_files_with_deprels_off(tmp_path, conllu_sentence):
    gold_path = tmp_path / 'gold.conllu'
    system_path = tmp_path / 'system.conllu'
    gold_path.write_text(conllu_sentence, encoding='utf-8')
    system_path.write_text(conllu_sentence, encoding='utf-8')
    scores = evaluate_conllu.evaluate_ud_files(str(gold_path), str(system_path), tb_type='0', eval_deprels=False)
    assert scores['Tokens'].f1 == pytest.approx(1.0)
    assert scores['UAS'].f1 is None or scores['UAS'].f1 == 0.0


def test_evaluate_partial_match(treebank_type):
    # Create data where exactly one word matches in UPOS
    gold = io.StringIO(
        """1\tA\tlemma_A\tNOUN\t_\t_\t0\troot\t0:root\t_\n2\tB\tlemma_B\tVERB\t_\t_\t1\tobj\t1:obj\t_\n\n""",
    )
    system = io.StringIO(
        """1\tA\tlemma_X\tNOUN\t_\t_\t0\troot\t0:root\t_\n2\tB\tlemma_B\tADJ\t_\t_\t1\tobj\t1:obj\t_\n\n""",
    )
    gold_ud = evaluate_conllu.load_conllu(gold, treebank_type, eval_deprels=True)
    system_ud = evaluate_conllu.load_conllu(system, treebank_type, eval_deprels=True)
    scores = evaluate_conllu.evaluate(gold_ud, system_ud, eval_deprels=True)
    # Word 1: NOUN matches NOUN (correct)
    # Word 2: VERB doesn't match ADJ (incorrect)
    # So F1 should be 0.5 (1 correct out of 2)
    assert scores['UPOS'].f1 == 0.5  # One correct UPOS out of two  # noqa: PLR2004
    assert scores['Lemmas'].f1 == 0.5  # One correct lemma out of two  # noqa: PLR2004
    assert scores['Tokens'].f1 == 1.0  # Same tokenization
