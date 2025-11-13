"""Factories for conllu test data generation."""

from __future__ import annotations


class TreeStructureFactory:
    """Factory for creating tree structures for testing."""

    @classmethod
    def create_linear_tree(cls, size: int = 5) -> dict[int, int]:
        """Create a linear tree structure.

        Args:
            size: Number of tokens

        Returns:
            Dictionary mapping token_id to head_id

        """
        tree = {1: 0}  # Root
        for i in range(2, size + 1):
            tree[i] = i - 1  # Each token depends on the previous one
        return tree

    @classmethod
    def create_with_nonprojectivity(cls) -> dict[int, int]:
        """Create a tree with nonprojective dependencies.

        Returns:
            Dictionary mapping token_id to head_id with nonprojective arc

        """
        # Example: "A hearing on the issue is scheduled"
        # where 'issue' (5) depends on 'hearing' (2), creating nonprojectivity
        return {
            1: 2,  # A -> hearing
            2: 7,  # hearing -> scheduled (root is 7)
            3: 5,  # on -> issue
            4: 5,  # the -> issue
            5: 2,  # issue -> hearing (nonprojective!)
            6: 7,  # is -> scheduled
            7: 0,  # scheduled -> root
        }

    @classmethod
    def create_with_cycle(cls) -> dict[int, int]:
        """Create a tree with a cycle (invalid structure).

        Returns:
            Dictionary mapping token_id to head_id with a cycle

        """
        return {
            1: 2,  # 1 -> 2
            2: 3,  # 2 -> 3
            3: 1,  # 3 -> 1 (cycle!)
        }

    @classmethod
    def create_disconnected(cls) -> dict[int, int]:
        """Create a disconnected graph (multiple roots).

        Returns:
            Dictionary mapping token_id to head_id with multiple roots

        """
        return {
            1: 0,  # First root
            2: 1,  # Depends on first root
            3: 0,  # Second root (disconnected!)
            4: 3,  # Depends on second root
        }
