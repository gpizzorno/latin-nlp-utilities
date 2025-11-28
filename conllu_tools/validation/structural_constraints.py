"""Structural constraints validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from conllu_tools.constants import LEFT_TO_RIGHT_RELATIONS, ORPHAN_ALLOWED_PARENTS

from .validation_mixin import BaseValidationMixin

if TYPE_CHECKING:
    import conllu


class StructuralConstraintsValidationMixin(BaseValidationMixin):
    """Mixin providing structural constraints validation methods."""

    def _validate_left_to_right_relations(self, token: conllu.Token) -> None:
        """Validate that certain relations go left-to-right.

        Certain UD relations must always go left-to-right: conj, fixed, flat,
        goeswith, and appos.

        Arguments:
            token: Token to validate

        """
        token_id = token['id']

        # Skip multiword tokens
        if isinstance(token_id, tuple):
            return

        deprel = token.get('deprel', '')
        if not deprel:
            return

        # Extract base relation (before colon)
        base_deprel = deprel.split(':')[0]

        # Check if this is a relation that must go left-to-right
        if base_deprel in LEFT_TO_RIGHT_RELATIONS:
            head = token.get('head')
            if head is None or head == 0:
                return

            # Check direction: token ID must be greater than head ID
            if isinstance(token_id, (int, float)) and token_id < head:
                self.reporter.warn(
                    f"Relation '{deprel}' must go left-to-right.",
                    'Syntax',
                    testlevel=3,
                    testid=f'right-to-left-{base_deprel}',
                    node_id=str(token_id),
                )

    def _validate_single_subject(self, token: conllu.Token) -> None:
        """Check that predicate has at most 2 subjects.

        Most predicates should have only 1 subject, but up to 2 are allowed
        for special cases (e.g., nonverbal predicates without copula).

        Arguments:
            token: Token to validate

        """
        token_id = token['id']

        # Skip multiword tokens
        if isinstance(token_id, tuple):
            return

        # Get all children with 'subj' in their deprel
        if not hasattr(self, 'current_sentence'):
            return

        sentence = self.current_sentence
        subjects = []

        for child_token in sentence:
            child_id = child_token['id']
            # Skip multiword tokens
            if isinstance(child_id, tuple):
                continue

            child_head = child_token.get('head')
            child_deprel = child_token.get('deprel', '')

            # Check if this child is attached to our token and has 'subj' in deprel
            if child_head == token_id and 'subj' in child_deprel:
                subjects.append(child_id)

        # Warn if more than 2 subjects
        if len(subjects) > 2:  # noqa: PLR2004
            self.reporter.warn(
                f'Node has more than one subject: {subjects!s}',
                'Syntax',
                testlevel=3,
                testid='too-many-subjects',
                node_id=str(token_id),
            )

    def _validate_orphan(self, token: conllu.Token) -> None:
        """Validate the orphan relation.

        The orphan relation is used to attach an unpromoted orphan to the promoted
        orphan in gapping constructions. The parent of orphan should typically be
        attached via conj, parataxis, root, or other clausal relations.

        Arguments:
            token: Token to validate

        """
        token_id = token['id']

        # Skip multiword tokens
        if isinstance(token_id, tuple):
            return

        deprel = token.get('deprel', '')
        if not deprel:
            return

        # Extract base relation (before colon)
        base_deprel = deprel.split(':')[0]

        if base_deprel == 'orphan':
            head = token.get('head')
            if head is None or head == 0:
                return

            # Find the parent token
            if not hasattr(self, 'current_sentence'):
                return

            sentence = self.current_sentence
            parent_token = None

            for sent_token in sentence:
                sent_id = sent_token['id']
                if sent_id == head:
                    parent_token = sent_token
                    break

            if parent_token is None:
                return

            parent_deprel = parent_token.get('deprel', '')
            parent_base_deprel = parent_deprel.split(':')[0]

            # Check if parent has an allowed relation
            if parent_base_deprel not in ORPHAN_ALLOWED_PARENTS:
                self.reporter.warn(
                    (
                        f"The parent of 'orphan' should normally be one of {ORPHAN_ALLOWED_PARENTS} "
                        f"but it is '{parent_base_deprel}'."
                    ),
                    'Syntax',
                    testlevel=3,
                    testid='orphan-parent',
                    node_id=str(token_id),
                )
