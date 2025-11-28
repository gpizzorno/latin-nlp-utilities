"""Base classes for CoNLL-U evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import conllu


class UDError(Exception):
    """Raised when there is an error in the UD data or evaluation process."""


@dataclass(frozen=True)
class UDSpan:
    """Represents a span (start and end position) in the character array."""

    start: int
    end: int  # Note: end marks the first position AFTER the end


@dataclass
class UDWord:
    """Represents a word with its span and CoNLL-U token."""

    span: UDSpan
    token: conllu.Token
    is_multiword: bool  # True if this word is part of a multi-word token
    enhanced_deps: list[tuple[int | UDWord, list[str]]] | None = None  # Processed enhanced dependencies
    functional_children: list[UDWord] | None = None  # List of functional children for MLAS

    def __hash__(self) -> int:
        """Make UDWord hashable for use in dictionaries."""
        return hash((self.span, id(self.token), self.is_multiword))


@dataclass
class AlignmentWord:
    """Represents an aligned pair of gold and system words."""

    gold_word: UDWord
    system_word: UDWord


class Alignment:
    """Represents the alignment between gold and system words."""

    def __init__(self, gold_words: list[UDWord], system_words: list[UDWord]) -> None:
        """Initialize alignment.

        Args:
            gold_words: List of gold words
            system_words: List of system words

        """
        self.gold_words = gold_words
        self.system_words = system_words
        self.matched_words: list[AlignmentWord] = []
        self.matched_words_map: dict[UDWord, UDWord] = {}

    def append_aligned_words(self, gold_word: UDWord, system_word: UDWord) -> None:
        """Add an aligned word pair.

        Args:
            gold_word: Gold word
            system_word: System word

        """
        self.matched_words.append(AlignmentWord(gold_word, system_word))
        self.matched_words_map[system_word] = gold_word


@dataclass
class Score:
    """Represents evaluation scores for a particular metric."""

    gold_total: int | None
    system_total: int | None
    correct: int | None
    aligned_total: int | None = None

    @property
    def precision(self) -> float:
        """Calculate precision."""
        if self.system_total and self.system_total > 0:
            return self.correct / self.system_total if self.correct is not None else 0.0
        return 0.0

    @property
    def recall(self) -> float:
        """Calculate recall."""
        if self.gold_total and self.gold_total > 0:
            return self.correct / self.gold_total if self.correct is not None else 0.0
        return 0.0

    @property
    def f1(self) -> float:
        """Calculate F1 score."""
        if self.system_total and self.gold_total and self.correct is not None:
            total = self.system_total + self.gold_total
            if total > 0:
                return 2 * self.correct / total
        return 0.0

    @property
    def aligned_accuracy(self) -> float | None:
        """Calculate aligned accuracy."""
        if self.aligned_total and self.aligned_total > 0 and self.correct is not None:
            return self.correct / self.aligned_total
        return None
