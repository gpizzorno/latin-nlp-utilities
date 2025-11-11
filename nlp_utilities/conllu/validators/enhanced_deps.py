"""Enhanced dependencies validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import regex as re

from nlp_utilities.constants import BASIC_HEAD_MATCHER, ENHANCED_HEAD_MATCHER

from .helpers import is_empty_node
from .validation_mixin import BaseValidationMixin

if TYPE_CHECKING:
    import conllu


class EnhancedDepsValidationMixin(BaseValidationMixin):
    """Mixin providing enhanced dependencies validation methods."""

    def _validate_enhanced_dependencies(self, sentence: conllu.TokenList) -> None:
        """Validate enhanced dependencies (DEPS column).

        Validates:
        - Enhanced dependency format
        - Head references exist
        - No self-loops
        - Root consistency
        - Orphan/empty node interactions (Level 3)

        Arguments:
            sentence: Parsed sentence to validate

        """
        # Collect all valid node IDs (words and empty nodes, not multiword tokens)
        valid_ids, has_empty_nodes = self._collect_valid_node_ids(sentence)
        has_orphan_in_deps = False

        # Validate DEPS for each word and empty node
        for token in sentence:
            # Skip multiword tokens
            if isinstance(token['id'], tuple):
                continue

            # Get DEPS (conllu library parses it into list of (deprel, head) tuples)
            deps = token.get('deps')

            # Skip if no enhanced dependencies
            if not deps or deps == '_':
                continue

            # Check if deps is parsed as a list
            if not isinstance(deps, list):
                self.reporter.warn(
                    f'Malformed DEPS column: {deps}',
                    'Format',
                    testlevel=2,
                    testid='invalid-deps',
                    node_id=str(token['id']),
                )
                continue

            # Validate each enhanced dependency
            for deprel, head in deps:
                self._validate_enhanced_dep(token['id'], deprel, head, valid_ids)

                # Track orphan relations
                deprel_base = deprel.split(':')[0]
                if deprel_base == 'orphan':
                    has_orphan_in_deps = True

        # Level 3: Check orphan/empty node consistency
        if self.level >= 3 and has_empty_nodes and has_orphan_in_deps:  # noqa: PLR2004
            self.reporter.warn(
                "'orphan' not allowed in enhanced graph when empty nodes are present",
                'Enhanced',
                testlevel=3,
                testid='eorphan-with-empty-node',
            )

    def _collect_valid_node_ids(self, sentence: conllu.TokenList) -> tuple[set[str], bool]:
        """Collect all valid node IDs for enhanced dependency validation.

        Arguments:
            sentence: Parsed sentence

        Returns:
            Tuple of (set of valid IDs as strings, whether sentence has empty nodes)

        """
        valid_ids = set()
        has_empty_nodes = False

        for token in sentence:
            token_id = token['id']
            if isinstance(token_id, tuple):
                # Skip multiword tokens
                continue
            if isinstance(token_id, str) and is_empty_node(token_id):
                has_empty_nodes = True
            valid_ids.add(str(token_id))

        # Add root
        valid_ids.add('0')

        return valid_ids, has_empty_nodes

    def _validate_enhanced_dep(
        self,
        token_id: int | str,
        deprel: str,
        head: int | str,
        valid_ids: set[str],
    ) -> None:
        """Validate a single enhanced dependency.

        Checks:
        - Head format is valid (integer or decimal for empty nodes)
        - Head ID exists in the sentence
        - No self-loops
        - Root relation consistency (head=0 must have deprel='root')
        - Relation type is valid (level 2-3: universal, level 4+: language-specific)

        Arguments:
            token_id: ID of the dependent token
            deprel: Enhanced dependency relation
            head: Head ID (can be int or decimal string for empty nodes)
            valid_ids: Set of valid node IDs in the sentence

        """
        # Regex patterns for enhanced head validation
        basic_head_re = re.compile(BASIC_HEAD_MATCHER)
        enhanced_head_re = re.compile(ENHANCED_HEAD_MATCHER)

        head_str = str(head)

        # Validate head format
        if isinstance(head, int):
            # Simple integer head
            if not basic_head_re.match(head_str):
                self.reporter.warn(
                    f'Invalid enhanced head reference: {head_str}',
                    'Format',
                    testlevel=2,
                    testid='invalid-ehead',
                    node_id=str(token_id),
                )
        elif not enhanced_head_re.match(head_str):
            # Could be decimal (empty node reference)
            self.reporter.warn(
                f'Invalid enhanced head reference: {head_str}',
                'Format',
                testlevel=2,
                testid='invalid-ehead',
                node_id=str(token_id),
            )

        # Check if head exists
        if head_str not in valid_ids:
            self.reporter.warn(
                f'Undefined enhanced head reference (no such ID): {head_str}',
                'Enhanced',
                testlevel=2,
                testid='unknown-ehead',
                node_id=str(token_id),
            )

        # Check for self-loops
        if str(token_id) == head_str:
            self.reporter.warn(
                f'Enhanced dependency self-loop: {token_id} -> {head_str}',
                'Enhanced',
                testlevel=2,
                testid='deps-self-loop',
                node_id=str(token_id),
            )

        # Validate root consistency
        if head_str == '0' and deprel != 'root':
            self.reporter.warn(
                "Enhanced relation type must be 'root' if head is 0",
                'Enhanced',
                testlevel=2,
                testid='enhanced-0-is-not-root',
                node_id=str(token_id),
            )
        elif head_str != '0' and deprel == 'root':
            self.reporter.warn(
                "Enhanced relation type cannot be 'root' if head is not 0",
                'Enhanced',
                testlevel=2,
                testid='enhanced-root-is-not-0',
                node_id=str(token_id),
            )

        # Level 2-3: Validate enhanced deprel against universal relations (base part only)
        # Enhanced deps can have subtypes and case information, so we only check the base
        if self.level >= 2 and self.level < 4 and self.universal_deprels:  # noqa: PLR2004
            # Extract base relation (first part before colon)
            base_deprel = deprel.split(':')[0]
            # 'ref' is a special universal relation only allowed in enhanced dependencies
            if base_deprel not in self.universal_deprels and base_deprel != 'ref':
                self.reporter.warn(
                    f"Unknown universal enhanced relation: '{deprel}'",
                    'Enhanced',
                    testlevel=2,
                    testid='unknown-edeprel',
                    node_id=str(token_id),
                )
