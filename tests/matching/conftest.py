"""Shared fixtures for matching module tests."""

from __future__ import annotations

from typing import Any

import conllu
import pytest

from conllu_tools.matching import Condition, TokenPattern
from tests.test_data.load_data import SAMPLE_CONLLU


@pytest.fixture
def sample_token() -> dict[str, Any]:
    """Provide a sample token dictionary for testing."""
    return {
        'id': 1,
        'form': 'unum',
        'lemma': 'unus',
        'upos': 'NUM',
        'xpos': 'm-s---nn-',
        'feats': {'Case': 'Nom', 'Gender': 'Neut', 'Number': 'Sing'},
        'head': 2,
        'deprel': 'nummod',
        'deps': [(2, 'nummod')],
        'misc': {'start_char': '0', 'end_char': '4'},
    }


@pytest.fixture
def noun_token() -> dict[str, Any]:
    """Provide a sample noun token for testing."""
    return {
        'id': 2,
        'form': 'scala',
        'lemma': 'scalae',
        'upos': 'NOUN',
        'xpos': 'n-s---fn-',
        'feats': {'Case': 'Nom', 'Gender': 'Fem', 'Number': 'Sing'},
        'head': 0,
        'deprel': 'root',
        'deps': [(0, 'root')],
        'misc': {'start_char': '4', 'end_char': '9'},
    }


@pytest.fixture
def verb_token() -> dict[str, Any]:
    """Provide a sample verb token for testing."""
    return {
        'id': 3,
        'form': 'habebat',
        'lemma': 'habeo',
        'upos': 'VERB',
        'xpos': 'v3siia---',
        'feats': {
            'Aspect': 'Imp',
            'Mood': 'Ind',
            'Number': 'Sing',
            'Person': '3',
            'Tense': 'Past',
            'VerbForm': 'Fin',
            'Voice': 'Act',
        },
        'head': 0,
        'deprel': 'root',
        'deps': [(0, 'root')],
        'misc': None,
    }


@pytest.fixture
def adj_token() -> dict[str, Any]:
    """Provide a sample adjective token for testing."""
    return {
        'id': 4,
        'form': 'magnam',
        'lemma': 'magnus',
        'upos': 'ADJ',
        'xpos': 'a-s---fap',
        'feats': {'Case': 'Acc', 'Degree': 'Pos', 'Gender': 'Fem', 'Number': 'Sing'},
        'head': 3,
        'deprel': 'amod',
        'deps': [(3, 'amod')],
        'misc': None,
    }


@pytest.fixture
def adp_token() -> dict[str, Any]:
    """Provide a sample adposition token for testing."""
    return {
        'id': 5,
        'form': 'de',
        'lemma': 'de',
        'upos': 'ADP',
        'xpos': 'r--------',
        'feats': {'AdpType': 'Prep'},
        'head': 6,
        'deprel': 'case',
        'deps': [(6, 'case')],
        'misc': None,
    }


@pytest.fixture
def punct_token() -> dict[str, Any]:
    """Provide a sample punctuation token for testing."""
    return {
        'id': 10,
        'form': '.',
        'lemma': '.',
        'upos': 'PUNCT',
        'xpos': 'u--------',
        'feats': None,
        'head': 3,
        'deprel': 'punct',
        'deps': [(3, 'punct')],
        'misc': None,
    }


@pytest.fixture
def simple_condition() -> Condition:
    """Provide a simple equals condition."""
    return Condition(key='upos', values=['NOUN'])


@pytest.fixture
def multi_value_condition() -> Condition:
    """Provide a condition with multiple values."""
    return Condition(key='upos', values=['NOUN', 'VERB', 'ADJ'])


@pytest.fixture
def nested_condition() -> Condition:
    """Provide a nested condition for feats testing."""
    inner_conditions: list[str | Condition] = [
        Condition(key='Number', values=['Sing']),
        Condition(key='Case', values=['Abl', 'Dat']),
    ]
    return Condition(key='feats', values=inner_conditions)


@pytest.fixture
def simple_token_pattern() -> TokenPattern:
    """Provide a simple token pattern matching nouns."""
    condition = Condition(key='upos', values=['NOUN'])
    return TokenPattern(conditions=[condition])


@pytest.fixture
def complex_token_pattern() -> TokenPattern:
    """Provide a complex token pattern with multiple conditions."""
    upos_cond = Condition(key='upos', values=['NOUN'])
    feats_conds: list[str | Condition] = [
        Condition(key='Number', values=['Sing']),
        Condition(key='Case', values=['Abl']),
    ]
    feats_cond = Condition(key='feats', values=feats_conds)
    return TokenPattern(conditions=[upos_cond, feats_cond])


@pytest.fixture
def sample_sentence() -> conllu.TokenList:
    """Provide a sample sentence TokenList for matching tests."""
    conllu_data = conllu.parse(SAMPLE_CONLLU)
    return next(s for s in conllu_data if s.metadata.get('sent_id') == 'test-1')


@pytest.fixture
def complex_sentence() -> conllu.TokenList:
    """Provide a complex sentence TokenList for matching tests."""
    conllu_data = conllu.parse(SAMPLE_CONLLU)
    return next(s for s in conllu_data if s.metadata.get('sent_id') == 'test-2')


@pytest.fixture
def sentence_with_verb() -> conllu.TokenList:
    """Provide a sentence with a verb for pattern matching tests."""
    conllu_data = conllu.parse(SAMPLE_CONLLU)
    return next(s for s in conllu_data if s.metadata.get('sent_id') == 'test-3')


@pytest.fixture
def multi_sentence_corpus() -> list[conllu.TokenList]:
    """Provide a multi-sentence corpus for find_in_corpus tests."""
    conllu_data = conllu.parse(SAMPLE_CONLLU)
    return [s for s in conllu_data if s.metadata.get('sent_id', '').startswith('corpus-')]


@pytest.fixture
def sample_corpus() -> list[conllu.TokenList]:
    """Provide a sample corpus for testing."""
    conllu_data = conllu.parse(SAMPLE_CONLLU)
    return [s for s in conllu_data if s.metadata.get('sent_id', '').startswith('sent-')]
