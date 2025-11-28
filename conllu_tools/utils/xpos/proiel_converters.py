"""Functions for converting between PROIEL and Perseus XPOS tags."""

from __future__ import annotations

from conllu_tools.constants import PROIEL_CONCORDANCES
from conllu_tools.utils.features import feature_string_to_dict
from conllu_tools.utils.upos import upos_to_perseus


def _to_number(value: str | None) -> str:
    """Convert PROIEL 'num' to Perseus 3: 'number'."""
    if value is None:
        return '-'

    concordance = PROIEL_CONCORDANCES.get('number', {})

    return concordance.get(value, '-')  # Return '-' if no match found


def _to_tense(value: str | None) -> str:
    """Convert PROIEL 'tense' to Perseus 4: 'tense'."""
    if value is None:
        return '-'

    concordance = PROIEL_CONCORDANCES.get('tense', {})

    return concordance.get(value, '-')  # Return '-' if no match found


def _to_mood(value: str | None) -> str:
    """Convert PROIEL 'mood' to Perseus 5: 'mood'."""
    if value is None:
        return '-'

    concordance = PROIEL_CONCORDANCES.get('mood', {})

    return concordance.get(value, '-')  # Return '-' if no match found


def _to_voice(value: str | None) -> str:
    """Convert PROIEL 'voice' to Perseus 6: 'voice'."""
    if value is None:
        return '-'

    concordance = PROIEL_CONCORDANCES.get('voice', {})
    return concordance.get(value, '-')  # Return '-' if no match found


def _to_gender(value: str | None) -> str:
    """Convert PROIEL 'gender' to Perseus 7: 'gender'."""
    if value is None:
        return '-'

    concordance = PROIEL_CONCORDANCES.get('gender', {})

    return concordance.get(value, '-')  # Return '-' if no match found


def _to_case(value: str | None) -> str:
    """Convert PROIEL 'case' to Perseus 8: 'case'."""
    if value is None:
        return '-'

    concordance = PROIEL_CONCORDANCES.get('case', {})

    return concordance.get(value, '-')  # Return '-' if no match found


def _to_degree(value: str | None) -> str:
    """Convert PROIEL 'degree' to Perseus 9: 'degree'."""
    if value is None:
        return '-'

    concordance = PROIEL_CONCORDANCES.get('degree', {})

    return concordance.get(value, '-')  # Return '-' if no match found


def proiel_to_perseus(upos: str, feats: dict[str, str] | str) -> str:
    """Convert PROIEL UPOS and FEATS to Perseus XPOS tag.

    Arguments:
        upos: The Universal Part of Speech tag.
        feats: A feature string or dictionary of features.

    Returns:
        A Perseus XPOS string.

    """
    if isinstance(feats, str):
        feats = feature_string_to_dict(feats)

    # compile tags:
    pos = upos_to_perseus(upos)  # 1: part of speech
    person = feats.get('Person', '-')  # 2: person
    number = _to_number(feats.get('Number')) if 'Number' in feats else '-'  # 3: number
    tense = _to_tense(feats.get('Tense')) if 'Tense' in feats else '-'  # 4: tense
    mood = _to_mood(feats.get('Mood')) if 'Mood' in feats else '-'  # 5: mood
    voice = _to_voice(feats.get('Voice')) if 'Voice' in feats else '-'  # 6: voice
    gender = _to_gender(feats.get('Gender')) if 'Gender' in feats else '-'  # 7: gender
    case = _to_case(feats.get('Case')) if 'Case' in feats else '-'  # 8: case
    degree = _to_degree(feats.get('Degree')) if 'Degree' in feats else '-'  # 9: degree

    return f'{pos}{person}{number}{tense}{mood}{voice}{gender}{case}{degree}'
