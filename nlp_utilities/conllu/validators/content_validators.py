"""Content validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .functional_leaves import FunctionalLeavesValidationMixin
from .spans import SpansValidationMixin
from .structural_constraints import StructuralConstraintsValidationMixin
from .upos_deprel_compatibility import UposDeprelValidationMixin

if TYPE_CHECKING:
    import conllu


class ContentValidationMixin(
    FunctionalLeavesValidationMixin,
    SpansValidationMixin,
    UposDeprelValidationMixin,
    StructuralConstraintsValidationMixin,
):
    """Mixin providing content validation methods."""

    def _validate_content(self, sentence: conllu.TokenList) -> None:
        """Validate annotation content.

        Arguments:
            sentence: Parsed sentence

        """
        # Store sentence for child relation checking
        self.current_sentence = sentence

        for token in sentence:
            # Validate UPOS vs DEPREL compatibility
            if token['deprel'] and token['upos']:
                self._validate_upos_deprel_compatibility(token)

            # Validate structural constraints
            self._validate_left_to_right_relations(token)
            self._validate_single_subject(token)
            self._validate_orphan(token)

            # Validate span constraints
            self._validate_goeswith_span(token)
            self._validate_fixed_span(token)
            self._validate_projective_punctuation(token)

            # Validate functional leaves
            self._validate_functional_leaves(token)
