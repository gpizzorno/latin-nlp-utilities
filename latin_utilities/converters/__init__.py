"""Interface for converters."""

from .dalmepos_to_upos import dalmepos_to_upos
from .upos_to_perseus import upos_to_perseus

__all__ = [
    'dalmepos_to_upos',
    'upos_to_perseus',
]
