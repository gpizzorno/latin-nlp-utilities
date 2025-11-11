"""Interface for the BRAT module."""

from brat_to_conllu import brat_to_conllu
from conllu_to_brat import conllu_to_brat
from utils import (
    format_annotation,
    get_next_id_number,
    parse_annotation_line,
    read_annotations,
    read_text_lines,
    safe_type_to_type,
    sort_annotations,
    sort_annotations_set,
    type_to_safe_type,
    write_annotations,
    write_auxiliary_files,
    write_text,
)

__all__ = [
    'brat_to_conllu',
    'conllu_to_brat',
    'format_annotation',
    'get_next_id_number',
    'parse_annotation_line',
    'read_annotations',
    'read_text_lines',
    'safe_type_to_type',
    'sort_annotations',
    'sort_annotations_set',
    'type_to_safe_type',
    'write_annotations',
    'write_auxiliary_files',
    'write_text',
]
