"""Tree validation mixin."""

from __future__ import annotations

import conllu

from .base import UDError


class TreeValidationMixin:
    """Mixin providing tree validation methods."""

    # Type hints for attributes from UDEvaluator
    eval_deprels: bool

    def _validate_tree_structure(self, sentence: conllu.TokenList, sent_id: str = 'unknown') -> None:
        """Validate the dependency tree structure of a sentence.

        Arguments:
            sentence: CoNLL-U sentence to validate
            sent_id: Sentence ID for error messages

        Raises:
            UDError: If tree structure is invalid

        """
        if not self.eval_deprels:
            # Skip validation if not evaluating dependencies
            return

        # Get only words (not MWT ranges)
        words = [token for token in sentence if not isinstance(token['id'], tuple)]

        if not words:
            msg = f'Sentence {sent_id} has no words'
            raise UDError(msg)

        # Check that IDs are sequential starting from 1
        for i, token in enumerate(words, start=1):
            if token['id'] != i:
                msg = f'Sentence {sent_id}: Expected word ID {i}, got {token["id"]}'
                raise UDError(msg)

        # Validate HEAD values are in valid range
        num_words = len(words)
        for token in words:
            head = token['head']
            if head < 0 or head > num_words:
                msg = (
                    f"Sentence {sent_id}: HEAD {head} for word '{token['form']}' "
                    f'(id={token["id"]}) is out of range [0, {num_words}]'
                )
                raise UDError(msg)

        # Check for exactly one root
        roots = [token for token in words if token['head'] == 0]
        if len(roots) == 0:
            msg = f'Sentence {sent_id}: No root node found'
            raise UDError(msg)
        if len(roots) > 1:
            root_forms = [token['form'] for token in roots]
            msg = f'Sentence {sent_id}: Multiple roots found: {root_forms}'
            raise UDError(msg)

        # Detect cycles by attempting to build tree with conllu's to_tree()
        # This will raise ParseException if there's a cycle or other structural issue
        try:
            sentence.to_tree()
        except conllu.exceptions.ParseException as e:
            msg = f'Sentence {sent_id}: Invalid tree structure - {e}'
            raise UDError(msg) from e
