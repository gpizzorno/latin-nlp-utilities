"""Character constraint validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import regex as re

from nlp_utilities.constants import ENHANCED_DEPREL_MATCHER, INVALID_DEPREL_MATCHER

from .helpers import is_empty_node
from .validation_mixin import BaseValidationMixin

if TYPE_CHECKING:
    import conllu


class CharacterValidationMixin(BaseValidationMixin):
    """Mixin providing character constraint validation methods."""

    def _validate_character_constraints(self, sentence: conllu.TokenList) -> None:
        """Validate character constraints for UPOS, DEPREL, and other fields.

        Arguments:
            sentence: Parsed sentence

        """
        # Pattern for enhanced DEPREL with Unicode support
        # Allows ASCII lowercase base, optional subtypes, and Unicode prepositions
        edeprel_re = re.compile(ENHANCED_DEPREL_MATCHER, re.UNICODE)

        for token in sentence:
            token_id = token['id']

            # Skip multiword tokens for most validations
            if isinstance(token_id, tuple):
                continue

            self._validate_upos_format(token)
            self._validate_deprel_format(token)
            self._validate_deps_format(token, edeprel_re)

    def _validate_upos_format(self, token: conllu.Token) -> None:
        """Validate UPOS character format.

        Arguments:
            token: Token to validate

        """
        upos = token.get('upos')
        if not upos:
            return

        token_id = token['id']
        is_valid_upos = re.match(r'^[A-Z]+$', upos) is not None
        is_empty_with_underscore = is_empty_node(token_id) and upos == '_'

        if not (is_valid_upos or is_empty_with_underscore):
            self.reporter.warn(
                f"Invalid UPOS value '{upos}'.",
                'Morpho',
                testlevel=2,
                testid='invalid-upos',
                node_id=str(token_id),
            )

    def _validate_deprel_format(self, token: conllu.Token) -> None:
        """Validate DEPREL character format.

        Arguments:
            token: Token to validate

        """
        deprel = token.get('deprel')
        if not deprel:
            return

        token_id = token['id']
        is_valid_deprel = re.match(INVALID_DEPREL_MATCHER, deprel) is not None
        is_empty_with_underscore = is_empty_node(token_id) and deprel == '_'

        if not (is_valid_deprel or is_empty_with_underscore):
            self.reporter.warn(
                f"Invalid DEPREL value '{deprel}'.",
                'Syntax',
                testlevel=2,
                testid='invalid-deprel',
                node_id=str(token_id),
            )

    def _validate_deps_format(self, token: conllu.Token, edeprel_re: re.Pattern) -> None:
        """Validate DEPS (enhanced dependencies) character format.

        Arguments:
            token: Token to validate
            edeprel_re: Compiled regex for enhanced DEPREL validation

        """
        deps = token.get('deps')
        if not deps or deps == '_':
            return

        # DEPS should already be parsed by conllu library
        # Check each enhanced relation in the list
        if not isinstance(deps, list):
            return

        token_id = token['id']
        for dep_tuple in deps:
            # conllu library parses DEPS as (deprel, head) tuples
            edeprel = dep_tuple[0]
            if not edeprel_re.match(edeprel):
                self.reporter.warn(
                    f"Invalid enhanced relation type in DEPS: '{edeprel}'.",
                    'Enhanced',
                    testlevel=2,
                    testid='invalid-edeprel',
                    node_id=str(token_id),
                )
