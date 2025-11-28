"""Feature string and dictionary conversion utilities."""

from __future__ import annotations

from collections import OrderedDict
from typing import Any

from conllu_tools.constants import FEATS_TO_XPOS, XPOS_TO_FEATS


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


def xpos_to_features(xpos: str) -> dict[str, str]:
    """Convert XPOS in Perseus format to features.

    Arguments:
        xpos: An XPOS string in Perseus format.

    Returns:
        A dictionary of features.

    """
    feats = {}
    for position, char in enumerate(xpos, start=1):
        if char != '-':
            key = (position, char)
            if key in XPOS_TO_FEATS:
                feat, value = XPOS_TO_FEATS[key]
                feats[feat] = value
    return feats


def validate_features(upos: str, feats: dict[str, str] | str, feature_set: dict[str, Any]) -> dict[str, str]:
    """Ensure features are valid for given UPOS based on feature set.

    Arguments:
        upos: The Universal Part of Speech tag.
        feats: A feature string or dictionary of features.
        feature_set: A feature set dictionary defining valid features.

    Returns:
        A validated feature dictionary.

    """
    if upos is None or feature_set is None:
        msg = 'UPOS and feature set must be provided to validate FEATS.'
        raise ValueError(msg)

    if feats is None:
        return {}

    # convert feats string to dict if necessary
    if isinstance(feats, str):
        feats = feature_string_to_dict(feats)

    attr_names = {i.lower(): i for i in feature_set}
    validated_feats = {}
    for attr, value in feats.items():
        # normalize attr label: capitalize first letter
        norm_attr = attr_names.get(attr.lower())
        if norm_attr is not None:
            record = feature_set[norm_attr]
            # normalize value
            value_names = []
            for key in ['uvalues', 'lvalues', 'evalues']:
                value_names.extend(record[key])
            values_dict = {i.lower(): i for i in value_names}
            norm_value = values_dict.get(value.lower())
            # check if value is valid for UPOS
            if (
                norm_value is not None
                and upos in record['byupos']
                and norm_value in record['byupos'][upos]
                and record['byupos'][upos][norm_value] != 0
            ):
                validated_feats[norm_attr] = norm_value

    return validated_feats
