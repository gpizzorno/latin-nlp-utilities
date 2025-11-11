"""Functional leaves validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nlp_utilities.constants import FUNCTIONAL_LEAVES_RELATIONS, FUNCTIONAL_RELATION_CHILDREN

from .validation_mixin import BaseValidationMixin

if TYPE_CHECKING:
    import conllu


class FunctionalLeavesValidationMixin(BaseValidationMixin):
    """Mixin providing functional leaves validation methods."""

    def _validate_functional_leaves(self, token: conllu.Token) -> None:
        """Validate that functional words are leaves (with limited exceptions).

        Functional words (case, mark, cc, aux, cop, det, fixed, goeswith, punct)
        should generally not have dependents, with specific exceptions per relation.

        Arguments:
            token: Token to validate (checking its children)

        """
        token_id = token['id']

        # Skip multiword tokens
        if isinstance(token_id, tuple):
            return

        # Get base deprel (without subtypes)
        parent_deprel = token.get('deprel', '').split(':')[0]

        # Only check functional relations
        if parent_deprel not in FUNCTIONAL_LEAVES_RELATIONS:
            return

        # Check if parent has a gap (for punct exception)
        parent_has_gap = False
        try:
            gap = self.get_gap(token_id, self.current_sentence)
            parent_has_gap = bool(gap)
        except (conllu.exceptions.ParseException, AttributeError):
            pass

        # Check each child
        for child_token in self.current_sentence:
            child_id = child_token['id']

            # Skip multiword tokens
            if isinstance(child_id, tuple):
                continue

            # Check if this token is the parent
            if child_token.get('head') != token_id:
                continue

            child_deprel = child_token.get('deprel', '').split(':')[0]
            child_upos = child_token.get('upos', '')
            child_feats = child_token.get('feats', {}) or {}

            # Special exception: negation can modify any function word
            if self._is_negation(child_deprel, child_upos, child_feats) and parent_deprel != 'punct':
                continue

            # Special exception: punct can depend on parent with gap (nonprojective attachment)
            if parent_has_gap and child_deprel == 'punct':
                continue

            # Check relation-specific rules
            if not self._is_allowed_functional_child(parent_deprel, child_deprel):
                self._report_functional_leaf_violation(token, child_token, parent_deprel, child_deprel)

    def _is_negation(self, deprel: str, upos: str, feats: dict[str, str] | None) -> bool:
        """Check if a token is a negation modifier.

        Arguments:
            deprel: Dependency relation
            upos: UPOS tag
            feats: Features dictionary

        Returns:
            True if token is negation (advmod with PART/ADV and Polarity=Neg)

        """
        if deprel != 'advmod':
            return False
        if upos not in {'PART', 'ADV'}:
            return False
        # Check for Polarity=Neg in features
        if not feats:
            return False
        return feats.get('Polarity') == 'Neg'

    def _is_allowed_functional_child(self, parent_deprel: str, child_deprel: str) -> bool:
        """Check if a child relation is allowed for a functional parent.

        Arguments:
            parent_deprel: Parent's dependency relation
            child_deprel: Child's dependency relation

        Returns:
            True if child is allowed for this parent type

        """
        return child_deprel in FUNCTIONAL_RELATION_CHILDREN.get(parent_deprel, set())

    def _report_functional_leaf_violation(
        self,
        parent_token: conllu.Token,
        child_token: conllu.Token,
        parent_deprel: str,
        child_deprel: str,
    ) -> None:
        """Report a functional leaf violation.

        Arguments:
            parent_token: Parent token
            child_token: Child token
            parent_deprel: Parent's dependency relation
            child_deprel: Child's dependency relation

        """
        parent_id = parent_token['id']
        parent_form = parent_token.get('form', '_')
        child_id = child_token['id']
        child_form = child_token.get('form', '_')

        # Determine test ID based on parent relation
        if parent_deprel in {'mark', 'case'}:
            testid = 'leaf-mark-case'
        elif parent_deprel in {'aux', 'cop'}:
            testid = 'leaf-aux-cop'
        elif parent_deprel == 'cc':
            testid = 'leaf-cc'
        elif parent_deprel == 'fixed':
            testid = 'leaf-fixed'
        elif parent_deprel == 'goeswith':
            testid = 'leaf-goeswith'
        elif parent_deprel == 'punct':
            testid = 'leaf-punct'
        else:
            testid = 'leaf-functional'

        message = (
            f"'{parent_deprel}' not expected to have children "
            f'({parent_id}:{parent_form}:{parent_deprel} --> {child_id}:{child_form}:{child_deprel})'
        )

        self.reporter.warn(
            message,
            'Syntax',
            testlevel=3,
            testid=testid,
            node_id=str(parent_id),
        )
