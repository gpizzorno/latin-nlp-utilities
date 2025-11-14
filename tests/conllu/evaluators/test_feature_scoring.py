"""Features Scoring Tests."""

from __future__ import annotations

import conllu

from nlp_utilities.conllu.evaluators import ConlluEvaluator


def test_feats_match_with_identical_features() -> None:
    """Test _feats_match with identical features."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = puella
1\tpuella\tpuella\tNOUN\t_\tCase=Nom|Gender=Fem|Number=Sing\t0\troot\t_\t_

"""
    system_text = gold_text

    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    assert scores['UFeats'].f1 == 1.0


def test_feats_match_with_different_features() -> None:
    """Test _feats_match with different features."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = puella
1\tpuella\tpuella\tNOUN\t_\tCase=Nom|Gender=Fem|Number=Sing\t0\troot\t_\t_

"""
    system_text = """# sent_id = 1
# text = puella
1\tpuella\tpuella\tNOUN\t_\tCase=Acc|Gender=Fem|Number=Sing\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    assert scores['UFeats'].correct == 0


def test_feats_match_with_universal_feature_filtering() -> None:
    """Test _feats_match filters to universal features only."""
    evaluator = ConlluEvaluator()

    # Include language-specific feature (Foreign)
    gold_text = """# sent_id = 1
# text = puella
1\tpuella\tpuella\tNOUN\t_\tCase=Nom|Gender=Fem|NameType=Per\t0\troot\t_\t_

"""
    # System has same universal features but different language-specific
    system_text = """# sent_id = 1
# text = puella
1\tpuella\tpuella\tNOUN\t_\tCase=Nom|Gender=Fem|NameType=Geo\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # Should match because only universal features are compared
    assert scores['UFeats'].correct == 1


def test_feats_match_with_language_specific_ignored() -> None:
    """Test _feats_match ignores language-specific features."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = puella
1\tpuella\tpuella\tNOUN\t_\tCase=Nom|Gender=Fem|Number=Sing\t0\troot\t_\t_

"""
    # System has additional language-specific feature
    system_text = """# sent_id = 1
# text = puella
1\tpuella\tpuella\tNOUN\t_\tCase=Nom|Gender=Fem|Number=Sing|NameType=Per\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # Should still match (language-specific features ignored)
    assert scores['UFeats'].correct == 1


def test_feats_match_with_none_empty_features() -> None:
    """Test _feats_match with None/empty features."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\t_\t_\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\t_\t_\t0\troot\t_\t_

"""
    system_text = gold_text

    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # Empty features should match
    assert scores['UFeats'].correct == 2
