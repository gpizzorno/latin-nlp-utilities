"""Convert from and to UPOS."""

from __future__ import annotations

from nlp_utilities.constants import DALME_TAGS, UPOS_TO_PERSEUS


def upos_to_perseus(upos_tag: str) -> str:
    """Convert a UPOS tag to a Perseus XPOS tag."""
    return UPOS_TO_PERSEUS.get(upos_tag, '-')  # Return '-' for unknown tags


def dalme_to_upos(dalmepos_tag: str) -> str:
    """Convert a DALME POS tag to a Universal POS tag."""
    return DALME_TAGS.get(dalmepos_tag, 'X')  # Return 'X' for unknown tags
