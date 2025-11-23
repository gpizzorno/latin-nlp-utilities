"""Convert various XPOS formats to Perseus XPOS format."""

import regex as re

from nlp_utilities.constants import (
    ITTB_XPOS_MATCHER,
    LLCT_XPOS_MATCHER,
    PERSEUS_XPOS_MATCHER,
    PROIEL_XPOS_MATCHER,
)
from nlp_utilities.converters.features import feature_string_to_dict
from nlp_utilities.converters.upos import upos_to_perseus

from .ittb_converters import ittb_to_perseus
from .llct_converters import llct_to_perseus
from .proiel_converters import proiel_to_perseus


def format_xpos(upos: str, xpos: str | None, feats: dict[str, str] | str | None) -> str:
    """Convert morphology data in various formats to Perseus XPOS.

    Arguments:
        upos: The Universal Part of Speech tag.
        xpos: XPOS string formatted in almost styles (LLCT, ITTB, PROIEL, Perseus, DALME, etc).
        feats: A dictionary of features.

    Returns:
        A Perseus XPOS string.

    """
    if upos is None:
        msg = 'UPOS must be provided to format XPOS.'
        raise ValueError(msg)

    if not feats:
        feats = {}

    if isinstance(feats, str):
        feats = feature_string_to_dict(feats)

    if xpos is not None:
        if re.match(PERSEUS_XPOS_MATCHER, xpos):
            return f'{upos_to_perseus(upos)}{xpos[1:]}'  # ensure UPOS is correct
        if re.match(LLCT_XPOS_MATCHER, xpos):
            return llct_to_perseus(upos, xpos, feats)
        if re.match(ITTB_XPOS_MATCHER, xpos):
            return ittb_to_perseus(upos, xpos)
        if re.match(PROIEL_XPOS_MATCHER, xpos):
            return proiel_to_perseus(upos, feats)

    return f'{upos_to_perseus(upos)}--------'  # default fallback
