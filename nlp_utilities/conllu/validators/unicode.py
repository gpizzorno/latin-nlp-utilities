"""Unicode validation methods."""

from __future__ import annotations

import unicodedata
from typing import TYPE_CHECKING

from .validation_mixin import BaseValidationMixin

if TYPE_CHECKING:
    import conllu


class UnicodeValidationMixin(BaseValidationMixin):
    """Mixin providing Unicode validation methods."""

    def _validate_unicode(self, sentence: conllu.TokenList) -> None:
        """Validate basic CoNLL-U format.

        Validates:
        - Unicode normalization in FORM and LEMMA

        Arguments:
            sentence: Parsed sentence to validate

        """
        for token in sentence:
            # Check Unicode normalization for FORM
            form_normalized = unicodedata.normalize('NFC', token['form'])
            if token['form'] != form_normalized:
                self.reporter.warn(
                    f'Unicode not normalized in FORM: {token["form"]!r}',
                    'Unicode',
                    testlevel=1,
                    testid='unicode-normalization',
                    node_id=str(token['id']),
                )

            # Check Unicode normalization for LEMMA
            if token['lemma'] and token['lemma'] != '_':
                lemma_normalized = unicodedata.normalize('NFC', token['lemma'])
                if token['lemma'] != lemma_normalized:
                    self.reporter.warn(
                        f'Unicode not normalized in LEMMA: {token["lemma"]!r}',
                        'Unicode',
                        testlevel=1,
                        testid='unicode-normalization',
                        node_id=str(token['id']),
                    )
