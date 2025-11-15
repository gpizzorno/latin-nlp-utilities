"""Normalization utilities for Latin language."""

from __future__ import annotations

from typing import Any

from nlp_utilities.constants import VALIDITY_BY_POS
from nlp_utilities.converters.features import feature_string_to_dict
from nlp_utilities.converters.upos import upos_to_perseus


def normalize_features(
    upos: str | None,
    features: str | dict[str, Any],
    feature_set: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Normalize features based on UPOS and a feature set.

    Arguments:
        upos: The Universal Part of Speech tag.
        features: A feature string or dictionary of features.
        feature_set: A feature set dictionary defining valid features.

    Returns:
        A normalized feature dictionary or None.

    """
    if upos is None or feature_set is None:
        msg = 'Must pass UPOS, FEATS, and a Feature set'
        raise ValueError(msg)

    if isinstance(features, str):
        features = feature_string_to_dict(features)

    if features:
        output = {}

        for attr, value in features.items():
            # normalize attr label: capitalize first letter
            attr = attr.capitalize()  # noqa: PLW2901
            # check if attr is in feature set and value is valid for UPOS
            if attr in feature_set:
                record = feature_set[attr]
                if upos in record['byupos'] and value in record['byupos'][upos] and record['byupos'][upos][value] != 0:
                    output[attr] = value

        return output

    return features


def normalize_xpos(upos: str, xpos: str) -> str:
    """Normalize XPOS based on UPOS.

    Arguments:
        upos: The Universal Part of Speech tag.
        xpos: The language-specific Part of Speech tag.

    Returns:
        A normalized XPOS string.

    """
    if not upos or not xpos:
        msg = 'Must pass both UPOS and XPOS'
        raise ValueError(msg)

    upos_tag = upos_to_perseus(upos)
    new_xpos = ''
    for i, val in enumerate(xpos[1:], start=2):
        new_xpos = new_xpos + val if upos_tag in VALIDITY_BY_POS.get(i, '') else new_xpos + '-'

    # ensure lowercase
    new_xpos = new_xpos.lower()
    # ensure correct length
    new_xpos = new_xpos + '-' * (8 - len(new_xpos))

    return f'{upos_tag}{new_xpos}'
