"""Functions for converting between LLCT and Perseus XPOS tags."""

from __future__ import annotations

from conllu_tools.constants import LLCT_CONCORDANCES
from conllu_tools.utils.features import feature_string_to_dict
from conllu_tools.utils.upos import upos_to_perseus


def _validate_xpos_value(value: str | None, feats_type: str) -> str | None:
    """Validate LLCT XPOS value against concordance."""
    if value is None or value == '-':
        return None

    valid_values = LLCT_CONCORDANCES[feats_type].values()

    if value in valid_values:
        return value

    return None


def _reconcile_xpos_feats(xpos_value: str | None, feats_value: str | None, feats_type: str) -> str:
    """Reconcile LLCT XPOS and FEATS values."""
    # map FEATS value to XPOS value
    feats_value = LLCT_CONCORDANCES[feats_type].get(feats_value) if feats_value else None
    # validate both values
    xpos_value = _validate_xpos_value(xpos_value, feats_type)
    feats_value = _validate_xpos_value(feats_value, feats_type)

    # if neither value is valid, return '-'
    if not any([xpos_value, feats_value]):
        return '-'

    # if only one value is valid, return that value
    if xpos_value and not feats_value:
        return xpos_value
    if feats_value and not xpos_value:
        return feats_value

    # prefer XPOS value if both are valid
    return xpos_value if xpos_value else '-'


def llct_to_perseus(upos: str, xpos: str, feats: dict[str, str] | str) -> str:
    """Convert LLCT UPOS, XPOS, and FEATS to Perseus XPOS tag.

    Arguments:
        upos: The Universal Part of Speech tag.
        xpos: An LLCT XPOS string.
        feats: A feature string or dictionary of features.

    Returns:
        A Perseus XPOS string.

    """
    if not feats and '|' not in xpos:  # invalid punctuation xpos
        return f'{upos_to_perseus(upos)}--------'

    if isinstance(feats, str):
        feats = feature_string_to_dict(feats)

    parts = xpos.split('|')

    if len(parts) != 9:  # noqa: PLR2004
        # complete with dash if necessary
        parts += ['-'] * (9 - len(parts))

    parts.pop(1)  # drop second part (repeat upos?)
    pos, person, number, tense, mood, voice, gender, case, degree = parts

    # ensure correct PoS tag
    pos = upos_to_perseus(upos)  # 1: part of speech
    person = feats.get('Person', '-')  # 2: person
    number = _reconcile_xpos_feats(number, feats.get('Number'), 'number')  # 3: number
    tense = _reconcile_xpos_feats(tense, feats.get('Tense'), 'tense')  # 4: tense
    mood = _reconcile_xpos_feats(mood, feats.get('Mood'), 'mood')  # 5: mood
    voice = _reconcile_xpos_feats(voice, feats.get('Voice'), 'voice')  # 6: voice
    gender = _reconcile_xpos_feats(gender, feats.get('Gender'), 'gender')  # 7: gender
    case = _reconcile_xpos_feats(case, feats.get('Case'), 'case')  # 8: case
    degree = _reconcile_xpos_feats(degree, feats.get('Degree'), 'degree')  # 9: degree

    return f'{pos}{person}{number}{tense}{mood}{voice}{gender}{case}{degree}'
