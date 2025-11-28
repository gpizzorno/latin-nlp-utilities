"""SentencePattern class for matching token patterns in sentences."""

from __future__ import annotations

import uuid

import conllu

from .result import MatchResult
from .token import TokenPattern


class SentencePattern:
    """Represents a sequence of TokenPattern to match in a sentence as a whole.

    Attributes:
        name (str): The name of the SentencePattern.
        pattern (list[TokenPattern]): The list of TokenPatterns to match in sequence.

    """

    def __init__(self, pattern: list[TokenPattern], name: str | None = None) -> None:
        """Initialize the SentencePattern."""
        if not pattern:
            msg = 'SentencePattern requires a pattern.'
            raise ValueError(msg)

        if not isinstance(pattern, list) or not all(isinstance(p, TokenPattern) for p in pattern):
            msg = 'Pattern must be a list of TokenPattern instances.'
            raise ValueError(msg)

        self.name: str = name if name is not None else str(uuid.uuid4())
        self.pattern: list[TokenPattern] = pattern
        self.current_index: int = 0
        self.current_check: TokenPattern | None = None
        self.previous_check: TokenPattern | None = None
        self.matched_tokens: list[conllu.Token] = []

    def reset(self) -> None:
        """Reset the matching state."""
        self.current_index = 0
        self.current_check = None
        self.previous_check = None
        self.matched_tokens = []
        for pattern in self.pattern:
            if pattern.match_multiple:
                pattern.count = 0

    def match(self, sentence: conllu.TokenList) -> list[MatchResult]:
        """Match the pattern in the given sentence.

        Uses a backtracking algorithm: when a partial match fails, the algorithm
        retries from the position after where the failed match started, ensuring
        all possible matches are found.
        """
        matches = []
        tokens = list(sentence)
        start_pos = 0

        while start_pos < len(tokens):
            self.reset()
            pattern_idx = 0
            pos = start_pos

            while pos < len(tokens) and pattern_idx < len(self.pattern):
                token = tokens[pos]
                current_pattern = self.pattern[pattern_idx]

                if current_pattern.test(token):
                    self.matched_tokens.append(token)
                    pattern_idx += 1
                    pos += 1
                elif pattern_idx > 0 and self.pattern[pattern_idx - 1].match_multiple:
                    # Check if previous pattern (with match_multiple) can consume this token
                    if self.pattern[pattern_idx - 1].test(token):
                        self.matched_tokens.append(token)
                        pos += 1
                        continue
                    # Previous pattern can't match either, break and try next start position
                    break
                else:
                    # No match - break and try next starting position
                    break

            if pattern_idx >= len(self.pattern):
                # Complete match found
                matches.append(
                    MatchResult(
                        pattern_name=self.name,
                        sentence_id=sentence.metadata.get('sent_id', 'unknown'),
                        tokens=self.matched_tokens.copy(),
                    ),
                )
                # Move start position past the matched tokens to avoid overlapping matches
                start_pos = pos
            else:
                # No match starting from start_pos, try next position
                start_pos += 1

        self.reset()
        return matches

    def explain(self) -> str:
        """Provide a string explanation of the SentencePattern."""
        tp_explanations = [tp.explain() for tp in self.pattern]
        exp = 'This pattern matches a sequence of the following token patterns:\n'
        for i, explanation in enumerate(tp_explanations):
            exp += f'  Token Pattern {i + 1}: {explanation}\n'
        return exp

    def __repr__(self) -> str:
        """Return a string representation of the SentencePattern."""
        pattern_str = ', '.join(repr(pattern) for pattern in self.pattern)
        return f"SentencePattern(name='{self.name}', pattern=[{pattern_str}])"

    def __str__(self) -> str:
        """Return a string description of the SentencePattern."""
        return self.__repr__()
