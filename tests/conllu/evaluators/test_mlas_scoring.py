"""Tests for MLAS scoring."""

from __future__ import annotations

import conllu

from nlp_utilities.conllu.evaluators import UDEvaluator


def test_mlas_calculation() -> None:
    """Test MLAS (morphology-aware LAS) calculation."""
    evaluator = UDEvaluator()

    text = """# sent_id = 1
# text = puella cantat
1\tpuella\tpuella\tNOUN\t_\tCase=Nom|Gender=Fem|Number=Sing\t2\tnsubj\t_\t_
2\tcantat\tcanto\tVERB\t_\tMood=Ind|Number=Sing|Person=3|Tense=Pres\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    # Both are content words with correct morphology
    assert scores['MLAS'].gold_total == 2
    assert scores['MLAS'].correct == 2


def test_mlas_requires_head_deprel_upos_feats_match() -> None:
    """Test MLAS requires HEAD + DEPREL + UPOS + FEATS to match."""
    evaluator = UDEvaluator()

    gold_text = """# sent_id = 1
# text = puella cantat
1\tpuella\tpuella\tNOUN\t_\tCase=Nom|Gender=Fem|Number=Sing\t2\tnsubj\t_\t_
2\tcantat\tcanto\tVERB\t_\tMood=Ind|Number=Sing|Person=3\t0\troot\t_\t_

"""
    # System has wrong features for first word
    system_text = """# sent_id = 1
# text = puella cantat
1\tpuella\tpuella\tNOUN\t_\tCase=Acc|Gender=Fem|Number=Sing\t2\tnsubj\t_\t_
2\tcantat\tcanto\tVERB\t_\tMood=Ind|Number=Sing|Person=3\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # Only 1 of 2 correct (first word has wrong Case)
    assert scores['MLAS'].correct == 1


def test_mlas_requires_functional_children_match() -> None:
    """Test MLAS requires functional children to match."""
    evaluator = UDEvaluator()

    gold_text = """# sent_id = 1
# text = The cat runs
1\tThe\tthe\tDET\t_\tDefinite=Def\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\tNumber=Sing\t3\tnsubj\t_\t_
3\truns\trun\tVERB\t_\tNumber=Sing\t0\troot\t_\t_

"""
    # System has different functional child properties
    system_text = """# sent_id = 1
# text = The cat runs
1\tThe\tthe\tDET\t_\tDefinite=Ind\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\tNumber=Sing\t3\tnsubj\t_\t_
3\truns\trun\tVERB\t_\tNumber=Sing\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # Word 2 (cat) should not match in MLAS because its functional child (The) has different features
    # Word 3 (runs) has no functional children, so should match
    assert scores['MLAS'].correct == 1


def test_mlas_with_correct_functional_children() -> None:
    """Test MLAS with correct functional children."""
    evaluator = UDEvaluator()

    text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\tDefinite=Def\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\tNumber=Sing\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    # root should match with its functional child
    assert scores['MLAS'].correct == 1


def test_mlas_with_incorrect_functional_children() -> None:
    """Test MLAS with incorrect functional children."""
    evaluator = UDEvaluator()

    gold_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\tDefinite=Def\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\tNumber=Sing\t0\troot\t_\t_

"""
    # System has functional child with wrong UPOS
    system_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tPRON\t_\tDefinite=Def\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\tNumber=Sing\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # root should not match because functional child UPOS is wrong
    assert scores['MLAS'].correct == 0


def test_mlas_functional_children_mapping_through_alignment() -> None:
    """Test MLAS functional children are mapped through word alignment."""
    evaluator = UDEvaluator()

    # This is tested implicitly in the above tests - the functional children
    # from gold are mapped to their aligned system word IDs for comparison
    text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\tDefinite=Def\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\tNumber=Sing\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    # Should work correctly with alignment
    assert scores['MLAS'].f1 == 1.0


def test_mlas_with_empty_functional_children() -> None:
    """Test MLAS with empty functional children."""
    evaluator = UDEvaluator()

    # Content words with no functional children
    text = """# sent_id = 1
# text = cat runs
1\tcat\tcat\tNOUN\t_\tNumber=Sing\t2\tnsubj\t_\t_
2\truns\trun\tVERB\t_\tNumber=Sing\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    # Should match with empty functional children
    assert scores['MLAS'].correct == 2
