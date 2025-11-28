"""MISC column validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from conllu_tools.constants import MISC_ATTRIBUTES

from .helpers import is_empty_node, is_word
from .validation_mixin import BaseValidationMixin

if TYPE_CHECKING:
    import conllu


class MiscValidationMixin(BaseValidationMixin):
    """Mixin providing MISC column validation methods."""

    def _validate_misc(self, sentence: conllu.TokenList) -> None:
        """Validate MISC column format and attributes.

        Arguments:
            sentence: Parsed sentence

        """
        for token in sentence:
            token_id = token['id']

            # Skip multiword tokens for MISC validation
            if isinstance(token_id, tuple):
                continue

            # Only validate word tokens and empty nodes
            if not (is_word(token_id) or is_empty_node(token_id)):
                continue

            misc = token.get('misc')
            if not misc or misc == '_':
                continue

            # conllu library parses MISC as a dict, but we need to check for duplicates
            # in the original string representation
            # Check if there are duplicate keys in known MISC attributes
            # Count occurrences of each known attribute
            attr_counts = {}
            for attr in MISC_ATTRIBUTES:
                if attr in misc:
                    attr_counts[attr] = 1

            # Note: The conllu library automatically handles duplicate detection
            # by overwriting duplicate keys in the dict, so we can't detect them
            # from the parsed structure.
            # Validate SpaceAfter value if present
            if 'SpaceAfter' in misc:
                space_after_value = misc['SpaceAfter']
                if space_after_value != 'No':
                    self.reporter.warn(
                        f"SpaceAfter attribute should have value 'No', got '{space_after_value}'.",
                        'Format',
                        testlevel=2,
                        testid='invalid-spaceafter-value',
                        node_id=str(token_id),
                    )
