"""XPOS validation."""

from __future__ import annotations

from conllu_tools.constants import VALIDITY_BY_POS
from conllu_tools.utils.upos import upos_to_perseus


def validate_xpos(upos: str, xpos: str | None) -> str:
    """Ensure XPOS are valid for given UPOS.

    Arguments:
        upos: The Universal Part of Speech tag.
        xpos: The language-specific Part of Speech tag.

    Returns:
        A validated XPOS string.

    """
    if upos is None:
        msg = 'UPOS must be provided to validate XPOS.'
        raise ValueError(msg)

    upos_code = upos_to_perseus(upos)

    if xpos is None or len(xpos) != 9:  # noqa: PLR2004
        return f'{upos_code}--------'

    xpos_list = list(xpos)
    for position, valid_pos in VALIDITY_BY_POS.items():
        char = xpos_list[position - 1]
        if char != '-' and upos_code not in valid_pos:
            xpos_list[position - 1] = '-'

    return ''.join(xpos_list)
