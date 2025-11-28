"""Shared fixtures for all tests."""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from copy import deepcopy
from pathlib import Path
from typing import Any

import conllu
import pytest

from conllu_tools.io import load_language_data
from conllu_tools.validation.error_reporter import ErrorReporter
from conllu_tools.validation.helpers import TreeHelperMixin
from conllu_tools.validation.validator import ConlluValidator
from tests.factories import build_conllu_sentence
from tests.test_data.load_data import EN_SENTENCE, LA_SENTENCE


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def feature_set() -> dict[str, Any]:
    """Load Latin feature set for testing."""
    return load_language_data('feats', 'la', load_dalme=True)


@pytest.fixture
def sentence_en_tokens() -> list[dict[str, str | int]]:
    """Provide default tokens for a valid English sentence."""
    return deepcopy(EN_SENTENCE['tokens'])


@pytest.fixture
def sentence_la_tokens() -> list[dict[str, str | int]]:
    """Provide default tokens for a valid Latin sentence."""
    return deepcopy(LA_SENTENCE['tokens'])


@pytest.fixture
def root_token() -> dict[str, Any]:
    """Provide a root token for building valid trees."""
    return {
        'id': 2,
        'form': 'root',
        'lemma': 'root',
        'upostag': 'VERB',
        'xpostag': '_',
        'feats': '_',
        'head': 0,
        'deprel': 'root',
        'deps': '_',
        'misc': '_',
    }


@pytest.fixture
def minimal_token() -> dict[str, str | int]:
    """Provide a minimal valid token with all required fields."""
    return {
        'id': 1,
        'form': 'word',
        'lemma': 'word',
        'upostag': 'NOUN',
        'xpostag': '_',
        'feats': '_',
        'head': 0,
        'deprel': 'root',
        'deps': '_',
        'misc': '_',
    }


@pytest.fixture
def token_with_features() -> dict[str, str | int]:
    """Provide a token with complex feature set."""
    return {
        'id': 1,
        'form': 'words',
        'lemma': 'word',
        'upostag': 'NOUN',
        'xpostag': '_',
        'feats': 'Case=Nom|Gender=Masc|Number=Plur',
        'head': 0,
        'deprel': 'root',
        'deps': '_',
        'misc': '_',
    }


@pytest.fixture
def token_with_enhanced_deps() -> dict[str, str | int]:
    """Provide a token with enhanced dependencies."""
    return {
        'id': 1,
        'form': 'word',
        'lemma': 'word',
        'upostag': 'NOUN',
        'xpostag': '_',
        'feats': '_',
        'head': 0,
        'deprel': 'root',
        'deps': '0:root',
        'misc': '_',
    }


@pytest.fixture
def multiword_token() -> dict[str, Any]:
    """Provide a sample multiword token."""
    return {
        'id': (1, 2),
        'form': 'cannot',
        'lemma': '_',
        'upostag': '_',
        'xpostag': '_',
        'feats': '_',
        'head': None,
        'deprel': '_',
        'deps': '_',
        'misc': '_',
    }


@pytest.fixture
def empty_node_token() -> dict[str, Any]:
    """Provide a sample empty node token."""
    return {
        'id': (1, '.', 1),
        'form': 'word',
        'lemma': 'word',
        'upostag': 'NOUN',
        'xpostag': '_',
        'feats': '_',
        'head': 2,
        'deprel': 'obj',
        'deps': '_',
        'misc': '_',
    }


@pytest.fixture
def punct_token() -> dict[str, str | int]:
    """Provide a punctuation token for punct validation tests."""
    return {
        'id': 2,
        'form': '.',
        'lemma': '.',
        'upostag': 'PUNCT',
        'xpostag': '_',
        'feats': '_',
        'head': 1,
        'deprel': 'punct',
        'deps': '_',
        'misc': '_',
    }


@pytest.fixture
def error_reporter() -> ErrorReporter:
    """Provide a fresh ErrorReporter instance for each test."""
    return ErrorReporter()


@pytest.fixture
def populated_error_reporter() -> ErrorReporter:
    """Provide an ErrorReporter with sample errors for testing formatting."""
    reporter = ErrorReporter()
    reporter.sentence_id = 'test-sent-1'
    reporter.sentence_mapid = {
        'test-sent-1': {'alt_id': 'test-sent-1', 'order': 1},
        'test-sent-2': {'alt_id': 'test-sent-2', 'order': 2},
    }

    # Add errors to different sentences
    reporter.warn('First error', 'test-error-1', testlevel=1, testid='test-1', line_no=1, node_id='1')
    reporter.warn('Second error', 'test-error-2', testlevel=2, testid='test-2', line_no=2, node_id='2')

    reporter.sentence_id = 'test-sent-2'
    reporter.warn('Third error', 'test-error-3', testlevel=1, testid='test-3', line_no=5, node_id='1')

    return reporter


@pytest.fixture
def sentence_concordance() -> dict[str, dict[str, Any]]:
    """Provide a sample sentence_id to (alt_id, order) mapping."""
    return {
        'test-sent-1': {'alt_id': 'test-sent-1', 'order': 1},
        'test-sent-2': {'alt_id': 'test-sent-2', 'order': 2},
        'test-sent-3': {'alt_id': 'test-sent-3', 'order': 3},
    }


# Create a concrete test class that uses the TreeHelper mixin
class TestTreeHelper(TreeHelperMixin):
    """Concrete class for testing TreeHelperMixin."""


@pytest.fixture
def tree_helper() -> TestTreeHelper:
    """Provide a TreeHelperMixin instance for testing."""
    return TestTreeHelper()


def _create_token(
    id: int,  # noqa: A002
    form: str,
    lemma: str,
    upostag: str,
    head: int,
    deprel: str,
    xpostag: str = '_',
    feats: str = '_',
    deps: str = '_',
    misc: str = '_',
) -> dict[str, Any]:
    """Create token dict with less verbosity."""
    return {
        'id': id,
        'form': form,
        'lemma': lemma,
        'upostag': upostag,
        'xpostag': xpostag,
        'feats': feats,
        'head': head,
        'deprel': deprel,
        'deps': deps,
        'misc': misc,
    }


@pytest.fixture
def single_node_tree() -> conllu.TokenTree:
    """Provide a basic single-node tree structure for testing tree helpers.

    Structure:
        0 (root)
        └── 1 (word1) - root
    """
    sentence_dict = {
        'sent_id': 'simple',
        'text': 'word1',
        'tokens': [
            _create_token(1, 'word1', 'word1', 'VERB', 0, 'root'),
        ],
    }
    conllu_text = build_conllu_sentence(sentence_dict)
    sentence = conllu.parse(conllu_text)[0]
    return sentence.to_tree()


@pytest.fixture
def simple_tree() -> conllu.TokenTree:
    """Provide a basic 3-4 node tree structure for testing tree helpers.

    Structure:
        0 (root)
        └── 1 (word1) - root
            └── 2 (word2) - obj
    """
    sentence_dict = {
        'sent_id': 'simple',
        'text': 'word1 word2',
        'tokens': [
            _create_token(1, 'word1', 'word1', 'VERB', 0, 'root'),
            _create_token(2, 'word2', 'word2', 'NOUN', 1, 'obj'),
            _create_token(3, 'word3', 'word3', 'ADJ', 2, 'amod'),
        ],
    }
    conllu_text = build_conllu_sentence(sentence_dict)
    sentence = conllu.parse(conllu_text)[0]
    return sentence.to_tree()


@pytest.fixture
def complex_tree() -> conllu.TokenTree:
    """Provide a tree with 10+ nodes for edge case testing.

    Structure: Deeper tree with multiple levels and siblings.
    """
    sentence_dict = {
        'sent_id': 'complex',
        'text': 'The quick brown fox jumps over the lazy dog today',
        'tokens': [
            _create_token(1, 'The', 'the', 'DET', 4, 'det'),
            _create_token(2, 'quick', 'quick', 'ADJ', 4, 'amod'),
            _create_token(3, 'brown', 'brown', 'ADJ', 4, 'amod'),
            _create_token(4, 'fox', 'fox', 'NOUN', 5, 'nsubj'),
            _create_token(5, 'jumps', 'jump', 'VERB', 0, 'root'),
            _create_token(6, 'over', 'over', 'ADP', 9, 'case'),
            _create_token(7, 'the', 'the', 'DET', 9, 'det'),
            _create_token(8, 'lazy', 'lazy', 'ADJ', 9, 'amod'),
            _create_token(9, 'dog', 'dog', 'NOUN', 5, 'obl'),
            _create_token(10, 'today', 'today', 'NOUN', 5, 'obl:tmod', misc='SpaceAfter=No'),
        ],
    }
    conllu_text = build_conllu_sentence(sentence_dict)
    sentence = conllu.parse(conllu_text)[0]
    return sentence.to_tree()


@pytest.fixture
def nonprojective_tree() -> conllu.TokenTree:
    """Provide a tree with known nonprojective dependencies.

    Example: A hearing on the issue is scheduled today
    where 'issue' depends on 'hearing' creating a nonprojective arc.
    """
    sentence_dict = {
        'sent_id': 'nonprojective',
        'text': 'A hearing on the issue is scheduled today',
        'tokens': [
            _create_token(1, 'A', 'a', 'DET', 2, 'det'),
            _create_token(2, 'hearing', 'hearing', 'NOUN', 7, 'nsubj:pass'),
            _create_token(3, 'on', 'on', 'ADP', 5, 'case'),
            _create_token(4, 'the', 'the', 'DET', 5, 'det'),
            _create_token(5, 'issue', 'issue', 'NOUN', 2, 'nmod'),
            _create_token(6, 'is', 'be', 'AUX', 7, 'aux:pass'),
            _create_token(7, 'scheduled', 'schedule', 'VERB', 0, 'root'),
            _create_token(8, 'today', 'today', 'NOUN', 7, 'obl:tmod', misc='SpaceAfter=No'),
        ],
    }
    conllu_text = build_conllu_sentence(sentence_dict)
    sentence = conllu.parse(conllu_text)[0]
    return sentence.to_tree()


@pytest.fixture
def disconnected_graph() -> list[dict[str, Any]]:
    """Provide a graph with multiple components for connectivity tests.

    Note: Returns tokens list, not tree, as disconnected graphs cannot form a proper tree.
    """
    return [
        {
            'id': 1,
            'form': 'word1',
            'lemma': 'word1',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'word2',
            'lemma': 'word2',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,  # Second root - disconnected
            'deprel': 'root',
            'deps': '0:root',
            'misc': '_',
        },
    ]


@pytest.fixture
def tree_with_empty_nodes() -> conllu.TokenTree:
    """Provide a tree containing empty nodes for empty node validation."""
    sentence_dict = {
        'sent_id': 'test',
        'text': 'word1 word2 word3',
        'tokens': [
            {
                'id': 1,
                'form': 'word1',
                'lemma': 'word1',
                'upostag': 'VERB',
                'xpostag': '_',
                'feats': '_',
                'head': 0,
                'deprel': 'root',
                'deps': '_',
                'misc': '_',
            },
            {
                'id': (1, '.', 1),
                'form': 'implied',
                'lemma': 'implied',
                'upostag': 'NOUN',
                'xpostag': '_',
                'feats': '_',
                'head': 1,
                'deprel': 'obj',
                'deps': '_',
                'misc': '_',
            },
            {
                'id': 2,
                'form': 'word2',
                'lemma': 'word2',
                'upostag': 'NOUN',
                'xpostag': '_',
                'feats': '_',
                'head': 1,
                'deprel': 'obl',
                'deps': '_',
                'misc': '_',
            },
        ],
    }
    conllu_text = build_conllu_sentence(sentence_dict)
    sentence = conllu.parse(conllu_text)[0]
    return sentence.to_tree()


@pytest.fixture
def tree_with_mwt() -> conllu.TokenTree:
    """Provide a tree containing multiword tokens for MWT testing."""
    sentence_dict = {
        'sent_id': 'test',
        'text': 'cannot go',
        'tokens': [
            {
                'id': (1, 2),
                'form': 'cannot',
                'lemma': '_',
                'upostag': '_',
                'xpostag': '_',
                'feats': '_',
                'head': None,
                'deprel': '_',
                'deps': '_',
                'misc': '_',
            },
            {
                'id': 1,
                'form': 'can',
                'lemma': 'can',
                'upostag': 'AUX',
                'xpostag': '_',
                'feats': '_',
                'head': 3,
                'deprel': 'aux',
                'deps': '_',
                'misc': '_',
            },
            {
                'id': 2,
                'form': 'not',
                'lemma': 'not',
                'upostag': 'PART',
                'xpostag': '_',
                'feats': '_',
                'head': 3,
                'deprel': 'advmod',
                'deps': '_',
                'misc': '_',
            },
            {
                'id': 3,
                'form': 'go',
                'lemma': 'go',
                'upostag': 'VERB',
                'xpostag': '_',
                'feats': '_',
                'head': 0,
                'deprel': 'root',
                'deps': '_',
                'misc': '_',
            },
        ],
    }
    conllu_text = build_conllu_sentence(sentence_dict)
    sentence = conllu.parse(conllu_text)[0]
    return sentence.to_tree()


@pytest.fixture
def validator_level_1() -> ConlluValidator:
    """Provide a pre-configured validator for level 1."""
    return ConlluValidator(level=1)


@pytest.fixture
def validator_level_2() -> ConlluValidator:
    """Provide a pre-configured validator for level 2."""
    return ConlluValidator(level=2)


@pytest.fixture
def validator_level_3() -> ConlluValidator:
    """Provide a pre-configured validator for level 3."""
    return ConlluValidator(level=3)


@pytest.fixture
def validator_level_4() -> ConlluValidator:
    """Provide a pre-configured validator for level 4."""
    return ConlluValidator(level=4)


@pytest.fixture
def validator_level_5() -> ConlluValidator:
    """Provide a pre-configured validator for level 5."""
    return ConlluValidator(level=5)


@pytest.fixture
def validator_with_lang() -> ConlluValidator:
    """Provide a validator configured for specific language testing (Latin)."""
    return ConlluValidator(level=4, lang='la')
