"""Spans validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .validation_mixin import BaseValidationMixin

if TYPE_CHECKING:
    import conllu


class SpansValidationMixin(BaseValidationMixin):
    """Mixin providing spans validation methods."""

    def _validate_goeswith_span(self, token: conllu.Token) -> None:
        """Validate goeswith span is contiguous.

        The 'goeswith' relation connects word parts separated by whitespace
        that should be one word. We check that nodes form a contiguous chain
        without gaps, and that they are separated by whitespace.

        Arguments:
            token: Token to validate (checking its goeswith children)

        """
        token_id = token['id']

        # Skip multiword tokens
        if isinstance(token_id, tuple):
            return

        # Get children with goeswith relation
        goeswith_children = self._get_goeswith_children(token_id)

        if not goeswith_children:
            return

        # Check contiguity
        self._check_goeswith_contiguity(token_id, goeswith_children)

        # Check whitespace separation
        self._check_goeswith_spacing(token_id, goeswith_children)

    def _get_goeswith_children(self, token_id: int) -> list[int]:
        """Get list of children with goeswith relation.

        Arguments:
            token_id: Parent token ID

        Returns:
            Sorted list of child IDs with goeswith relation

        """
        goeswith_children = []

        for child_token in self.current_sentence:
            child_id = child_token['id']
            # Skip multiword tokens
            if isinstance(child_id, tuple):
                continue

            if child_token.get('head') == token_id:
                child_deprel = child_token.get('deprel', '').split(':')[0]
                if child_deprel == 'goeswith':
                    goeswith_children.append(child_id)

        return sorted(goeswith_children)

    def _check_goeswith_contiguity(self, token_id: int, goeswith_children: list[int]) -> None:
        """Check that goeswith group forms a contiguous span.

        Arguments:
            token_id: Parent token ID
            goeswith_children: Sorted list of child IDs

        """
        # Create list of all nodes in the goeswith group (head + children)
        goeswith_list = sorted([token_id, *goeswith_children])

        # Expected range: all IDs from head to last child
        expected_range = list(range(token_id, goeswith_children[-1] + 1))

        # Check if the goeswith group is contiguous
        if goeswith_list != expected_range:
            self.reporter.warn(
                f'Violation of guidelines: gaps in goeswith group {goeswith_list!s} != {expected_range!s}.',
                'Syntax',
                testlevel=3,
                testid='goeswith-gap',
                node_id=str(token_id),
            )

    def _check_goeswith_spacing(self, token_id: int, goeswith_children: list[int]) -> None:
        """Check that goeswith nodes are separated by whitespace.

        Arguments:
            token_id: Parent token ID
            goeswith_children: Sorted list of child IDs

        """
        # Create list of all nodes in the goeswith group (head + children)
        goeswith_list = sorted([token_id, *goeswith_children])

        # Check that non-last nodes in the chain have a space after them
        for node_id in goeswith_list[:-1]:
            # Find the token with this ID
            for t in self.current_sentence:
                if t['id'] == node_id:
                    misc = t.get('misc')
                    if misc and misc.get('SpaceAfter') == 'No':
                        self.reporter.warn(
                            "'goeswith' cannot connect nodes that are not separated by whitespace",
                            'Syntax',
                            testlevel=3,
                            testid='goeswith-nospace',
                            node_id=str(token_id),
                        )
                    break

    def _validate_fixed_span(self, token: conllu.Token) -> None:
        """Validate fixed span is mostly contiguous.

        Fixed expressions should not skip words that are not part of the
        expression, except for intervening punctuation.

        Arguments:
            token: Token to validate (checking its fixed children)

        """
        token_id = token['id']

        # Skip multiword tokens
        if isinstance(token_id, tuple):
            return

        # Get children with fixed relation
        fixed_children = self._get_fixed_children(token_id)

        if not fixed_children:
            return

        # Check for non-punctuation gaps in the fixed expression
        self._check_fixed_gaps(token_id, fixed_children)

    def _get_fixed_children(self, token_id: int) -> list[int]:
        """Get list of children with fixed relation.

        Arguments:
            token_id: Parent token ID

        Returns:
            Sorted list of child IDs with fixed relation

        """
        fixed_children = []

        for child_token in self.current_sentence:
            child_id = child_token['id']
            # Skip multiword tokens
            if isinstance(child_id, tuple):
                continue

            if child_token.get('head') == token_id:
                child_deprel = child_token.get('deprel', '').split(':')[0]
                if child_deprel == 'fixed':
                    fixed_children.append(child_id)

        return sorted(fixed_children)

    def _check_fixed_gaps(self, token_id: int, fixed_children: list[int]) -> None:
        """Check for gaps in fixed expression (excluding punctuation).

        Arguments:
            token_id: Parent token ID
            fixed_children: Sorted list of child IDs

        """
        # Create list of all nodes in the fixed expression (head + children)
        fixed_list = sorted([token_id, *fixed_children])

        # Expected range: all IDs from head to last child
        expected_range = list(range(token_id, fixed_children[-1] + 1))

        # Find nodes in the gap (nodes between head and last child not in fixed expression)
        gap_ids = set(expected_range) - set(fixed_list)

        # Filter out punctuation from gap (punctuation is allowed in fixed expressions)
        non_punct_gaps = self._filter_non_punct_gaps(gap_ids)

        if non_punct_gaps:
            self.reporter.warn(
                f'Gaps in fixed expression {fixed_list!s}',
                'Syntax',
                testlevel=3,
                testid='fixed-gap',
                node_id=str(token_id),
            )

    def _filter_non_punct_gaps(self, gap_ids: set[int]) -> list[int]:
        """Filter out punctuation nodes from gap IDs.

        Arguments:
            gap_ids: Set of gap node IDs

        Returns:
            List of non-punctuation gap IDs

        """
        non_punct_gaps = []
        for gap_id in gap_ids:
            for t in self.current_sentence:
                if t['id'] == gap_id:
                    deprel = t.get('deprel', '').split(':')[0]
                    if deprel != 'punct':
                        non_punct_gaps.append(gap_id)
                    break
        return non_punct_gaps

    def _validate_projective_punctuation(self, token: conllu.Token) -> None:
        """Validate punctuation attachment is projective.

        Punctuation should not cause non-projectivity or be attached
        non-projectively.

        Arguments:
            token: Token to validate

        """
        token_id = token['id']

        # Skip multiword tokens
        if isinstance(token_id, tuple):
            return

        deprel = token.get('deprel', '').split(':')[0]

        if deprel != 'punct':
            return

        # Check if punctuation causes non-projectivity in other nodes
        try:
            nonproj_nodes = self.get_caused_nonprojectivities(token_id, self.current_sentence)
            if nonproj_nodes:
                self.reporter.warn(
                    f'Punctuation must not cause non-projectivity of nodes {nonproj_nodes}',
                    'Syntax',
                    testlevel=3,
                    testid='punct-causes-nonproj',
                    node_id=str(token_id),
                )

            # Check if punctuation itself is attached non-projectively
            gap = self.get_gap(token_id, self.current_sentence)
            if gap:
                self.reporter.warn(
                    f'Punctuation must not be attached non-projectively over nodes {sorted(gap)}',
                    'Syntax',
                    testlevel=3,
                    testid='punct-is-nonproj',
                    node_id=str(token_id),
                )
        except conllu.exceptions.ParseException:
            # If tree building fails, skip projectivity checks
            # (errors will be caught elsewhere)
            pass
