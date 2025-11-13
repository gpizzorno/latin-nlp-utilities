"""Helper methods for tree operations and projectivity analysis."""

from __future__ import annotations

import conllu


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
