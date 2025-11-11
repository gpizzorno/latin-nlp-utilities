"""Modular evaluator for CoNLL-U format evaluation."""

from .base import Score
from .evaluator import UDEvaluator

__all__ = ['Score', 'UDEvaluator']
