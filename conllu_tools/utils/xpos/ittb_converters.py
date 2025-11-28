"""Functions for converting between ITTB and Perseus XPOS tags."""

from __future__ import annotations

from conllu_tools.constants import ITTB_CONCORDANCES
from conllu_tools.utils.upos import upos_to_perseus


def _gen_to_person(value: str | None) -> str:
    """Convert ITTB 'gen' to Perseus 2: 'person'."""
    if value is None:
        return '-'

    concordance = ITTB_CONCORDANCES.get('gen_to_person', [])

    for gen_values, person in concordance:
        if value in gen_values:
            return person  # type: ignore [return-value]

    return '-'  # Return '-' if no match found


def _gen_to_number(value: str | None) -> str:
    """Convert ITTB 'gen' to Perseus 3: 'number'."""
    if value is None:
        return '-'

    concordance = ITTB_CONCORDANCES.get('gen_to_number', [])

    for gen_values, number in concordance:
        if value in gen_values:
            return number  # type: ignore [return-value]

    return '-'  # Return '-' if no match found


def _cas_to_number(value: str | None) -> str:
    """Convert ITTB 'cas' to Perseus 3: 'number'."""
    if value is None:
        return '-'

    concordance = ITTB_CONCORDANCES.get('cas_to_number', [])

    for cas_values, number in concordance:
        if value in cas_values:
            return number  # type: ignore [return-value]

    return '-'  # Return '-' if no match found


def _tem_to_tense(value: str | None) -> str:
    """Convert ITTB 'tem' to Perseus 4: 'tense'."""
    if value is None:
        return '-'

    concordance: dict[str, str] = ITTB_CONCORDANCES.get('tem_to_tense', {})  # type: ignore [assignment]

    return concordance.get(value, '-')  # Return '-' if no match found


def _mod_to_mood(value: str | None) -> str:
    """Convert ITTB 'mod' to Perseus 5: 'mood'."""
    if value is None:
        return '-'

    concordance = ITTB_CONCORDANCES.get('mod_to_mood', [])

    for mod_values, mood in concordance:
        if value in mod_values:
            return mood  # type: ignore [return-value]

    return '-'  # Return '-' if no match found


def _mod_to_voice(value: str | None) -> str:
    """Convert ITTB 'mod' to Perseus 6: 'voice'."""
    if value is None:
        return '-'

    concordance = ITTB_CONCORDANCES.get('mod_to_voice', [])

    for mod_values, voice in concordance:
        if value in mod_values:
            return voice  # type: ignore [return-value]

    return '-'  # Return '-' if no match found


def _gen_to_gender(value: str | None) -> str:
    """Convert ITTB 'gen' to Perseus 7: 'gender'."""
    if value is None:
        return '-'

    concordance: dict[str, str] = ITTB_CONCORDANCES.get('gen_to_gender', {})  # type: ignore [assignment]

    return concordance.get(value, '-')  # Return '-' if no match found


def _cas_to_case(value: str | None) -> str:
    """Convert ITTB 'cas' to Perseus 8: 'case'."""
    if value is None:
        return '-'

    concordance = ITTB_CONCORDANCES.get('cas_to_case', {})

    for cas_values, case in concordance:
        if value in cas_values:
            return case  # type: ignore [return-value]

    return '-'  # Return '-' if no match found


def _grnp_to_degree(value: str | None) -> str:
    """Convert ITTB 'grn' or 'grp' to Perseus 9: 'degree'."""
    if value is None:
        return '-'

    concordance: dict[str, str] = ITTB_CONCORDANCES.get('grnp_to_degree', {})  # type: ignore [assignment]

    return concordance.get(value, '-')  # Return '-' if no match found


def ittb_to_perseus(upos: str | None, xpos: str | None) -> str:
    """Convert ITTB UPOS and XPOS to Perseus XPOS tag.

    Arguments:
        upos: The Universal Part of Speech tag.
        xpos: The ITTB XPOS tag.

    Returns:
        A Perseus XPOS string.

    """
    if upos is None or xpos is None:
        return '----------'

    xpos_dict = {el[:3]: el[3] for el in xpos.split('|') if len(el) == 4}  # noqa: PLR2004

    # compile tags:
    pos = upos_to_perseus(upos)  # 1: part of speech
    person = _gen_to_person(xpos_dict['gen']) if 'gen' in xpos_dict else '-'  # 2: person

    # 3: number
    if 'cas' in xpos_dict:
        number = _cas_to_number(xpos_dict['cas'])
    elif 'gen' in xpos_dict:
        number = _gen_to_number(xpos_dict['gen'])
    else:
        number = '-'

    tense = _tem_to_tense(xpos_dict['tem']) if 'tem' in xpos_dict else '-'  # 4: tense
    mood = _mod_to_mood(xpos_dict['mod']) if 'mod' in xpos_dict else '-'  # 5: mood
    voice = _mod_to_voice(xpos_dict['mod']) if 'mod' in xpos_dict else '-'  # 6: voice
    gender = _gen_to_gender(xpos_dict['gen']) if 'gen' in xpos_dict else '-'  # 7: gender
    case = _cas_to_case(xpos_dict['cas']) if 'cas' in xpos_dict else '-'  # 8: case

    # 9: degree
    ittb_t = xpos_dict.get('grn', xpos_dict.get('grp'))
    degree = _grnp_to_degree(ittb_t) if ittb_t else '-'

    return f'{pos}{person}{number}{tense}{mood}{voice}{gender}{case}{degree}'
