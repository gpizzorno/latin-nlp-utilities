"""Enhanced dependencies validation."""

from __future__ import annotations

import conllu
import regex as re

from conllu_tools.constants import BASIC_HEAD_MATCHER, ENHANCED_HEAD_MATCHER

from .validation_mixin import BaseValidationMixin


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
            token_id = token['id']

            # Skip multiword tokens (tuple with '-' separator)
            if isinstance(token_id, tuple) and len(token_id) == 3 and token_id[1] == '-':  # noqa: PLR2004
                continue

            # Get DEPS (conllu library parses it into list of (deprel, head) tuples)
            deps = token.get('deps')

            # Skip if no enhanced dependencies
            if not deps or deps == '_':
                continue

            # Check if deps is parsed as a list
            if not isinstance(deps, list):
                # Convert token_id to string for error reporting
                token_id_str = self._token_id_to_string(token_id)
                self.reporter.warn(
                    f'Malformed DEPS column: {deps}',
                    'Format',
                    testlevel=2,
                    testid='invalid-deps',
                    node_id=token_id_str,
                )
                continue

            # Validate DEPS sorting and duplicates
            self._validate_deps_structure(token_id, deps)

            # Validate each enhanced dependency
            for deprel, head in deps:
                self._validate_enhanced_dep(token_id, deprel, head, valid_ids)

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

        # Level 2: Validate enhanced graph connectivity
        if self.level >= 2:  # noqa: PLR2004
            self._validate_enhanced_graph_connectivity(sentence, valid_ids)

    def _validate_enhanced_graph_connectivity(
        self,
        sentence: conllu.TokenList,
        valid_ids: set[str],
    ) -> None:
        """Validate that the enhanced graph is connected.

        According to UD v2 guidelines, all nodes must be reachable from enhanced roots.
        Checks that every word and empty node has a path to root in the enhanced graph.

        Arguments:
            sentence: Parsed sentence
            valid_ids: Set of valid node IDs (excluding root '0')

        """
        # Build enhanced graph structure
        egraph = self._build_enhanced_graph(sentence)

        if not egraph:
            # No enhanced dependencies found - this is valid
            return

        # Compute reachable nodes from root (0)
        reachable: set[str] = set()

        # Start from root (0) and traverse all reachable nodes
        self._collect_reachable_nodes('0', egraph, reachable)

        # Find unreachable nodes (excluding root itself)
        node_ids = valid_ids - {'0'}
        unreachable = node_ids - reachable

        if unreachable:
            # Sort for consistent error messages
            sorted_unreachable = sorted(
                unreachable,
                key=lambda x: (float(x.replace('.', '')) if '.' in x else float(x)),
            )
            self.reporter.warn(
                f'Enhanced graph is not connected. Nodes {sorted_unreachable} are not reachable from any root',
                'Enhanced',
                testlevel=2,
                testid='unconnected-egraph',
            )

    def _build_enhanced_graph(self, sentence: conllu.TokenList) -> dict[str, set[str]]:
        """Build enhanced graph structure from DEPS column.

        Returns a dictionary mapping each node ID to its set of children in the enhanced graph.

        Arguments:
            sentence: Parsed sentence

        Returns:
            Dictionary: {parent_id: set of child_ids}

        """
        egraph: dict[str, set[str]] = {}
        has_enhanced_deps = False

        for token in sentence:
            token_id = token['id']

            # Skip multiword tokens (tuple with '-' separator)
            if isinstance(token_id, tuple) and len(token_id) == 3 and token_id[1] == '-':  # noqa: PLR2004
                continue

            # Convert token_id to string
            token_id_str = self._token_id_to_string(token_id)
            deps = token.get('deps')

            # Skip if no enhanced dependencies
            if not deps or deps == '_' or not isinstance(deps, list):
                continue

            has_enhanced_deps = True

            # Add edges from each head to this token
            for _deprel, head in deps:
                head_str = self._head_to_string(head)
                egraph.setdefault(head_str, set()).add(token_id_str)

        # Return None if no enhanced dependencies exist
        return egraph if has_enhanced_deps else {}

    def _collect_reachable_nodes(
        self,
        node_id: str,
        egraph: dict[str, set[str]],
        reachable: set[str],
    ) -> None:
        """Recursively collect all nodes reachable from a given node.

        Uses depth-first search with cycle detection.

        Arguments:
            node_id: Starting node ID
            egraph: Enhanced graph structure
            reachable: Set to collect reachable node IDs (modified in place)

        """
        # Get children of this node
        children = egraph.get(node_id, set())

        for child in children:
            # Skip if already visited (cycle detection)
            if child in reachable:
                continue

            # Mark as reachable
            reachable.add(child)

            # Recursively visit children
            self._collect_reachable_nodes(child, egraph, reachable)

    def _get_node_parents(self, sentence: conllu.TokenList, node_id: str) -> list[tuple[str, str]]:
        """Get list of (head, deprel) tuples for a node's enhanced parents.

        Arguments:
            sentence: Parsed sentence
            node_id: Node ID to find parents for

        Returns:
            List of (head_id, deprel) tuples

        """
        for token in sentence:
            if str(token['id']) == node_id:
                deps = token.get('deps')
                if deps and deps != '_' and isinstance(deps, list):
                    return [(self._head_to_string(head), deprel) for deprel, head in deps]
                return []
        return []

    def _head_to_string(self, head: int | str | tuple[int, str, int]) -> str:
        """Convert head to string representation.

        Arguments:
            head: Head ID (int, string, or tuple for empty nodes)

        Returns:
            String representation of head ID

        """
        if isinstance(head, tuple):
            # Empty node: (major, '.', minor) -> "major.minor"
            return f'{head[0]}.{head[2]}'
        return str(head)

    def _token_id_to_string(self, token_id: int | str | tuple[int, str, int]) -> str:
        """Convert token ID to string representation.

        Arguments:
            token_id: Token ID (int, string, or tuple)

        Returns:
            String representation of token ID

        """
        if isinstance(token_id, tuple) and len(token_id) == 3:  # noqa: PLR2004
            # Could be MWT (major, '-', minor) or empty node (major, '.', minor)
            return f'{token_id[0]}{token_id[1]}{token_id[2]}'
        return str(token_id)

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

            # Check if this is a tuple
            if isinstance(token_id, tuple):
                # Distinguish between MWT (middle element '-') and empty node (middle element '.')
                if len(token_id) == 3 and token_id[1] == '.':  # noqa: PLR2004
                    # This is an empty node
                    has_empty_nodes = True
                    # Convert to string format "major.minor"
                    valid_ids.add(f'{token_id[0]}.{token_id[2]}')
                # else: MWT range, skip it
                continue

            # Regular word ID (int)
            valid_ids.add(str(token_id))

        # Add root
        valid_ids.add('0')

        return valid_ids, has_empty_nodes

    def _validate_enhanced_dep(  # noqa: C901
        self,
        token_id: int | str | tuple[int, str, int],
        deprel: str,
        head: int | str | tuple[int, str, int],
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
            token_id: ID of the dependent token (can be int, string, or tuple)
            deprel: Enhanced dependency relation
            head: Head ID (can be int, string, or tuple for empty nodes)
            valid_ids: Set of valid node IDs in the sentence

        """
        # Convert IDs to string format
        token_id_str = self._token_id_to_string(token_id)
        head_str = self._head_to_string(head)

        # Regex patterns for enhanced head validation
        basic_head_re = re.compile(BASIC_HEAD_MATCHER)
        enhanced_head_re = re.compile(ENHANCED_HEAD_MATCHER)

        # Validate head format
        if isinstance(head, int):
            # Simple integer head
            if not basic_head_re.match(head_str):
                self.reporter.warn(
                    f'Invalid enhanced head reference: {head_str}',
                    'Format',
                    testlevel=2,
                    testid='invalid-ehead',
                    node_id=token_id_str,
                )
        elif isinstance(head, tuple):
            # Empty node head (tuple form) - validate decimal format
            if not enhanced_head_re.match(head_str):
                self.reporter.warn(
                    f'Invalid enhanced head reference: {head_str}',
                    'Format',
                    testlevel=2,
                    testid='invalid-ehead',
                    node_id=token_id_str,
                )
        elif not enhanced_head_re.match(head_str):
            # String head - could be decimal (empty node reference)
            self.reporter.warn(
                f'Invalid enhanced head reference: {head_str}',
                'Format',
                testlevel=2,
                testid='invalid-ehead',
                node_id=token_id_str,
            )

        # Check if head exists
        if head_str not in valid_ids:
            self.reporter.warn(
                f'Undefined enhanced head reference (no such ID): {head_str}',
                'Enhanced',
                testlevel=2,
                testid='unknown-ehead',
                node_id=token_id_str,
            )

        # Check for self-loops
        if token_id_str == head_str:
            self.reporter.warn(
                f'Enhanced dependency self-loop: {token_id_str} -> {head_str}',
                'Enhanced',
                testlevel=2,
                testid='deps-self-loop',
                node_id=token_id_str,
            )

        # Validate root consistency
        if head_str == '0' and deprel != 'root':
            self.reporter.warn(
                "Enhanced relation type must be 'root' if head is 0",
                'Enhanced',
                testlevel=2,
                testid='enhanced-0-is-not-root',
                node_id=token_id_str,
            )
        elif head_str != '0' and deprel == 'root':
            self.reporter.warn(
                "Enhanced relation type cannot be 'root' if head is not 0",
                'Enhanced',
                testlevel=2,
                testid='enhanced-root-is-not-0',
                node_id=token_id_str,
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

        # Level 4+: Validate enhanced deprel against language-specific relations
        if self.level >= 4 and self.depreldata:  # noqa: PLR2004
            self._validate_language_specific_enhanced_deprel(token_id, deprel)

    def _validate_deps_structure(  # noqa: C901
        self,
        token_id: int | str,
        deps: list[tuple[str, int | str]],
    ) -> None:
        """Validate DEPS formatting: sorting by head and checking for duplicates.

        According to CoNLL-U format specification:
        - DEPS must be sorted by head index (numerically)
        - For same head, relations must be sorted alphabetically
        - No duplicate head:deprel pairs

        Arguments:
            token_id: ID of the token being validated
            deps: List of (deprel, head) tuples from parsed DEPS

        """
        if not deps or len(deps) < 2:  # noqa: PLR2004
            # Nothing to validate if there are 0 or 1 dependencies
            return

        # Convert heads to comparable numeric values for sorting check
        # The conllu library parses empty node IDs like "1.1" as tuples (1, '.', 1).
        def head_to_float(head: int | str | tuple[int, str, int]) -> float:
            """Convert head to float for comparison."""
            if isinstance(head, tuple):
                try:
                    return float(f'{head[0]}.{head[2]}')
                except (ValueError, TypeError, IndexError):
                    return 0.0
            try:
                return float(head)
            except (ValueError, TypeError):
                return 0.0

        def head_to_str(head: int | str | tuple[int, str, int]) -> str:
            """Convert head to string for display."""
            return f'{head[0]}.{head[2]}' if isinstance(head, tuple) else str(head)

        heads = [head_to_float(head) for deprel, head in deps]

        # Check if heads are sorted
        if heads != sorted(heads):
            deps_str = '|'.join(f'{head_to_str(head)}:{deprel}' for deprel, head in deps)
            self.reporter.warn(
                f"DEPS not sorted by head index: '{deps_str}'",
                'Format',
                testlevel=2,
                testid='unsorted-deps',
                node_id=str(token_id),
            )
            return

        # Check that relations for same head are sorted and no duplicates
        last_head_float: float | None = None
        last_deprel: str | None = None

        for deprel, head in deps:
            head_float = head_to_float(head)

            if head_float == last_head_float and last_deprel is not None:
                # Same head - check deprel sorting
                if deprel < last_deprel:
                    deps_str = '|'.join(f'{head_to_str(h)}:{d}' for d, h in deps)
                    self.reporter.warn(
                        f"DEPS pointing to head '{head_to_str(head)}' not sorted by relation type: '{deps_str}'",
                        'Format',
                        testlevel=2,
                        testid='unsorted-deps-2',
                        node_id=str(token_id),
                    )
                    return

                # Check for duplicates
                if deprel == last_deprel:
                    self.reporter.warn(
                        f"DEPS contain multiple instances of the same relation '{head_to_str(head)}:{deprel}'",
                        'Format',
                        testlevel=2,
                        testid='repeated-deps',
                        node_id=str(token_id),
                    )

            last_head_float = head_float
            last_deprel = deprel

    def _validate_language_specific_enhanced_deprel(
        self,
        token_id: int | str | tuple[int, str, int],
        deprel: str,
    ) -> None:
        """Validate enhanced DEPREL against language-specific data at Level 4+.

        Args:
            token_id: The token ID being validated
            deprel: The full enhanced DEPREL string (may include subtypes and case info)

        Note:
            For enhanced dependencies, we need to get the language from the token.
            Since we don't have direct access to the token here, we use self.lang.
            Code-switching support would require passing the token object.

        """
        lang = self.lang

        # Check if we have data for this language
        if lang not in self.depreldata:
            # No language-specific data available, skip validation
            return

        lang_deprels = self.depreldata[lang]

        # Check if the full deprel (with subtypes) exists in the language data
        if deprel in lang_deprels:
            # Exact match found - check if permitted
            deprel_info = lang_deprels[deprel]
            permitted = deprel_info.get('permitted', 1)

            if permitted == 0:
                # Relation exists but is not permitted for this language
                deprel_type = deprel_info.get('type', 'unknown')
                self.reporter.warn(
                    f"Enhanced DEPREL '{deprel}' is not permitted for language '{lang}' (type: {deprel_type})",
                    'Enhanced',
                    testlevel=4,
                    testid='unpermitted-edeprel',
                    node_id=str(token_id),
                )
            return

        # Special case: 'ref' is only allowed in enhanced dependencies
        deprel_base_parts = deprel.split(':')
        if deprel_base_parts[0] == 'ref':
            return

        # Not found - check if base relation exists
        base_deprel = deprel_base_parts[0]
        if base_deprel in lang_deprels:
            # Base exists but full relation doesn't
            self.reporter.warn(
                f"Unknown enhanced DEPREL subtype for language '{lang}': '{deprel}' (base '{base_deprel}' is valid)",
                'Enhanced',
                testlevel=4,
                testid='unknown-edeprel-subtype',
                node_id=str(token_id),
            )
        else:
            # Completely unknown relation
            self.reporter.warn(
                f"Unknown enhanced DEPREL for language '{lang}': '{deprel}'",
                'Enhanced',
                testlevel=4,
                testid='unknown-edeprel-langspec',
                node_id=str(token_id),
            )
