"""Functions for converting between LLCT and Perseus XPOS tags."""

from __future__ import annotations

from nlp_utilities.converters.upos import upos_to_perseus


def llct_to_perseus(upos: str, xpos: str) -> str:
    """Format LLCT UPOS and XPOS as Perseus XPOS tag."""
    xpos_list = xpos.split('|')

    # ensure correct PoS tag
    xpos_list[0] = upos_to_perseus(upos)
    return ''.join(xpos_list)
