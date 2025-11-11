"""Language format validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import regex as re

from .validation_mixin import BaseValidationMixin

if TYPE_CHECKING:
    import conllu


class LanguageFormatValidationMixin(BaseValidationMixin):
    """Mixin providing language format validation methods."""

    def _validate_language_specific_format(self, sentence: conllu.TokenList) -> None:
        """Validate language-specific format requirements.

        Arguments:
            sentence: Parsed sentence

        """
        # Check features against language-specific requirements
        if self.lang in self.featdata:
            self._validate_all_feature_values(sentence)

        # Check DEPREL subtypes against language-specific requirements
        if self.lang in self.depreldata:
            self._validate_all_deprel_subtypes(sentence)

        # Check whitespace in FORM/LEMMA against language-specific exceptions
        self._validate_all_whitespace(sentence)

    def _validate_all_deprel_subtypes(self, sentence: conllu.TokenList) -> None:
        """Validate all DEPREL subtypes in a sentence.

        Arguments:
            sentence: Parsed sentence

        """
        for token in sentence:
            # Skip multiword tokens
            if isinstance(token['id'], tuple):
                continue

            if token['deprel']:
                self._validate_deprel_subtype(token)

    def _validate_all_whitespace(self, sentence: conllu.TokenList) -> None:
        """Validate whitespace in all tokens in a sentence.

        Arguments:
            sentence: Parsed sentence

        """
        for token in sentence:
            # Skip multiword tokens
            if isinstance(token['id'], tuple):
                continue

            self._validate_whitespace(token)

    def _validate_all_feature_values(self, sentence: conllu.TokenList) -> None:
        """Validate all feature values in a sentence.

        Arguments:
            sentence: Parsed sentence

        """
        for token in sentence:
            # Skip multiword tokens
            if isinstance(token['id'], tuple):
                continue

            if token['feats']:
                self._validate_feature_values(token)

    def _validate_deprel_subtype(self, token: conllu.Token) -> None:
        """Validate DEPREL subtype against language-specific data.

        Arguments:
            token: Token to validate

        """
        deprel = token['deprel']
        if not deprel or deprel == '_':
            return

        lang_deprels = self.depreldata.get(self.lang, {})
        if not lang_deprels:
            return

        # Check if this exact DEPREL (including subtype) is documented
        if deprel not in lang_deprels:
            # Extract base relation to provide helpful error message
            base_deprel = self._extract_base_deprel(deprel)

            # Check if it's a subtype issue (base exists but full deprel doesn't)
            if base_deprel != deprel and base_deprel in lang_deprels:
                self.reporter.warn(
                    f"Unknown DEPREL subtype: '{deprel}'. "
                    f"Base relation '{base_deprel}' exists but this subtype is not documented "
                    f'for language [{self.lang}].',
                    'Syntax',
                    testlevel=4,
                    testid='unknown-deprel-subtype',
                    node_id=str(token['id']),
                )
            else:
                # Neither base nor full relation is documented
                self.reporter.warn(
                    f"Unknown DEPREL label: '{deprel}'.",
                    'Syntax',
                    testlevel=4,
                    testid='unknown-deprel',
                    node_id=str(token['id']),
                )
            return

        # Check if the relation is permitted
        deprel_record = lang_deprels[deprel]
        if deprel_record.get('permitted', 0) == 0:
            self.reporter.warn(
                f"DEPREL '{deprel}' is not permitted in language [{self.lang}].",
                'Syntax',
                testlevel=4,
                testid='deprel-not-permitted',
                node_id=str(token['id']),
            )

    def _extract_base_deprel(self, deprel: str) -> str:
        """Extract base DEPREL without subtype.

        Arguments:
            deprel: Full DEPREL (e.g., "nmod:poss" or "advcl:pred")

        Returns:
            Base DEPREL (e.g., "nmod" or "advcl")

        """
        # Split on first colon to get base relation
        return deprel.split(':', 1)[0]

    def _validate_whitespace(self, token: conllu.Token) -> None:
        """Validate whitespace in FORM and LEMMA fields.

        Check if FORM or LEMMA contains whitespace. If so, validate against
        language-specific exceptions from tokens_w_space.ud file.

        Arguments:
            token: Token to validate

        """
        # Check FORM and LEMMA columns
        for col_name in ['form', 'lemma']:
            value = token[col_name]

            # Skip empty values
            if not value or value == '_':
                continue

            # Check if value contains whitespace
            if not self._contains_whitespace(value):
                continue

            # Check if value matches any exception patterns
            if not self._matches_whitespace_exception(value):
                col_display = col_name.upper()
                self.reporter.warn(
                    (
                        f"'{value}' in column {col_display} is not on the list of exceptions "
                        'allowed to contain whitespace (data/tokens_w_space.LANG files).'
                    ),
                    'Format',
                    testlevel=4,
                    testid='invalid-word-with-space',
                    node_id=str(token['id']),
                )

    def _contains_whitespace(self, value: str) -> bool:
        """Check if a string contains whitespace.

        Arguments:
            value: String to check

        Returns:
            True if value contains whitespace

        """
        return bool(re.search(r'\s', value, re.UNICODE))

    def _matches_whitespace_exception(self, value: str) -> bool:
        """Check if a value matches any whitespace exception pattern.

        Arguments:
            value: String to check against exception patterns

        Returns:
            True if value matches any exception pattern

        """
        return any(pattern.fullmatch(value) for pattern in self.tokens_w_space)
