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
        """Validate Unicode normalization (NFC) for FORM and LEMMA fields.

        Note: The conllu library handles parsing of other columns, so we focus
        on validating the content fields (FORM and LEMMA) which may contain
        user-generated text with potential Unicode normalization issues.

        Arguments:
            sentence: Parsed sentence to validate

        """
        for token in sentence:
            # Check Unicode normalization for FORM
            if token['form']:
                self._validate_field_unicode(token, 'form', 'FORM')

            # Check Unicode normalization for LEMMA
            if token['lemma'] and token['lemma'] != '_':
                self._validate_field_unicode(token, 'lemma', 'LEMMA')

    def _validate_field_unicode(
        self,
        token: conllu.Token,
        field_key: str,
        field_name: str,
    ) -> None:
        """Validate Unicode normalization for a specific field.

        Arguments:
            token: Token to validate
            field_key: Key to access field in token dict (e.g., 'form', 'lemma')
            field_name: Display name for field (e.g., 'FORM', 'LEMMA')

        """
        field_value = token[field_key]
        normalized = unicodedata.normalize('NFC', field_value)

        if field_value != normalized:
            # Find the first character that differs
            first_diff_pos = -1
            input_char_name = ''
            normalized_char_name = ''

            for i, (input_char, norm_char) in enumerate(zip(field_value, normalized)):
                if input_char != norm_char:
                    first_diff_pos = i
                    try:
                        input_char_name = unicodedata.name(input_char)
                    except ValueError:
                        input_char_name = f'U+{ord(input_char):04X}'
                    try:
                        normalized_char_name = unicodedata.name(norm_char)
                    except ValueError:
                        normalized_char_name = f'U+{ord(norm_char):04X}'
                    break
            else:
                # Strings differ in length
                first_diff_pos = min(len(field_value), len(normalized))

            # Build detailed error message
            if first_diff_pos >= 0 and input_char_name and normalized_char_name:
                message = (
                    f'Unicode not normalized in {field_name}: '
                    f'character[{first_diff_pos}] is {input_char_name}, '
                    f'should be {normalized_char_name}'
                )
            else:
                message = f'Unicode not normalized in {field_name}: {field_value!r}'

            self.reporter.warn(
                message,
                'Unicode',
                testlevel=1,
                testid='unicode-normalization',
                node_id=str(token['id']),
            )
