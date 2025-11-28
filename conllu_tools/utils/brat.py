"""Utilities for BRAT standoff format."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Any

from conllu_tools.constants import BRAT_TYPE_TO_TYPE, TYPE_TO_BRAT_TYPE


def type_to_safe_type(typestring: str) -> str:
    """Rewrite characters in CoNLL-X types that cannot be directly used in identifiers in brat-flavored standoff.

    Arguments:
        typestring: The original CoNLL-X type string.

    Returns:
        A brat-compatible type string.

    """
    return ''.join([TYPE_TO_BRAT_TYPE.get(c, c) for c in typestring])


def safe_type_to_type(typestring: str) -> str:
    """Rewrite characters in brat-flavored standoff types back to CoNLL-X format.

    Arguments:
        typestring: The brat-safe type string.

    Returns:
        The original CoNLL-X type string.

    """
    for c, r in BRAT_TYPE_TO_TYPE.items():
        if c in typestring:
            typestring = typestring.replace(c, r)
    return typestring


def parse_annotation_line(line: str) -> dict[str, Any] | None:
    """Parse a BRAT annotation line into its components.

    Arguments:
        line: A single line from a BRAT .ann file.

    Returns:
        A dictionary with annotation details, or None if the line is invalid.

    """
    parts = line.strip().split('\t')
    if len(parts) < 2:  # noqa: PLR2004
        return None

    ann_type = parts[0][0]
    ann_id = int(parts[0][1:])

    if ann_type == 'T':
        # Entity annotation: T1	PUNCT 15 16	.
        if len(parts) >= 3:  # noqa: PLR2004
            annotation_parts = parts[1].split()
            upos = annotation_parts[0]
            start = int(annotation_parts[1])
            end = int(annotation_parts[2])
            form = parts[2] if len(parts) > 2 else ''  # noqa: PLR2004
            return {'type': 'T', 'id': ann_id, 'upos': upos, 'start': start, 'end': end, 'form': form}

    elif ann_type == 'R':
        # Relation annotation: R3	punct Arg1:T3 Arg2:T4
        annotation_parts = parts[1].split()
        deprel = annotation_parts[0]
        head = int(annotation_parts[1].split(':')[1][1:])  # Extract number from "T3"
        dep = int(annotation_parts[2].split(':')[1][1:])  # Extract number from "T4"
        return {'type': 'R', 'id': ann_id, 'deprel': deprel, 'head': head, 'dep': dep}

    return None


def format_annotation(ann: dict[str, Any]) -> str:
    """Format an annotation dict back into BRAT format.

    Arguments:
        ann: A dictionary with annotation details.

    Returns:
        A string formatted for a BRAT .ann file.

    """
    if ann['type'] == 'T':
        return f'{ann["type"]}{ann["id"]}\t{ann["upos"]} {ann["start"]} {ann["end"]}\t{ann["form"]}'
    if ann['type'] == 'R':
        return f'{ann["type"]}{ann["id"]}\t{ann["deprel"]} Arg1:T{ann["head"]} Arg2:T{ann["dep"]}'
    return ''


def read_annotations(filepath: str) -> list[dict[str, str | int]]:
    """Read and parse all annotations from a BRAT .ann file.

    Arguments:
        filepath: Path to the BRAT .ann file.

    Returns:
        A list of annotation dictionaries.

    """
    annotations = []
    with open(filepath, encoding='utf-8') as file:
        for line in file:
            ann = parse_annotation_line(line)
            if ann:
                annotations.append(ann)
    return annotations


def read_text_lines(filepath: str) -> list[str]:
    """Read the text content from a BRAT .txt file.

    Arguments:
        filepath: Path to the BRAT .txt file.

    Returns:
        The text content of the file as a list of strings.

    """
    with open(filepath, encoding='utf-8') as file:
        return list(file.readlines())


def sort_annotations_set(annotations: list[dict[str, Any]]) -> list[dict[str, str | int]]:
    """Sort set of annotations by ID number to maintain consistent ordering.

    Arguments:
        annotations: A list of annotation dictionaries.

    Returns:
        A sorted list of annotation dictionaries.

    """
    _type = annotations[0]['type'] if annotations else None
    sort_by_field = 'start' if _type == 'T' else 'id'
    return sorted(annotations, key=lambda x: int(x[sort_by_field]))


def sort_annotations(annotations: list[dict[str, Any]]) -> list[dict[str, str | int]]:
    """Sort annotations by type and ID number.

    Arguments:
        annotations: A list of annotation dictionaries.

    Returns:
        A sorted list of annotation dictionaries.

    """
    t_anns = sort_annotations_set([ann for ann in annotations if ann['type'] == 'T'])
    r_anns = sort_annotations_set([ann for ann in annotations if ann['type'] == 'R'])
    return t_anns + r_anns


def write_annotations(filepath: str | Path, annotations: list[dict[str, str | int]]) -> None:
    """Write annotations to a BRAT .ann file.

    Arguments:
        filepath: Path to the output BRAT .ann file.
        annotations: A list of annotation dictionaries to write.

    """
    with open(filepath, 'w', encoding='utf-8') as file:
        for ann in sort_annotations(annotations):
            file.write(format_annotation(ann) + '\n')


def write_text(filepath: str | Path, doctext: list[str]) -> None:
    """Write document text to a BRAT .txt file.

    Arguments:
        filepath: Path to the output BRAT .txt file.
        doctext: A list of strings representing the document text.

    """
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write('\n'.join(doctext))
        file.write('\n')  # Ensure the last line ends with a newline


def write_auxiliary_files(output_directory: str, metadata: dict[str, Any]) -> None:
    """Add metadata and default BRAT configuration files to the output directory.

    Arguments:
        output_directory: The directory to write the configuration files to.
        metadata: Dictionary with metadata values for the directory.

    """
    config_files = ['annotation.conf', 'tools.conf', 'visual.conf']
    for filename in config_files:
        config_file = files('conllu_tools').joinpath(f'data/{filename}')
        with config_file.open('r') as src, open(Path(output_directory) / filename, 'w') as dst:
            dst.write(src.read())

    with open(Path(output_directory) / 'metadata.json', 'w') as file:
        json.dump(metadata, file, indent=4)


def get_next_id_number(annotations: list[dict[str, Any]], prefix: str) -> int:
    """Find the next available ID number for a given prefix (T or R).

    Arguments:
        annotations: A list of annotation dictionaries.
        prefix: The prefix to search for ('T' for entities, 'R' for relations).

    Returns:
        The next available ID number for the given prefix.

    """
    max_num = 0
    for ann in annotations:
        if ann['type'] == prefix:
            num = int(ann['id'])
            max_num = max(max_num, num)
    return max_num + 1
