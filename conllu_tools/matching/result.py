"""MatchResult class to store results of pattern matching."""

from __future__ import annotations

from dataclasses import dataclass

import conllu


@dataclass
class MatchResult:
    """A class to store match results.

    Attributes:
        pattern_name (str): The name of the matched pattern.
        sentence_id (str): The ID of the sentence where the match was found.
        tokens (list[conllu.Token]): The list of tokens that matched the pattern.

    """

    pattern_name: str
    sentence_id: str
    tokens: list[conllu.Token]

    @property
    def substring(self) -> str:
        """Return the matched substring."""
        return ' '.join(token['form'] for token in self.tokens)

    @property
    def lemmata(self) -> list[str]:
        """Return the lemmata of the matched tokens."""
        return [token['lemma'] for token in self.tokens]

    @property
    def forms(self) -> list[str]:
        """Return the forms of the matched tokens."""
        return [token['form'] for token in self.tokens]

    def __repr__(self) -> str:
        """Return a string representation of the MatchResult."""
        return (
            f"MatchResult(pattern_name='{self.pattern_name}', "
            f"sentence_id='{self.sentence_id}', "
            f"substring='{self.substring}', "
        )

    def __str__(self) -> str:
        """Return a string representation of the MatchResult."""
        return self.substring
