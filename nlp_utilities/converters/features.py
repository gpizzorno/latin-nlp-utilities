"""Feature string and dictionary conversion utilities."""

from __future__ import annotations

from collections import OrderedDict
from typing import Any

from nlp_utilities.constants import FEATS_TO_XPOS


def feature_string_to_dict(feat_string: str | None) -> dict[str, str]:
    """Convert a feature string to a dictionary.

    Arguments:
        feat_string: A feature string.

    Returns:
        A dictionary of features.

    """
    if not feat_string or feat_string == '_':
        return {}

    f_pairs = [i.strip().split('=') for i in feat_string.strip().split('|')]
    return {i[0].strip(): i[1].strip() for i in f_pairs}


def feature_dict_to_string(feat_dict: dict[str, Any] | None) -> str:
    """Convert a feature dictionary to a string.

    Arguments:
        feat_dict: A dictionary of features.

    Returns:
        A feature string.

    """
    if not feat_dict:
        return '_'

    sorted_features = OrderedDict(sorted(feat_dict.items(), key=lambda x: x[0].lower()))
    return '|'.join([f'{k}={v}' for k, v in sorted_features.items()])


def features_to_xpos(feats: dict[str, str] | str) -> str:
    """Convert features to XPOS in Perseus format.

    Arguments:
        feats: A feature string or dictionary of features.

    Returns:
        An XPOS string in Perseus format.

    """
    if isinstance(feats, str):
        feats = feature_string_to_dict(feats)

    xpos = ['-'] * 9
    for (feat, value), (position, char) in FEATS_TO_XPOS.items():
        if feats.get(feat) == value:
            xpos[position - 1] = char

    return ''.join(xpos)
