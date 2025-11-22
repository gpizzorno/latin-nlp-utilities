"""Validation utilities for Latin language."""

from __future__ import annotations

from typing import Any

from .constants import VALIDITY_BY_POS
from .converters.features import feature_string_to_dict
from .converters.upos import upos_to_perseus


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
