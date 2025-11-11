"""Functions for converting between PROIEL and Perseus XPOS tags."""

from __future__ import annotations

from nlp_utilities.constants import PROIEL_CONCORDANCES
from nlp_utilities.converters.features import feature_string_to_dict
from nlp_utilities.converters.upos import upos_to_perseus


def to_number(value: str | None) -> str:
    """Convert PROIEL 'num' to Perseus 3: 'number'."""
    if value is None:
        return '-'

    concordance = PROIEL_CONCORDANCES.get('to_number', {})

    return concordance.get(value, '-')  # Return '-' if no match found


def to_tense(value: str | None) -> str:
    """Convert PROIEL 'tense' to Perseus 4: 'tense'."""
    if value is None:
        return '-'

    concordance = PROIEL_CONCORDANCES.get('to_tense', {})

    return concordance.get(value, '-')  # Return '-' if no match found


def to_mood(value: str | None) -> str:
    """Convert PROIEL 'mood' to Perseus 5: 'mood'."""
    if value is None:
        return '-'

    concordance = PROIEL_CONCORDANCES.get('to_mood', {})

    return concordance.get(value, '-')  # Return '-' if no match found


def to_voice(value: str | None) -> str:
    """Convert PROIEL 'voice' to Perseus 6: 'voice'."""
    if value is None:
        return '-'

    concordance = PROIEL_CONCORDANCES.get('to_voice', {})
    return concordance.get(value, '-')  # Return '-' if no match found


def to_gender(value: str | None) -> str:
    """Convert PROIEL 'gender' to Perseus 7: 'gender'."""
    if value is None:
        return '-'

    concordance = PROIEL_CONCORDANCES.get('to_gender', {})

    return concordance.get(value, '-')  # Return '-' if no match found


def to_case(value: str | None) -> str:
    """Convert PROIEL 'case' to Perseus 8: 'case'."""
    if value is None:
        return '-'

    concordance = PROIEL_CONCORDANCES.get('to_case', {})

    return concordance.get(value, '-')  # Return '-' if no match found


def to_degree(value: str | None) -> str:
    """Convert PROIEL 'degree' to Perseus 9: 'degree'."""
    if value is None:
        return '-'

    concordance = PROIEL_CONCORDANCES.get('to_degree', {})

    return concordance.get(value, '-')  # Return '-' if no match found


def proiel_to_perseus(upos: str, feats: str) -> str:
    """Format PROIEL UPOS and FEATS as Perseus XPOS tag."""
    feats_dict = feature_string_to_dict(feats)

    # compile tags:
    pos = upos_to_perseus(upos)  # 1: part of speech
    person = feats_dict.get('Person', '-')  # 2: person
    number = to_number(feats_dict.get('Number')) if 'Number' in feats_dict else '-'  # 3: number
    tense = to_tense(feats_dict.get('Tense')) if 'Tense' in feats_dict else '-'  # 4: tense
    mood = to_mood(feats_dict.get('Mood')) if 'Mood' in feats_dict else '-'  # 5: mood
    voice = to_voice(feats_dict.get('Voice')) if 'Voice' in feats_dict else '-'  # 6: voice
    gender = to_gender(feats_dict.get('Gender')) if 'Gender' in feats_dict else '-'  # 7: gender
    case = to_case(feats_dict.get('Case')) if 'Case' in feats_dict else '-'  # 8: case
    degree = to_degree(feats_dict.get('Degree')) if 'Degree' in feats_dict else '-'  # 9: degree

    return f'{pos}{person}{number}{tense}{mood}{voice}{gender}{case}{degree}'
