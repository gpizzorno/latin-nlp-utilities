"""Language specific content validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import regex as re

from .helpers import get_alt_language
from .validation_mixin import BaseValidationMixin

if TYPE_CHECKING:
    import conllu


class LanguageContentValidationMixin(BaseValidationMixin):
    """Mixin providing language specific content validation methods."""

    def _validate_language_specific_content(self, sentence: conllu.TokenList) -> None:
        """Validate language-specific content requirements.

        Arguments:
            sentence: Parsed sentence

        """
        # Validate auxiliary verbs and copulas
        if self.lang in self.auxdata:
            for token in sentence:
                # Skip multiword tokens
                if isinstance(token['id'], tuple):
                    continue

                # Check copula lemmas first (cop takes precedence over AUX)
                if token['deprel'] == 'cop' and token['lemma'] and token['lemma'] != '_':
                    self._validate_copula_lemma(token)
                # Check auxiliary verbs (only if not a copula)
                elif token['upos'] == 'AUX' and token['lemma'] and token['lemma'] != '_':
                    self._validate_auxiliary_lemma(token)

    def _validate_auxiliary_lemma(self, token: conllu.Token) -> None:
        """Validate auxiliary verb lemma.

        Arguments:
            token: Token to validate

        """
        # Check for alternative language
        lang = get_alt_language(token) or self.lang

        # Get auxiliary list for the language
        auxlist, _ = self._get_aux_cop_lists(lang)

        if not auxlist:
            # No auxiliaries documented for this language
            self.reporter.warn(
                (
                    f"'{token['lemma']}' is not an auxiliary verb in language [{lang}] "
                    '(there are no known approved auxiliaries in this language)'
                ),
                'Morpho',
                testlevel=5,
                testid='aux-lemma',
                node_id=str(token['id']),
            )
        elif token['lemma'] not in auxlist:
            # Lemma not in auxiliary list
            self.reporter.warn(
                f"'{token['lemma']}' is not an auxiliary verb in language [{lang}]",
                'Morpho',
                testlevel=5,
                testid='aux-lemma',
                node_id=str(token['id']),
            )

    def _validate_copula_lemma(self, token: conllu.Token) -> None:
        """Validate copula lemma.

        Arguments:
            token: Token to validate

        """
        # Check for alternative language
        lang = get_alt_language(token) or self.lang

        # Get copula list for the language
        _, coplist = self._get_aux_cop_lists(lang)

        if not coplist:
            # No copulas documented for this language
            self.reporter.warn(
                (
                    f"'{token['lemma']}' is not a copula in language [{lang}] "
                    '(there are no known approved copulas in this language)'
                ),
                'Syntax',
                testlevel=5,
                testid='cop-lemma',
                node_id=str(token['id']),
            )
        elif token['lemma'] not in coplist:
            # Lemma not in copula list
            self.reporter.warn(
                f"'{token['lemma']}' is not a copula in language [{lang}]",
                'Syntax',
                testlevel=5,
                testid='cop-lemma',
                node_id=str(token['id']),
            )

    def _get_aux_cop_lists(self, lang: str | None = None) -> tuple[list[str], list[str]]:
        """Get lists of auxiliary and copula lemmas for the specified language.

        Arguments:
            lang: Language code (defaults to self.lang)

        Returns:
            Tuple of (auxiliary lemmas, copula lemmas)

        """
        if lang is None:
            lang = self.lang

        lemmalist = self.auxdata.get(lang, {})
        auxlist = [
            lemma
            for lemma, data in lemmalist.items()
            if any(f['function'] != 'cop.PRON' for f in data.get('functions', []))
        ]
        coplist = [
            lemma
            for lemma, data in lemmalist.items()
            if any(re.match(r'^cop\.', f['function']) for f in data.get('functions', []))
        ]
        return auxlist, coplist
