"""Interface for the matching module."""

from .condition import Condition
from .result import MatchResult
from .sentence import SentencePattern
from .token import TokenPattern
from .utils import build_pattern, find_in_corpus

__all__ = [
    'Condition',
    'MatchResult',
    'SentencePattern',
    'TokenPattern',
    'build_pattern',
    'find_in_corpus',
]
