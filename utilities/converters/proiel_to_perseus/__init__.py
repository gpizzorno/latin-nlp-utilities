"""Interface for the proiel_to_perseus converters."""

from .proiel_converters import (
    to_case,
    to_degree,
    to_gender,
    to_mood,
    to_number,
    to_tense,
    to_voice,
)

__all__ = [
    'to_case',
    'to_degree',
    'to_gender',
    'to_mood',
    'to_number',
    'to_tense',
    'to_voice',
]
