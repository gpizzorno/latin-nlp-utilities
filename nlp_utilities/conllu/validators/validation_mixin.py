"""Base class for validation mixins."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import regex as re

from .helpers import TreeHelperMixin

if TYPE_CHECKING:
    import conllu

    from .error_reporter import ErrorReporter


class BaseValidationMixin(TreeHelperMixin):
    """Base class for validation mixins.

    This mixin expects to be used with a class that provides:
    - self.reporter: ErrorReporter instance
    - self.level: int (validation level)
    - self.spaceafterno_in_effect: bool
    - self.upos_tags: set[str]
    - self.current_sentence: conllu.TokenList
    """

    # Type hints for attributes from ConlluValidator
    reporter: ErrorReporter
    level: int
    spaceafterno_in_effect: bool
    upos_tags: set[str]
    current_sentence: conllu.TokenList
    tokens_w_space: list[re.Pattern]
    lang: str
    featdata: dict[str, Any]
    depreldata: dict[str, Any]
    auxdata: dict[str, Any]
    universal_deprels: set[str]

    # placeholder methods
    def _validate_feature_values(self, token: conllu.Token) -> None:
        """Validate feature values (placeholder)."""
