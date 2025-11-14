"""Modular evaluator for CoNLL-U format evaluation."""

from .base import Score
from .evaluator import ConlluEvaluator

__all__ = ['ConlluEvaluator', 'Score']
