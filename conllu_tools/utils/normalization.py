"""Normalization utilities."""

from __future__ import annotations

from typing import Any

from conllu_tools.utils.features import feature_string_to_dict, features_to_xpos, xpos_to_features
from conllu_tools.utils.xpos import format_xpos

from .features import validate_features
from .xpos import validate_xpos


def normalize_morphology(
    upos: str,
    xpos: str,
    feats: dict[str, str] | str,
    feature_set: dict[str, Any],
    ref_features: dict[str, str] | str | None = None,
) -> tuple[str, dict[str, str]]:
    """Normalize morphological information.

    Takes UPOS, XPOS, and FEATS, normalizes and validates them against
    a provided feature set, and reconciles with reference features if provided.

    Arguments:
        upos: The Universal Part of Speech tag.
        xpos: The language-specific Part of Speech tag.
        feats: A string or dictionary of features.
        feature_set: A feature set dictionary defining valid features.
        ref_features: A reference feature string or dictionary to reconcile with (optional).

    Returns:
        A tuple containing the normalized XPOS string and validated feature dictionary.

    """
    # normalize xpos format if needed
    xpos = format_xpos(upos, xpos, feats)
    # validate xpos against upos
    xpos = validate_xpos(upos, xpos)
    # set default for feats if None and ensure it is a dict
    feats = feature_string_to_dict(feats) if isinstance(feats, str) else feats if feats is not None else {}

    if ref_features is not None and isinstance(ref_features, str):
        ref_features = feature_string_to_dict(ref_features)

    # reconcile feats with reference features if provided
    # feats take precedence over ref_features, but we fill in
    # missing keys from ref_features
    if ref_features is not None:
        for key, value in ref_features.items():
            if key not in feats:
                feats[key] = value

    # use feature_set to validate against upos
    feats = validate_features(upos, feats, feature_set)

    # generate an xpos set from the validated features
    xpos_from_feats = features_to_xpos(feats)
    # validate generated xpos against upos
    xpos_from_feats = validate_xpos(upos, xpos_from_feats)

    # reconcile two sets of xpos
    # the provided xpos takes precedence over generated xpos
    # but we fill in missing slots
    for i in range(9):
        if xpos[i] == '-':
            xpos = xpos[:i] + xpos_from_feats[i] + xpos[i + 1 :]

    # generate a feature set from the final xpos
    feats_from_xpos = xpos_to_features(xpos)
    # validate generated features against upos + feature_set
    feats_from_xpos = validate_features(upos, feats_from_xpos, feature_set)
    # reconcile two sets of features
    for key, value in feats_from_xpos.items():
        if key not in feats:
            feats[key] = value

    return xpos, feats
