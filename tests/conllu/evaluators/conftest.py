"""Configure pytest fixtures for evaluator tests."""

from __future__ import annotations

from pathlib import Path

import conllu
import pytest

from nlp_utilities.conllu.evaluators.base import (
    Alignment,
    AlignmentWord,
    Score,
    UDSpan,
    UDWord,
)
from nlp_utilities.conllu.evaluators.evaluator import ConlluEvaluator


@pytest.fixture
def simple_udspan() -> UDSpan:
    """Provide a simple UDSpan for testing."""
    return UDSpan(start=0, end=5)


@pytest.fixture
def empty_udspan() -> UDSpan:
    """Provide an empty UDSpan (start=end) for testing."""
    return UDSpan(start=5, end=5)


@pytest.fixture
def simple_token() -> conllu.Token:
    """Provide a simple conllu.Token for testing."""
    return conllu.Token(
        [
            ('id', 1),
            ('form', 'word'),
            ('lemma', 'word'),
            ('upos', 'NOUN'),
            ('xpos', '_'),
            ('feats', None),
            ('head', 0),
            ('deprel', 'root'),
            ('deps', None),
            ('misc', None),
        ],
    )


@pytest.fixture
def token_with_features() -> conllu.Token:
    """Provide a token with morphological features."""
    return conllu.Token(
        [
            ('id', 1),
            ('form', 'word'),
            ('lemma', 'word'),
            ('upos', 'NOUN'),
            ('xpos', 'N'),
            ('feats', {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}),
            ('head', 0),
            ('deprel', 'root'),
            ('deps', None),
            ('misc', None),
        ],
    )


@pytest.fixture
def simple_udword(simple_token: conllu.Token, simple_udspan: UDSpan) -> UDWord:
    """Provide a simple UDWord for testing."""
    return UDWord(
        span=simple_udspan,
        token=simple_token,
        is_multiword=False,
    )


@pytest.fixture
def multiword_udword(simple_token: conllu.Token) -> UDWord:
    """Provide a UDWord marked as multiword."""
    span = UDSpan(start=0, end=10)
    return UDWord(
        span=span,
        token=simple_token,
        is_multiword=True,
    )


@pytest.fixture
def udword_with_enhanced_deps(simple_token: conllu.Token, simple_udspan: UDSpan) -> UDWord:
    """Provide a UDWord with enhanced dependencies."""
    word = UDWord(
        span=simple_udspan,
        token=simple_token,
        is_multiword=False,
    )
    # Enhanced deps: list of (parent_id_or_word, dependency_path)
    word.enhanced_deps = [(0, ['root'])]
    return word


@pytest.fixture
def udword_with_functional_children(
    simple_token: conllu.Token,
    simple_udspan: UDSpan,
) -> UDWord:
    """Provide a UDWord with functional children."""
    word = UDWord(
        span=simple_udspan,
        token=simple_token,
        is_multiword=False,
    )
    # Create a functional child
    child_token = conllu.Token(
        [
            ('id', 2),
            ('form', 'the'),
            ('lemma', 'the'),
            ('upos', 'DET'),
            ('xpos', '_'),
            ('feats', None),
            ('head', 1),
            ('deprel', 'det'),
            ('deps', None),
            ('misc', None),
        ],
    )
    child_word = UDWord(
        span=UDSpan(start=5, end=8),
        token=child_token,
        is_multiword=False,
    )
    word.functional_children = [child_word]
    return word


@pytest.fixture
def alignment_word_pair(simple_udword: UDWord) -> AlignmentWord:
    """Provide an AlignmentWord pair for testing."""
    # Create a second word to pair with
    token2 = conllu.Token(
        [
            ('id', 1),
            ('form', 'word'),
            ('lemma', 'word'),
            ('upos', 'NOUN'),
            ('xpos', '_'),
            ('feats', None),
            ('head', 0),
            ('deprel', 'root'),
            ('deps', None),
            ('misc', None),
        ],
    )
    system_word = UDWord(
        span=UDSpan(start=0, end=5),
        token=token2,
        is_multiword=False,
    )
    return AlignmentWord(gold_word=simple_udword, system_word=system_word)


@pytest.fixture
def empty_alignment() -> Alignment:
    """Provide an empty Alignment for testing."""
    return Alignment(gold_words=[], system_words=[])


@pytest.fixture
def simple_alignment(simple_udword: UDWord) -> Alignment:
    """Provide a simple Alignment with one aligned word pair."""
    token2 = conllu.Token(
        [
            ('id', 1),
            ('form', 'word'),
            ('lemma', 'word'),
            ('upos', 'NOUN'),
            ('xpos', '_'),
            ('feats', None),
            ('head', 0),
            ('deprel', 'root'),
            ('deps', None),
            ('misc', None),
        ],
    )
    system_word = UDWord(
        span=UDSpan(start=0, end=5),
        token=token2,
        is_multiword=False,
    )
    alignment = Alignment(gold_words=[simple_udword], system_words=[system_word])
    alignment.append_aligned_words(simple_udword, system_word)
    return alignment


@pytest.fixture
def simple_score() -> Score:
    """Provide a simple Score for testing."""
    return Score(gold_total=10, system_total=10, correct=8)


@pytest.fixture
def perfect_score() -> Score:
    """Provide a perfect Score for testing."""
    return Score(gold_total=10, system_total=10, correct=10)


@pytest.fixture
def zero_score() -> Score:
    """Provide a zero Score for testing."""
    return Score(gold_total=10, system_total=10, correct=0)


@pytest.fixture
def score_with_aligned_total() -> Score:
    """Provide a Score with aligned_total for testing."""
    return Score(gold_total=10, system_total=12, correct=8, aligned_total=9)


@pytest.fixture
def evaluator() -> ConlluEvaluator:
    """Provide a default ConlluEvaluator instance."""
    return ConlluEvaluator()


@pytest.fixture
def evaluator_no_deprels() -> ConlluEvaluator:
    """Provide a ConlluEvaluator with eval_deprels=False."""
    return ConlluEvaluator(eval_deprels=False)


@pytest.fixture
def evaluator_with_treebank_type() -> ConlluEvaluator:
    """Provide a ConlluEvaluator with treebank_type filters."""
    return ConlluEvaluator(treebank_type='12')


@pytest.fixture
def test_gold_path() -> Path:
    """Provide path to test gold.conllu file."""
    return Path('tests/test_data/gold.conllu')


@pytest.fixture
def test_system_path() -> Path:
    """Provide path to test system.conllu file."""
    return Path('tests/test_data/system.conllu')


@pytest.fixture
def simple_conllu_sentence() -> conllu.TokenList:
    """Provide a simple conllu.TokenList for testing."""
    text = """# sent_id = 1
# text = word
1\tword\tword\tNOUN\t_\t_\t0\troot\t_\t_

"""
    return conllu.parse(text)[0]


@pytest.fixture
def conllu_sentence_with_mwt() -> conllu.TokenList:
    """Provide a conllu.TokenList with multi-word token."""
    text = """# sent_id = 1
# text = cannot
1-2\tcannot\t_\t_\t_\t_\t_\t_\t_\t_
1\tcan\tcan\tAUX\t_\t_\t3\taux\t_\t_
2\tnot\tnot\tPART\t_\t_\t3\tadvmod\t_\t_
3\tgo\tgo\tVERB\t_\t_\t0\troot\t_\t_

"""
    return conllu.parse(text)[0]


@pytest.fixture
def conllu_sentence_with_enhanced_deps() -> conllu.TokenList:
    """Provide a conllu.TokenList with enhanced dependencies."""
    text = """# sent_id = 1
# text = word1 word2
1\tword1\tword1\tVERB\t_\t_\t0\troot\t0:root\t_
2\tword2\tword2\tNOUN\t_\t_\t1\tobj\t1:obj\t_

"""
    return conllu.parse(text)[0]
