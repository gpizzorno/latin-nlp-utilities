"""Helper functions for token type detection in CoNLL-U files."""

from __future__ import annotations

import conllu
import regex as re

from conllu_tools.constants import EMPTY_NODE, EMPTY_NODE_ID, MULTIWORD_TOKEN


class TreeHelperMixin:
    """Mixin providing tree operation helper methods."""

    def get_projection(self, tree_node: conllu.TokenTree) -> set[int]:
        """Collect all descendant node IDs (projection) from a tree node.

        Args:
            tree_node: Root node of subtree

        Returns:
            Set of node IDs in the projection (including the root node itself)

        """
        projection: set[int] = {tree_node.token['id']}
        self._collect_projection_recursive(tree_node, projection)
        return projection

    def _collect_projection_recursive(self, node: conllu.TokenTree, projection: set[int]) -> None:
        """Recursively collect descendant IDs.

        Args:
            node: Current node
            projection: Set to accumulate IDs into

        Note:
            This matches the old validator behavior - only children are added to projection,
            NOT the node itself.

        """
        for child in node.children:
            child_id = child.token['id']
            if child_id in projection:
                # Cycle detected - skip this child
                continue
            projection.add(child_id)
            self._collect_projection_recursive(child, projection)

    def collect_ancestors(self, token_id: int, sentence: conllu.TokenList) -> list[int]:
        """Collect ancestor node IDs from a token up to root.

        Args:
            token_id: Starting token ID
            sentence: Parsed sentence

        Returns:
            List of ancestor IDs (including root 0)

        """
        ancestors = []
        current_id = token_id

        # Create a lookup for tokens by ID
        token_by_id = {}
        for token in sentence:
            if isinstance(token['id'], int):
                token_by_id[token['id']] = token

        # Traverse up to root
        while current_id != 0:
            if current_id not in token_by_id:
                # Invalid token ID
                break

            token = token_by_id[current_id]
            head = token.get('head')

            if head is None:
                break

            if head in ancestors:
                # Cycle detected
                break

            ancestors.append(head)
            current_id = head

        return ancestors

    def get_gap(self, token_id: int, sentence: conllu.TokenList) -> set[int]:
        """Get the gap between a node and its parent.

        A gap is the set of nodes between a node and its parent that are NOT
        in the parent's projection (i.e., not descendants of the parent).

        Args:
            token_id: Token ID to analyze
            sentence: Parsed sentence

        Returns:
            Set of node IDs in the gap

        """
        # Create a lookup for tokens by ID
        token_by_id = {}
        for token in sentence:
            if isinstance(token['id'], int):
                token_by_id[token['id']] = token

        if token_id not in token_by_id:
            return set()

        token = token_by_id[token_id]
        parent_id = token.get('head')

        if parent_id is None or parent_id == 0:
            return set()

        # Get the range of nodes between token and parent
        range_between = (
            set(range(token_id + 1, parent_id)) if token_id < parent_id else set(range(parent_id + 1, token_id))
        )

        if not range_between:
            return set()

        # Build tree and get parent's projection
        try:
            tree = sentence.to_tree()
            # Find the parent node in the tree
            parent_node = self._find_node_in_tree(tree, parent_id)
            if parent_node:
                projection = self.get_projection(parent_node)
                # Gap is nodes in the range that are NOT in parent's projection
                return range_between - projection
        except (conllu.exceptions.ParseException, AttributeError):
            # If we can't build tree, return empty set
            return set()

        return set()

    def _find_node_in_tree(self, tree_node: conllu.TokenTree, target_id: int) -> conllu.TokenTree | None:
        """Find a specific node in the tree by ID.

        Args:
            tree_node: Root of tree/subtree to search
            target_id: Target node ID

        Returns:
            TokenTree node if found, None otherwise

        """
        if tree_node.token['id'] == target_id:
            return tree_node

        for child in tree_node.children:
            result = self._find_node_in_tree(child, target_id)
            if result:
                return result

        return None

    def get_caused_nonprojectivities(self, token_id: int, sentence: conllu.TokenList) -> list[int]:
        """Check which nodes are in gaps caused by this node's nonprojective attachment.

        Returns nodes that are NOT ancestors of this node and lie on the opposite
        side of this node from their parent. Only reports if the node's parent
        is not in the same gap (to avoid blaming a node that was dragged into
        a gap by its parent).

        Args:
            token_id: Token ID to analyze
            sentence: Parsed sentence

        Returns:
            Sorted list of node IDs that are nonprojective because of this node

        """
        # Create a lookup for tokens by ID
        token_by_id = {}
        max_id = 0
        for token in sentence:
            if isinstance(token['id'], int):
                token_by_id[token['id']] = token
                max_id = max(max_id, token['id'])

        if token_id not in token_by_id:
            return []

        token = token_by_id[token_id]
        parent_id = token.get('head')

        if parent_id is None or parent_id == 0:
            return []

        # Get ancestors of this node
        ancestors = self.collect_ancestors(token_id, sentence)
        ancestors_set = set(ancestors)

        # Get ranges to either side of token_id
        # Don't look beyond the parent (if it's in the same gap, it's the parent's responsibility)
        if parent_id < token_id:
            left = range(parent_id + 1, token_id)
            right = range(token_id + 1, max_id + 1)
        else:
            left = range(1, token_id)
            right = range(token_id + 1, parent_id)

        # Exclude nodes whose parents are ancestors of token_id
        left_non_ancestor = [x for x in left if x in token_by_id and token_by_id[x].get('head') not in ancestors_set]
        right_non_ancestor = [x for x in right if x in token_by_id and token_by_id[x].get('head') not in ancestors_set]

        # Find crossing edges
        left_cross = [x for x in left_non_ancestor if token_by_id[x].get('head', 0) > token_id]
        right_cross = [x for x in right_non_ancestor if token_by_id[x].get('head', 0) < token_id]

        # Exclude nonprojectivities caused by ancestors of token_id
        if parent_id < token_id:
            right_cross = [x for x in right_cross if token_by_id[x].get('head', 0) > parent_id]
        else:
            left_cross = [x for x in left_cross if token_by_id[x].get('head', 0) < parent_id]

        return sorted(left_cross + right_cross)


def is_word(token_id: int | tuple[int, int] | str) -> bool:
    """Check if the token ID represents a word (simple integer).

    Arguments:
        token_id: Token ID in various formats (int, tuple, or string)

    Returns:
        True if the token ID represents a regular word token

    Examples:
        >>> is_word(1)
        True
        >>> is_word("5")
        True
        >>> is_word((1, 2))
        False
        >>> is_word("2.1")
        False

    """
    if isinstance(token_id, int):
        return token_id >= 1
    if isinstance(token_id, tuple):
        return False
    # String format
    return bool(re.match(r'^[1-9][0-9]*$', str(token_id)))


def is_multiword_token(token_id: int | tuple[int, str, int] | str) -> bool:
    """Check if the token ID represents a multiword token (range like 1-2).

    Arguments:
        token_id: Token ID in various formats (int, tuple, or string)

    Returns:
        True if the token ID represents a multiword token range

    Examples:
        >>> is_multiword_token((1, 2))
        True
        >>> is_multiword_token("1-2")
        True
        >>> is_multiword_token(1)
        False
        >>> is_multiword_token("2.1")
        False

    """
    if isinstance(token_id, tuple) and not is_empty_node(token_id):
        return True
    if isinstance(token_id, int):
        return False
    # String format
    return bool(re.match(MULTIWORD_TOKEN, str(token_id)))


def is_empty_node(token_id: int | tuple[int, str, int] | str) -> bool:
    """Check if the token ID represents an empty node (decimal like 1.1).

    Arguments:
        token_id: Token ID in various formats (int, tuple, or string)

    Returns:
        True if the token ID represents an empty node

    Examples:
        >>> is_empty_node("2.1")
        True
        >>> is_empty_node((2, '.', 1))
        True
        >>> is_empty_node("10.25")
        True
        >>> is_empty_node(1)
        False
        >>> is_empty_node((1, '-', 2))
        False

    """
    if isinstance(token_id, int):
        return False
    if isinstance(token_id, tuple):
        # conllu library parses empty nodes as (word_id, '.', empty_id)
        return len(token_id) == 3 and token_id[1] == '.'  # noqa: PLR2004
    # String format
    return bool(re.match(EMPTY_NODE, str(token_id)))


def parse_empty_node_id(token_id: tuple[int, str, int] | str) -> tuple[str, str]:
    """Parse an empty node ID into (word_id, empty_id) components.

    Arguments:
        token_id: Empty node ID like "3.1" or tuple (3, '.', 1)

    Returns:
        Tuple of (word_id, empty_id) as strings, e.g., ("3", "1")

    Raises:
        ValueError: If token_id is not a valid empty node ID

    Examples:
        >>> parse_empty_node_id("3.1")
        ('3', '1')
        >>> parse_empty_node_id((3, '.', 1))
        ('3', '1')
        >>> parse_empty_node_id("10.25")
        ('10', '25')
        >>> parse_empty_node_id("1-2")
        Traceback (most recent call last):
            ...
        ValueError: Not a valid empty node ID: 1-2

    """
    # Handle tuple format from conllu library: (word_id, '.', empty_id)
    if isinstance(token_id, tuple):
        if len(token_id) == 3 and token_id[1] == '.':  # noqa: PLR2004
            return (str(token_id[0]), str(token_id[2]))
        msg = f'Not a valid empty node ID tuple: {token_id}'
        raise ValueError(msg)

    # Handle string format
    m = re.match(EMPTY_NODE_ID, str(token_id))
    if not m:
        msg = f'Not a valid empty node ID: {token_id}'
        raise ValueError(msg)
    word_id, empty_id = m.groups()
    return str(word_id), str(empty_id)


def is_word_part_of_mwt(
    token_id: int,
    sentence: conllu.TokenList,
) -> bool:
    """Check if a word token ID is part of a multiword token range."""
    for token in sentence:
        if is_multiword_token(token['id']):
            start, _sep, end = get_mwt_range_from_id(token['id'])
            if start <= token_id <= end:
                return True
    return False


def is_part_of_mwt(
    token_id: int | tuple[int, int] | str,
    mwt_ranges: list[tuple[int, int]],
) -> bool:
    """Check if a token ID is part of a multiword token range."""
    if not isinstance(token_id, int):
        return False
    return any(start <= token_id <= end for start, end in mwt_ranges)


def get_mwt_range_from_id(token_id: tuple[int, str, int] | str) -> tuple[int, str, int]:
    """Get the MWT range (start, end) from a token ID if it is an MWT.

    Arguments:
        token_id: Token ID as tuple or string

    Returns:
        Tuple of (start, separator, end)

    Raises:
        ValueError: If token_id is not a valid MWT ID

    """
    if isinstance(token_id, tuple):
        return token_id
    if isinstance(token_id, str):
        m = re.match(MULTIWORD_TOKEN, token_id)
        if m:
            start_str, sep, end_str = m.groups()
            return (int(start_str), sep, int(end_str))

    msg = f'Not a valid MWT ID: {token_id}'
    raise ValueError(msg)


def add_token_to_reconstruction(
    token: conllu.Token,
    reconstructed_parts: list[str],
) -> None:
    """Add a token's form to the reconstruction, with space handling."""
    reconstructed_parts.append(token['form'])

    # Check for SpaceAfter=No
    misc = token.get('misc')
    if misc and isinstance(misc, dict) and misc.get('SpaceAfter') == 'No':
        return  # Don't add space

    reconstructed_parts.append(' ')


def get_alt_language(token: conllu.Token) -> str | None:
    """Extract alternative language from MISC column.

    Arguments:
        token: Token to check

    Returns:
        Language code if Lang= attribute exists, None otherwise

    """
    if not token['misc']:
        return None

    # Check for Lang= attribute in MISC
    misc = token['misc']
    if isinstance(misc, dict) and 'Lang' in misc:
        lang_value = misc['Lang']
        return str(lang_value) if lang_value else None

    return None
