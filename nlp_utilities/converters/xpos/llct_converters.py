"""Functions for converting between LLCT and Perseus XPOS tags."""

from __future__ import annotations

from nlp_utilities.constants import LLCT_CONCORDANCES
from nlp_utilities.converters.features import feature_string_to_dict
from nlp_utilities.converters.upos import upos_to_perseus


def validate_xpos_value(value: str | None, feats_type: str) -> str | None:
    """Validate LLCT XPOS value against concordance."""
    if value is None or value == '-':
        return None

    valid_values = LLCT_CONCORDANCES[feats_type].values()

    if value in valid_values:
        return value

    return None


def reconcile_xpos_feats(xpos_value: str | None, feats_value: str | None, feats_type: str) -> str:
    """Reconcile LLCT XPOS and FEATS values."""
    # map FEATS value to XPOS value
    feats_value = LLCT_CONCORDANCES[feats_type].get(feats_value) if feats_value else None
    # validate both values
    xpos_value = validate_xpos_value(xpos_value, feats_type)
    feats_value = validate_xpos_value(feats_value, feats_type)

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


def llct_to_perseus(upos: str, xpos: str, feats: str) -> str:
    """Format LLCT UPOS, XPOS, and FEATS as Perseus XPOS tag."""
    if not feats and '|' not in xpos:  # invalid punctuation xpos
        return f'{upos_to_perseus(upos)}--------'

    feats_dict = feature_string_to_dict(feats)
    parts = xpos.split('|')

    if len(parts) != 9:  # noqa: PLR2004
        # complete with dash if necessary
        parts += ['-'] * (9 - len(parts))

    parts.pop(1)  # drop second part (repeat upos?)
    pos, person, number, tense, mood, voice, gender, case, degree = parts

    # ensure correct PoS tag
    pos = upos_to_perseus(upos)  # 1: part of speech
    person = feats_dict.get('Person', '-')  # 2: person
    number = reconcile_xpos_feats(number, feats_dict.get('Number'), 'number')  # 3: number
    tense = reconcile_xpos_feats(tense, feats_dict.get('Tense'), 'tense')  # 4: tense
    mood = reconcile_xpos_feats(mood, feats_dict.get('Mood'), 'mood')  # 5: mood
    voice = reconcile_xpos_feats(voice, feats_dict.get('Voice'), 'voice')  # 6: voice
    gender = reconcile_xpos_feats(gender, feats_dict.get('Gender'), 'gender')  # 7: gender
    case = reconcile_xpos_feats(case, feats_dict.get('Case'), 'case')  # 8: case
    degree = reconcile_xpos_feats(degree, feats_dict.get('Degree'), 'degree')  # 9: degree

    return f'{pos}{person}{number}{tense}{mood}{voice}{gender}{case}{degree}'
