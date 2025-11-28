"""ID sequence validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .helpers import is_empty_node, parse_empty_node_id
from .validation_mixin import BaseValidationMixin

if TYPE_CHECKING:
    import conllu


class IdSequenceValidationMixin(BaseValidationMixin):
    """Mixin providing ID sequence validation methods."""

    def _validate_id_sequence(self, sentence: conllu.TokenList) -> None:
        """Validate that ID sequence is correctly formed.

        Validates:
        - Word IDs form sequence 1, 2, 3... (no gaps, no duplicates, in order)
        - Empty node IDs are correctly sequenced (X.1, X.2, X.3 after word X)
        - Multiword tokens appear before their component words
        - IDs start at 1

        Arguments:
            sentence: Parsed sentence to validate

        """
        # Collect IDs and their properties
        word_ids, seen_word_ids, mwt_ranges, empty_nodes = self._collect_ids(sentence)

        # Validate word ID sequence
        self._validate_word_sequence(word_ids)

        # Validate duplicate word IDs
        self._check_duplicate_word_ids(seen_word_ids, word_ids)

        # Validate multiword token placement
        self._validate_mwt_placement(sentence, mwt_ranges)

        # Validate empty node sequences
        self._validate_empty_node_sequences(empty_nodes)

        # Validate empty node placement
        self._validate_empty_node_placement(sentence)

    def _collect_ids(
        self,
        sentence: conllu.TokenList,
    ) -> tuple[list[int], set[int], list[tuple[int, int, int]], dict[int, list[int]]]:
        """Collect all IDs from sentence.

        Returns:
            Tuple of (word_ids, seen_word_ids, mwt_ranges, empty_nodes)

        """
        word_ids: list[int] = []
        seen_word_ids: set[int] = set()
        mwt_ranges: list[tuple[int, int, int]] = []  # (start, end, position)
        empty_nodes: dict[int, list[int]] = {}  # word_id -> list of empty_node_ids

        for position, token in enumerate(sentence):
            token_id = token['id']

            if isinstance(token_id, tuple) and len(token_id) == 3:  # noqa: PLR2004
                if token_id[1] == '-':
                    # Multiword token: (start, '-', end)
                    start, _sep, end = token_id
                    mwt_ranges.append((start, end, position))
                elif token_id[1] == '.':
                    # Empty node: (word_id, '.', empty_id)
                    try:
                        word_id_str, empty_id_str = parse_empty_node_id(token_id)
                        word_id = int(word_id_str)
                        empty_id = int(empty_id_str)
                        if word_id not in empty_nodes:
                            empty_nodes[word_id] = []
                        empty_nodes[word_id].append(empty_id)
                    except ValueError:
                        # Invalid format - already reported by format validation
                        pass

            elif isinstance(token_id, int):
                # Regular word
                word_ids.append(token_id)
                seen_word_ids.add(token_id)

        return word_ids, seen_word_ids, mwt_ranges, empty_nodes

    def _validate_word_sequence(self, word_ids: list[int]) -> None:
        """Validate that word IDs form sequence 1, 2, 3..."""
        if not word_ids:
            return

        # Check that IDs start at 1
        if word_ids[0] != 1:
            expected_seq_str = ','.join(str(x) for x in range(1, len(word_ids) + 1))
            actual_seq_str = ','.join(str(x) for x in word_ids)
            self.reporter.warn(
                f"Word IDs should start at 1. Got '{actual_seq_str}'. Expected '{expected_seq_str}'.",
                'Format',
                testlevel=1,
                testid='word-id-not-starting-at-1',
            )

        # Check that IDs form sequence 1, 2, 3... (in order, no gaps)
        expected_seq_list = list(range(1, len(word_ids) + 1))
        if word_ids != expected_seq_list:
            expected_str = ','.join(str(x) for x in expected_seq_list)
            actual_str = ','.join(str(x) for x in word_ids)
            self.reporter.warn(
                f"Words do not form a sequence. Got '{actual_str}'. Expected '{expected_str}'.",
                'Format',
                testlevel=1,
                testid='word-id-sequence',
            )

    def _check_duplicate_word_ids(self, seen_word_ids: set[int], word_ids: list[int]) -> None:
        """Check for duplicate word IDs."""
        if len(word_ids) != len(seen_word_ids):
            # Find duplicates
            seen: set[int] = set()
            for word_id in word_ids:
                if word_id in seen:
                    self.reporter.warn(
                        f'Duplicate word ID: {word_id}',
                        'Format',
                        testlevel=1,
                        testid='duplicate-word-id',
                        node_id=str(word_id),
                    )
                seen.add(word_id)

    def _validate_mwt_placement(
        self,
        sentence: conllu.TokenList,
        mwt_ranges: list[tuple[int, int, int]],
    ) -> None:
        """Validate that multiword tokens appear before their component words."""
        for start, end, mwt_position in mwt_ranges:
            # Find positions of the component words
            for word_position, token in enumerate(sentence):
                token_id = token['id']
                if isinstance(token_id, int) and start <= token_id <= end and word_position <= mwt_position:
                    # Word appears at or before MWT - this is wrong
                    self.reporter.warn(
                        f'Multiword token {start}-{end} must appear before its component words',
                        'Format',
                        testlevel=1,
                        testid='mwt-not-before-words',
                        node_id=f'{start}-{end}',
                    )
                    break  # Only report once per MWT

    def _validate_empty_node_sequences(self, empty_nodes: dict[int, list[int]]) -> None:
        """Validate empty node sequences for each word."""
        for word_id, empty_ids in empty_nodes.items():
            # Empty nodes should be sequenced X.1, X.2, X.3...
            expected_empty_seq = list(range(1, len(empty_ids) + 1))
            if sorted(empty_ids) != expected_empty_seq:
                expected_str = ','.join(f'{word_id}.{x}' for x in expected_empty_seq)
                actual_str = ','.join(f'{word_id}.{x}' for x in sorted(empty_ids))
                self.reporter.warn(
                    f'Empty nodes after word {word_id} do not form correct sequence. '
                    f"Got '{actual_str}'. Expected '{expected_str}'.",
                    'Format',
                    testlevel=1,
                    testid='empty-node-sequence',
                    node_id=f'{word_id}.1',
                )

            # Check for duplicates
            if len(empty_ids) != len(set(empty_ids)):
                duplicates = [x for x in empty_ids if empty_ids.count(x) > 1]
                for dup in set(duplicates):
                    self.reporter.warn(
                        f'Duplicate empty node ID: {word_id}.{dup}',
                        'Format',
                        testlevel=1,
                        testid='duplicate-empty-node-id',
                        node_id=f'{word_id}.{dup}',
                    )

    def _validate_empty_node_placement(self, sentence: conllu.TokenList) -> None:
        """Validate that empty nodes appear after their word and before the next word."""
        for token_idx, token in enumerate(sentence):
            token_id = token['id']

            if not is_empty_node(token_id):
                continue

            try:
                word_id_str, _empty_id = parse_empty_node_id(token_id)
                word_id = int(word_id_str)

                # Find the position of word_id and word_id+1
                word_position: int | None = None
                next_word_position: int | None = None

                for idx, t in enumerate(sentence):
                    if isinstance(t['id'], int):
                        if t['id'] == word_id:
                            word_position = idx
                        elif t['id'] == word_id + 1:
                            next_word_position = idx
                            break

                # Format token_id as string for error messages
                token_id_str = f'{word_id}.{_empty_id}' if isinstance(token_id, tuple) else str(token_id)

                # Empty node should be after its word
                if word_position is not None and token_idx <= word_position:
                    self.reporter.warn(
                        f'Empty node {token_id_str} must appear after word {word_id}',
                        'Format',
                        testlevel=1,
                        testid='empty-node-not-after-word',
                        node_id=token_id_str,
                    )

                # Empty node should be before the next word (if it exists)
                if next_word_position is not None and token_idx >= next_word_position:
                    self.reporter.warn(
                        f'Empty node {token_id_str} must appear before word {word_id + 1}',
                        'Format',
                        testlevel=1,
                        testid='empty-node-not-before-next-word',
                        node_id=token_id_str,
                    )

            except ValueError:
                # Invalid format - already reported by format validation
                pass
