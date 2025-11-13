"""Tests for tree building and structure validation."""

import conllu

from nlp_utilities.conllu.validators.validator import ConlluValidator
from tests.helpers.assertion import assert_error_count


def test_valid_tree() -> None:
    """Test building a valid tree."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upos': 'PRON',
            'xpos': '_',
            'feats': None,
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': None,
        },
        {
            'id': 2,
            'form': 'came',
            'lemma': 'come',
            'upos': 'VERB',
            'xpos': '_',
            'feats': None,
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': None,
        },
        {
            'id': 3,
            'form': '.',
            'lemma': '.',
            'upos': 'PUNCT',
            'xpos': '_',
            'feats': None,
            'head': 2,
            'deprel': 'punct',
            'deps': '_',
            'misc': None,
        },
    ]
    sentence = conllu.models.TokenList(tokens, {'sent_id': 'test1', 'text': 'He came.'})  # type: ignore [arg-type]
    validator = ConlluValidator(level=2)
    validator.reporter.sentence_id = 'test1'
    validator.reporter.tree_counter = 1

    # Build tree
    tree = validator._build_and_validate_tree(sentence)

    assert tree is not None, 'Tree should be built successfully'
    assert tree.token['form'] == 'came', f"Root should be 'came', got {tree.token['form']}"
    assert len(tree.children) == 2, f'Root should have 2 children, got {len(tree.children)}'

    assert_error_count(validator.reporter, 0)


def test_self_loop() -> None:
    """Test detection of self-loop (HEAD == ID)."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upos': 'PRON',
            'xpos': '_',
            'feats': None,
            'head': 1,  # Self-loop!
            'deprel': 'nsubj',
            'deps': '_',
            'misc': None,
        },
        {
            'id': 2,
            'form': 'came',
            'lemma': 'come',
            'upos': 'VERB',
            'xpos': '_',
            'feats': None,
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': None,
        },
    ]
    sentence = conllu.models.TokenList(tokens, {'sent_id': 'test2', 'text': 'He came.'})  # type: ignore [arg-type]

    validator = ConlluValidator(level=2)
    validator.reporter.sentence_id = 'test2'
    validator.reporter.tree_counter = 1

    tree = validator._build_and_validate_tree(sentence)

    assert tree is None, 'Tree should not be built with self-loop'

    assert_error_count(validator.reporter, 1, 'head-self-loop')


def test_projection() -> None:
    """Test projection collection (descendant IDs)."""
    tokens = [
        {
            'id': 1,
            'form': 'He',
            'lemma': 'he',
            'upos': 'PRON',
            'xpos': '_',
            'feats': None,
            'head': 2,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': None,
        },
        {
            'id': 2,
            'form': 'came',
            'lemma': 'come',
            'upos': 'VERB',
            'xpos': '_',
            'feats': None,
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': None,
        },
        {
            'id': 3,
            'form': 'home',
            'lemma': 'home',
            'upos': 'ADV',
            'xpos': '_',
            'feats': None,
            'head': 2,
            'deprel': 'advmod',
            'deps': '_',
            'misc': None,
        },
    ]
    sentence = conllu.models.TokenList(tokens, {'sent_id': 'test3', 'text': 'He came home.'})  # type: ignore [arg-type]

    validator = ConlluValidator(level=2)
    tree = validator._build_and_validate_tree(sentence)

    assert tree is not None

    # Get projection of root
    projection = validator.get_projection(tree)

    # Should include root and all descendants
    assert 2 in projection, 'Projection should include root (2)'
    assert 1 in projection, 'Projection should include child 1'
    assert 3 in projection, 'Projection should include child 3'
    assert len(projection) == 3, f'Projection should have 3 nodes, got {len(projection)}'


def test_collect_ancestors() -> None:
    """Test ancestor collection."""
    tokens = [
        {
            'id': 1,
            'form': 'The',
            'lemma': 'the',
            'upos': 'DET',
            'xpos': '_',
            'feats': None,
            'head': 2,
            'deprel': 'det',
            'deps': '_',
            'misc': None,
        },
        {
            'id': 2,
            'form': 'dog',
            'lemma': 'dog',
            'upos': 'NOUN',
            'xpos': '_',
            'feats': None,
            'head': 3,
            'deprel': 'nsubj',
            'deps': '_',
            'misc': None,
        },
        {
            'id': 3,
            'form': 'barked',
            'lemma': 'bark',
            'upos': 'VERB',
            'xpos': '_',
            'feats': None,
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': None,
        },
    ]
    sentence = conllu.models.TokenList(tokens, {'sent_id': 'test4', 'text': 'The dog barked.'})  # type: ignore [arg-type]

    validator = ConlluValidator(level=2)

    # Collect ancestors of token 1 (The)
    ancestors = validator.collect_ancestors(1, sentence)

    # Should be: 1 -> 2 (dog) -> 3 (barked) -> 0 (root)
    assert ancestors == [2, 3, 0], f'Expected ancestors [2, 3, 0], got {ancestors}'

    # Collect ancestors of token 3 (barked)
    ancestors = validator.collect_ancestors(3, sentence)

    # Should be: 3 -> 0 (root)
    assert ancestors == [0], f'Expected ancestors [0], got {ancestors}'
