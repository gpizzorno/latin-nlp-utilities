"""Structure validation."""

from __future__ import annotations

import conllu

from .helpers import is_empty_node
from .validation_mixin import BaseValidationMixin


class StructureValidationMixin(BaseValidationMixin):
    """Mixin providing structure validation methods."""

    def _validate_structure(self, sentence: conllu.TokenList) -> None:  # noqa: C901
        """Validate tree structure.

        Arguments:
            sentence: Parsed sentence

        """
        # Validate multiword token ranges
        if self.level >= 1:
            self._validate_multiword_token_ranges(sentence)

        # Filter out empty nodes and multiword tokens when checking for roots
        # Empty nodes have _ in HEAD/DEPREL, multiword tokens are ranges
        words_only = [
            token
            for token in sentence
            if not isinstance(token['id'], tuple)  # Not a multiword token
            and not (isinstance(token['id'], str) and is_empty_node(token['id']))  # Not an empty node
        ]

        # Validate that there's exactly one root
        roots = [token for token in words_only if token['head'] == 0]
        if len(roots) == 0:
            self.reporter.warn(
                'Sentence has no root',
                'Syntax',
                testlevel=2,
                testid='no-root',
            )
        elif len(roots) > 1:
            self.reporter.warn(
                f'Sentence has multiple roots: {[t["id"] for t in roots]}',
                'Syntax',
                testlevel=2,
                testid='multiple-roots',
            )

        # Validate UPOS tags
        for token in sentence:
            # Skip empty nodes for UPOS validation (they should have _)
            if isinstance(token['id'], str) and is_empty_node(token['id']):
                continue

            if token['upos'] and token['upos'] not in self.upos_tags and token['upos'] != '_':
                self.reporter.warn(
                    f'Unknown UPOS tag: {token["upos"]!r}',
                    'Morpho',
                    testlevel=2,
                    testid='unknown-upos',
                    node_id=str(token['id']),
                )

            # Validate deprel (skip empty nodes - they should have _)
            if (
                token['deprel']
                and token['deprel'] != '_'
                and not (isinstance(token['id'], str) and is_empty_node(token['id']))
            ):
                deprel = token['deprel'].split(':')[0]

                # Level 2-3: Validate against universal deprels
                if (
                    self.level >= 2  # noqa: PLR2004
                    and self.level < 4  # noqa: PLR2004
                    and self.universal_deprels
                    and deprel not in self.universal_deprels
                ):
                    self.reporter.warn(
                        f"Unknown universal DEPREL: '{token['deprel']}'",
                        'Syntax',
                        testlevel=2,
                        testid='unknown-deprel',
                        node_id=str(token['id']),
                    )

                if token['head'] == 0 and deprel != 'root':
                    self.reporter.warn(
                        "DEPREL must be 'root' if HEAD is 0",
                        'Syntax',
                        testlevel=2,
                        testid='0-is-not-root',
                        node_id=str(token['id']),
                    )
                elif token['head'] != 0 and deprel == 'root':
                    self.reporter.warn(
                        "DEPREL cannot be 'root' if HEAD is not 0",
                        'Syntax',
                        testlevel=2,
                        testid='root-is-not-0',
                        node_id=str(token['id']),
                    )

        # Validate HEAD references
        self._validate_head_references(sentence)

        # Build and validate tree structure
        self._build_and_validate_tree(sentence)

    def _validate_head_references(self, sentence: conllu.TokenList) -> None:
        """Validate that HEAD references existing token IDs.

        Arguments:
            sentence: Parsed sentence

        Note:
            The conllu library validates HEAD format during parsing (must be numeric).
            This method validates that HEAD values reference actual token IDs in the sentence.

        """
        # Build set of valid token IDs (words and empty nodes)
        valid_ids: set[int | str] = set()
        for token in sentence:
            token_id = token['id']
            # Include regular word IDs (integers) or empty node IDs (strings like "1.1")
            if isinstance(token_id, int) or (isinstance(token_id, str) and is_empty_node(token_id)):
                valid_ids.add(token_id)
            # Skip multiword tokens (tuples like (1, 2))

        # Validate HEAD for each word token
        for token in sentence:
            token_id = token['id']

            # Skip multiword tokens (they should have _ in HEAD, already validated)
            if isinstance(token_id, tuple):
                continue

            # Skip empty nodes (they should have _ in HEAD, already validated)
            if isinstance(token_id, str) and is_empty_node(token_id):
                continue

            # Get HEAD value
            head = token.get('head')
            if head is None or head == '_':
                # Already reported in format validation
                continue

            # Check if HEAD references a valid ID or is root (0)
            if head != 0 and head not in valid_ids:
                self.reporter.warn(
                    f"Undefined HEAD (no such ID): '{head}'",
                    'Syntax',
                    testlevel=2,
                    testid='unknown-head',
                    node_id=str(token_id),
                )

    def _validate_multiword_token_ranges(self, sentence: conllu.TokenList) -> None:
        """Validate that multiword token ranges are valid and non-overlapping.

        Checks:
        - Multiword token ranges don't overlap
        - All word IDs referenced by multiword tokens exist

        Arguments:
            sentence: Parsed sentence to validate

        """
        # Collect all word IDs and multiword token ranges
        word_ids = set()
        mwt_ranges = []

        for token in sentence:
            token_id = token['id']
            if isinstance(token_id, tuple):
                # Multiword token - ID is (start, '-', end)
                mwt_ranges.append((token_id[0], token_id[2], token))
            elif isinstance(token_id, int):
                # Regular word
                word_ids.add(token_id)

        # Check for overlapping ranges
        covered: set[int] = set()
        for start, end, _token in mwt_ranges:
            token_id_str = f'{start}-{end}'

            # Check if this range overlaps with previously seen ranges
            current_range = set(range(start, end + 1))
            overlap = covered & current_range
            if overlap:
                self.reporter.warn(
                    f'Multiword token range {token_id_str} overlaps with other ranges',
                    'Format',
                    testlevel=1,
                    testid='overlapping-mwt',
                    node_id=token_id_str,
                )
            covered |= current_range

            # Check that all words in the range exist
            for word_id in range(start, end + 1):
                if word_id not in word_ids:
                    self.reporter.warn(
                        f'Multiword token {token_id_str} references non-existent word ID {word_id}',
                        'Format',
                        testlevel=1,
                        testid='mwt-invalid-range',
                        node_id=token_id_str,
                    )

    def _build_and_validate_tree(self, sentence: conllu.TokenList) -> conllu.TokenTree | None:
        """Build tree structure and validate cycles/connectivity.

        Arguments:
            sentence: Parsed sentence

        Returns:
            TokenTree if successful, None if tree cannot be built

        """
        # Check for self-loops before calling to_tree()
        for token in sentence:
            token_id = token['id']
            # Skip multiword tokens and empty nodes
            if isinstance(token_id, tuple) or (isinstance(token_id, str) and is_empty_node(token_id)):
                continue

            head = token.get('head')
            if head == token_id:
                self.reporter.warn(
                    f'HEAD==ID for token {token_id} (self-loop)',
                    'Syntax',
                    testlevel=2,
                    testid='head-self-loop',
                    node_id=str(token_id),
                )
                return None

        # Try to build the tree using conllu library
        try:
            return sentence.to_tree()
        except conllu.exceptions.ParseException as e:
            # Tree building failed - report the error
            error_msg = str(e)
            if 'cycle' in error_msg.lower() or 'tree' in error_msg.lower():
                self.reporter.warn(
                    f'Non-tree structure: {error_msg}',
                    'Syntax',
                    testlevel=2,
                    testid='non-tree',
                )
            elif 'no head node' in error_msg.lower() or 'root' in error_msg.lower():
                # This should have been caught by root validation above,
                # but report it here if the library caught it
                self.reporter.warn(
                    f'Tree structure error: {error_msg}',
                    'Syntax',
                    testlevel=2,
                    testid='tree-structure-error',
                )
            else:
                # Generic tree building error
                self.reporter.warn(
                    f'Cannot build tree: {error_msg}',
                    'Syntax',
                    testlevel=2,
                    testid='tree-building-error',
                )
            return None
