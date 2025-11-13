"""Tests for Enhanced Dependency scoring."""

from __future__ import annotations

import conllu

from nlp_utilities.conllu.evaluators import UDEvaluator


def test_enhanced_alignment_score_basic() -> None:
    """Test _enhanced_alignment_score basic functionality."""
    evaluator = UDEvaluator()

    text = """# sent_id = 1
# text = cat runs
1\tcat\tcat\tNOUN\t_\t_\t2\tnsubj\t2:nsubj\t_
2\truns\trun\tVERB\t_\t_\t0\troot\t0:root\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    # Both enhanced deps should match
    assert scores['ELAS'].correct == 2


def test_elas_enhanced_labeled_attachment_score() -> None:
    """Test ELAS (enhanced labeled attachment score)."""
    evaluator = UDEvaluator()

    gold_text = """# sent_id = 1
# text = cat runs
1\tcat\tcat\tNOUN\t_\t_\t2\tnsubj\t2:nsubj\t_
2\truns\trun\tVERB\t_\t_\t0\troot\t0:root\t_

"""
    # System has one wrong enhanced dep
    system_text = """# sent_id = 1
# text = cat runs
1\tcat\tcat\tNOUN\t_\t_\t2\tnsubj\t2:obj\t_
2\truns\trun\tVERB\t_\t_\t0\troot\t0:root\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # Only 1 of 2 should match
    assert scores['ELAS'].correct == 1


def test_eulas_enhanced_unlabeled_attachment_score() -> None:
    """Test EULAS (enhanced unlabeled attachment score) - ignores subtypes."""
    evaluator = UDEvaluator()

    gold_text = """# sent_id = 1
# text = house
1\thouse\thouse\tNOUN\t_\t_\t0\tnmod:tmod\t0:nmod:tmod\t_

"""
    # System has base label (no subtype)
    system_text = """# sent_id = 1
# text = house
1\thouse\thouse\tNOUN\t_\t_\t0\tnmod:tmod\t0:nmod\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # ELAS should not match (different subtypes)
    assert scores['ELAS'].correct == 0

    # EULAS should match (subtypes ignored)
    assert scores['EULAS'].correct == 1


def test_enhanced_deps_parent_matching() -> None:
    """Test enhanced deps parent matching through alignment."""
    evaluator = UDEvaluator()

    text = """# sent_id = 1
# text = cat runs
1\tcat\tcat\tNOUN\t_\t_\t2\tnsubj\t2:nsubj\t_
2\truns\trun\tVERB\t_\t_\t0\troot\t0:root\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    # Parents should match through alignment
    assert scores['ELAS'].f1 == 1.0


def test_enhanced_deps_path_matching() -> None:
    """Test enhanced deps path matching."""
    evaluator = UDEvaluator()

    gold_text = """# sent_id = 1
# text = book
1\tbook\tbook\tNOUN\t_\t_\t0\troot\t0:nmod>case\t_

"""
    # System has different path
    system_text = """# sent_id = 1
# text = book
1\tbook\tbook\tNOUN\t_\t_\t0\troot\t0:obl>case\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # Path doesn't match
    assert scores['ELAS'].correct == 0


def test_enhanced_deps_with_root() -> None:
    """Test enhanced deps with root (parent=0)."""
    evaluator = UDEvaluator()

    text = """# sent_id = 1
# text = runs
1\truns\trun\tVERB\t_\t_\t0\troot\t0:root\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    # Root should match
    assert scores['ELAS'].correct == 1


def test_enhanced_deps_alignment_mapping() -> None:
    """Test enhanced deps use alignment mapping for parents."""
    evaluator = UDEvaluator()

    # This is tested implicitly - system parents are mapped through matched_words_map
    text = """# sent_id = 1
# text = The cat runs
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t3\tnsubj\t3:nsubj\t_
3\truns\trun\tVERB\t_\t_\t0\troot\t0:root\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    # All enhanced deps should match through alignment
    assert scores['ELAS'].correct == 2


def test_enhanced_deps_counting_across_sentences() -> None:
    """Test enhanced deps are counted across all sentences."""
    evaluator = UDEvaluator()

    text = """# sent_id = 1
# text = cat runs
1\tcat\tcat\tNOUN\t_\t_\t2\tnsubj\t2:nsubj\t_
2\truns\trun\tVERB\t_\t_\t0\troot\t0:root\t_

# sent_id = 2
# text = dog walks
1\tdog\tdog\tNOUN\t_\t_\t2\tnsubj\t2:nsubj\t_
2\twalks\twalk\tVERB\t_\t_\t0\troot\t0:root\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    # Should count all 4 enhanced deps across both sentences
    assert scores['ELAS'].gold_total == 4
    assert scores['ELAS'].correct == 4
