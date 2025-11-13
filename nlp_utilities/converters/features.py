"""Feature string and dictionary conversion utilities."""

from __future__ import annotations

from collections import OrderedDict
from typing import Any


def feature_string_to_dict(feat_string: str | None) -> dict[str, str]:
    """Convert a feature string to a dictionary."""
    if not feat_string or feat_string == '_':
        return {}

    f_pairs = [i.strip().split('=') for i in feat_string.strip().split('|')]
    return {i[0].strip(): i[1].strip() for i in f_pairs}


def feature_dict_to_string(feat_dict: dict[str, Any] | None) -> str:
    """Convert a feature dictionary to a string."""
    if not feat_dict:
        return '_'

    sorted_features = OrderedDict(sorted(feat_dict.items(), key=lambda x: x[0].lower()))
    return '|'.join([f'{k}={v}' for k, v in sorted_features.items()])
