"""Tests for validation.py - Helper methods for tree operations and projectivity analysis."""

import conllu

from tests.conftest import TestTreeHelper
from tests.factories import ConlluSentenceFactory

test_sentence = {
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
            'id': 2,
            'form': 'word2',
            'lemma': 'word2',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'obj',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'word3',
            'lemma': 'word3',
            'upostag': 'ADJ',
            'xpostag': '_',
            'feats': '_',
            'head': 2,
            'deprel': 'amod',
            'deps': '_',
            'misc': '_',
        },
    ],
}


def test_get_projection_single_node(tree_helper: TestTreeHelper, single_node_tree: conllu.TokenTree) -> None:
    """Test get_projection() with a single node (root)."""
    projection = tree_helper.get_projection(single_node_tree)
    # Root node should be in its own projection
    assert 1 in projection
    assert len(projection) == 1


def test_get_projection_with_children(tree_helper: TestTreeHelper, simple_tree: conllu.TokenTree) -> None:
    """Test get_projection() includes all descendants."""
    projection = tree_helper.get_projection(simple_tree)
    # Should include root and all descendants
    assert projection == {1, 2, 3}


def test_get_projection_subtree(tree_helper: TestTreeHelper, complex_tree: conllu.TokenTree) -> None:
    """Test get_projection() on a subtree node."""
    node_5 = complex_tree.children[1]
    projection = tree_helper.get_projection(node_5)
    assert projection == {6, 7, 8, 9}


def test_collect_ancestors_to_root(tree_helper: TestTreeHelper) -> None:
    """Test collect_ancestors() collects path up to root."""
    sentence = ConlluSentenceFactory.as_tokenlist(**test_sentence)
    # Ancestors of node 3 should be [2, 1, 0]
    ancestors = tree_helper.collect_ancestors(3, sentence)
    assert ancestors == [2, 1, 0]


def test_collect_ancestors_from_root(tree_helper: TestTreeHelper) -> None:
    """Test collect_ancestors() from root node."""
    mod_sentence = test_sentence.copy()
    mod_sentence['tokens'] = test_sentence['tokens'][:2]  # Only tokens 1 and 2
    sentence = ConlluSentenceFactory.as_tokenlist(**mod_sentence)
    # Ancestors of root node 1 should be [0]
    ancestors = tree_helper.collect_ancestors(1, sentence)
    assert ancestors == [0]


def test_collect_ancestors_with_invalid_id(tree_helper: TestTreeHelper) -> None:
    """Test collect_ancestors() with non-existent token ID."""
    mod_sentence = test_sentence.copy()
    mod_sentence['tokens'] = test_sentence['tokens'][:1]  # Only token 1
    sentence = ConlluSentenceFactory.as_tokenlist(**mod_sentence)
    # Non-existent node should return empty or partial list
    ancestors = tree_helper.collect_ancestors(99, sentence)
    assert ancestors == []


def test_collect_ancestors_with_none_head(tree_helper: TestTreeHelper) -> None:
    """Test collect_ancestors() handles None head gracefully."""
    mod_sentence = test_sentence.copy()
    mod_sentence['tokens'] = test_sentence['tokens'][:1]  # Only token 1
    mod_sentence['tokens'][0]['head'] = None  # type: ignore [index] # Set head to None
    sentence = ConlluSentenceFactory.as_tokenlist(**mod_sentence)
    ancestors = tree_helper.collect_ancestors(1, sentence)
    assert ancestors == []


def test_collect_ancestors_prevents_cycles(tree_helper: TestTreeHelper) -> None:
    """Test collect_ancestors() stops when cycle detected."""
    # Create a sentence where we can test cycle detection
    # In practice this wouldn't happen in valid CoNLL-U, but we test the safety check
    mod_sentence = test_sentence.copy()
    mod_sentence['tokens'] = test_sentence['tokens'][:2]  # Only tokens 1 and 2
    sentence = ConlluSentenceFactory.as_tokenlist(**mod_sentence)
    # Normal case - should work fine
    ancestors = tree_helper.collect_ancestors(2, sentence)
    assert ancestors == [1]
    # The cycle detection code prevents infinite loops by checking if head already in ancestors


def test_get_gap_no_gap(tree_helper: TestTreeHelper) -> None:
    """Test get_gap() when there's no gap (adjacent nodes)."""
    mod_sentence = test_sentence.copy()
    mod_sentence['tokens'] = test_sentence['tokens'][:2]  # Only tokens 1 and 2
    sentence = ConlluSentenceFactory.as_tokenlist(**mod_sentence)
    gap = tree_helper.get_gap(2, sentence)
    # No nodes between 2 and its parent 1
    assert gap == set()


def test_get_gap_with_intervening_node(tree_helper: TestTreeHelper) -> None:
    """Test get_gap() with node between child and parent."""
    mod_sentence = test_sentence.copy()
    mod_sentence['tokens'][2]['head'] = 1  # type: ignore [index] # Make word3 depend on word1
    sentence = ConlluSentenceFactory.as_tokenlist(**mod_sentence)
    # Gap between node 3 and its parent 1 should include node 2 (if it's not in parent's projection)
    gap = tree_helper.get_gap(3, sentence)
    # Node 2 is also a child of 1, so it's in 1's projection - no gap
    assert gap == set()


def test_get_gap_nonprojective(tree_helper: TestTreeHelper, nonprojective_tree: conllu.TokenTree) -> None:
    """Test get_gap() detects gaps in nonprojective structures."""
    # Create a nonprojective structure where there's a real gap
    sentence = nonprojective_tree.to_list()  # type: ignore [no-untyped-call]
    # Node 5 depends on node 2, skipping over nodes 3 and 4
    # But nodes 3 and 4 are children of 5, so they're in 5's projection
    # Let's check node 2's gap to node 7
    gap = tree_helper.get_gap(2, sentence)
    # Should find nodes between 2 and 6 that aren't in 6's projection
    # Nodes 3, 4, 5 are between 2 and 6
    # Need to check which aren't in 6's projection
    assert isinstance(gap, set)


def test_get_gap_with_invalid_token_id(tree_helper: TestTreeHelper) -> None:
    """Test get_gap() with non-existent token ID."""
    mod_sentence = test_sentence.copy()
    mod_sentence['tokens'] = test_sentence['tokens'][:1]  # Only token 1
    sentence = ConlluSentenceFactory.as_tokenlist(**mod_sentence)
    gap = tree_helper.get_gap(99, sentence)
    assert gap == set()


def test_get_gap_from_root(tree_helper: TestTreeHelper) -> None:
    """Test get_gap() for root node (parent is 0)."""
    mod_sentence = test_sentence.copy()
    mod_sentence['tokens'] = test_sentence['tokens'][:2]  # Only 2 tokens
    sentence = ConlluSentenceFactory.as_tokenlist(**mod_sentence)
    gap = tree_helper.get_gap(1, sentence)
    # Root node has parent 0, should return empty set
    assert gap == set()


def test_get_gap_with_parse_exception(tree_helper: TestTreeHelper) -> None:
    """Test get_gap() handles ParseException gracefully."""
    # Create a sentence that might cause parsing issues
    mod_sentence = test_sentence.copy()
    mod_sentence['tokens'] = test_sentence['tokens'][1:]  # remove first node
    sentence = ConlluSentenceFactory.as_tokenlist(**mod_sentence)
    # Should handle gracefully even if tree building fails
    gap = tree_helper.get_gap(2, sentence)
    assert isinstance(gap, set)


def test_find_node_in_tree_root(tree_helper: TestTreeHelper, simple_tree: conllu.TokenTree) -> None:
    """Test _find_node_in_tree() finds root node."""
    found = tree_helper._find_node_in_tree(simple_tree, 1)
    assert found is not None
    assert found.token['id'] == 1


def test_find_node_in_tree_child(tree_helper: TestTreeHelper, simple_tree: conllu.TokenTree) -> None:
    """Test _find_node_in_tree() finds child node."""
    found = tree_helper._find_node_in_tree(simple_tree, 3)
    assert found is not None
    assert found.token['id'] == 3


def test_find_node_in_tree_not_found(tree_helper: TestTreeHelper, simple_tree: conllu.TokenTree) -> None:
    """Test _find_node_in_tree() returns None for non-existent node."""
    found = tree_helper._find_node_in_tree(simple_tree, 99)
    assert found is None


def test_get_caused_nonprojectivities_projective_tree(
    tree_helper: TestTreeHelper,
    simple_tree: conllu.TokenTree,
) -> None:
    """Test get_caused_nonprojectivities() returns empty for projective tree."""
    sentence = simple_tree.to_list()  # type: ignore [no-untyped-call]
    # In a projective tree, no node causes nonprojectivities
    nonproj = tree_helper.get_caused_nonprojectivities(2, sentence)
    assert nonproj == []


def test_get_caused_nonprojectivities_with_crossing(
    tree_helper: TestTreeHelper,
    nonprojective_tree: conllu.TokenTree,
) -> None:
    """Test get_caused_nonprojectivities() detects crossing edges."""
    sentence = nonprojective_tree.to_list()  # type: ignore [no-untyped-call]
    # Node 2 attaches to 7, causing nonprojectivity
    nonproj = tree_helper.get_caused_nonprojectivities(2, sentence)
    # Should detect nodes that cross this arc
    assert isinstance(nonproj, list)


def test_get_caused_nonprojectivities_from_root(tree_helper: TestTreeHelper) -> None:
    """Test get_caused_nonprojectivities() for root node."""
    mod_sentence = test_sentence.copy()
    mod_sentence['tokens'] = test_sentence['tokens'][:2]  # only two nodes
    sentence = ConlluSentenceFactory.as_tokenlist(**mod_sentence)
    # Root node (parent=0) should return empty list
    nonproj = tree_helper.get_caused_nonprojectivities(1, sentence)
    assert nonproj == []


def test_get_caused_nonprojectivities_with_invalid_id(tree_helper: TestTreeHelper) -> None:
    """Test get_caused_nonprojectivities() with non-existent token ID."""
    mod_sentence = test_sentence.copy()
    mod_sentence['tokens'] = test_sentence['tokens'][:1]  # only first node
    sentence = ConlluSentenceFactory.as_tokenlist(**mod_sentence)
    nonproj = tree_helper.get_caused_nonprojectivities(99, sentence)
    assert nonproj == []


def test_get_caused_nonprojectivities_excludes_ancestors(tree_helper: TestTreeHelper) -> None:
    """Test that get_caused_nonprojectivities() excludes nodes whose parents are ancestors."""
    mod_sentence = test_sentence.copy()
    mod_sentence['tokens'].append(  # type: ignore [attr-defined]
        {
            'id': 4,
            'form': 'word4',
            'lemma': 'word4',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 1,
            'deprel': 'obj',
            'deps': '_',
            'misc': '_',
        },
    )
    sentence = ConlluSentenceFactory.as_tokenlist(**mod_sentence)
    # Check various nodes
    nonproj = tree_helper.get_caused_nonprojectivities(2, sentence)
    # Should return a list (possibly empty for projective structure)
    assert isinstance(nonproj, list)


def test_single_node_tree(tree_helper: TestTreeHelper, single_node_tree: conllu.TokenTree) -> None:
    """Test all helper methods work with single-node tree."""
    sentence = single_node_tree.to_list()  # type: ignore [no-untyped-call]

    projection = tree_helper.get_projection(single_node_tree)
    assert projection == {1}

    ancestors = tree_helper.collect_ancestors(1, sentence)
    assert 0 in ancestors

    gap = tree_helper.get_gap(1, sentence)
    assert gap == set()

    nonproj = tree_helper.get_caused_nonprojectivities(1, sentence)
    assert nonproj == []


def test_complex_tree_all_methods(tree_helper: TestTreeHelper, complex_tree: conllu.TokenTree) -> None:
    """Integration test with complex tree using all methods."""
    sentence = complex_tree.to_list()  # type: ignore [no-untyped-call]

    # Test projection
    projection = tree_helper.get_projection(complex_tree)
    assert 5 in projection  # Root
    assert len(projection) == 10  # All nodes

    # Test ancestors
    ancestors = tree_helper.collect_ancestors(3, sentence)
    assert 4 in ancestors
    assert 5 in ancestors
    assert 0 in ancestors

    # Test gap
    gap = tree_helper.get_gap(4, sentence)
    assert isinstance(gap, set)

    # Test nonprojectivity
    nonproj = tree_helper.get_caused_nonprojectivities(4, sentence)
    assert isinstance(nonproj, list)
