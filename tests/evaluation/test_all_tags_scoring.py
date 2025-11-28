"""AllTags Scoring Tests."""

from __future__ import annotations

import conllu
from conllu_tools.evaluation import ConlluEvaluator


def test_alltags_matching() -> None:
    """Test AllTags (UPOS + XPOS + Universal FEATS) matching."""
    evaluator = ConlluEvaluator()

    text = """# sent_id = 1
# text = puella
1\tpuella\tpuella\tNOUN\tNN\tCase=Nom|Gender=Fem|Number=Sing\t0\troot\t_\t_

"""
    sentences = conllu.parse(text)
    scores = evaluator._evaluate_sentences(sentences, sentences)

    assert scores['AllTags'].f1 == 1.0


def test_alltags_all_components_correct() -> None:
    """Test AllTags with all components correct."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\tDT\tDefinite=Def\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\tNN\tNumber=Sing\t0\troot\t_\t_

"""
    system_text = gold_text

    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    assert scores['AllTags'].correct == 2


def test_alltags_some_components_incorrect() -> None:
    """Test AllTags with some components incorrect."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\tDT\tDefinite=Def\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\tNN\tNumber=Sing\t0\troot\t_\t_

"""
    # System has wrong XPOS for second word
    system_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\tDT\tDefinite=Def\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\tVB\tNumber=Sing\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # Only 1 of 2 correct (second word has wrong XPOS)
    assert scores['AllTags'].correct == 1


def test_alltags_universal_feature_filtering() -> None:
    """Test AllTags uses universal feature filtering."""
    evaluator = ConlluEvaluator()

    gold_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\tDT\tDefinite=Def\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\tNN\tNumber=Sing|NameType=Per\t0\troot\t_\t_

"""
    # System has different language-specific feature
    system_text = """# sent_id = 1
# text = The cat
1\tThe\tthe\tDET\tDT\tDefinite=Def\t2\tdet\t_\t_
2\tcat\tcat\tNOUN\tNN\tNumber=Sing|NameType=Geo\t0\troot\t_\t_

"""
    gold_sentences = conllu.parse(gold_text)
    system_sentences = conllu.parse(system_text)

    scores = evaluator._evaluate_sentences(gold_sentences, system_sentences)

    # Should match (language-specific features ignored)
    assert scores['AllTags'].correct == 2


# Tests will continue in next part...
