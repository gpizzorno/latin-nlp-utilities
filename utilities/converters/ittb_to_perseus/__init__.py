"""Interface for the ITTB to Perseus converters."""

from .ittb_converters import (
    cas_to_case,
    cas_to_number,
    gen_to_gender,
    gen_to_number,
    gen_to_person,
    grnp_to_degree,
    mod_to_mood,
    mod_to_voice,
    tem_to_tense,
)

__all__ = [
    'cas_to_case',
    'cas_to_number',
    'gen_to_gender',
    'gen_to_number',
    'gen_to_person',
    'grnp_to_degree',
    'mod_to_mood',
    'mod_to_voice',
    'tem_to_tense',
]
