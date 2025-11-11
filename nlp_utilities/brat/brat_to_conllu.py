"""Convert Brat standoff annotations to CoNLL-U format."""

from __future__ import annotations

import json
from pathlib import Path

import conllu
from typying import Any

from nlp_utilities.converters.features import feature_dict_to_string
from nlp_utilities.normalizers import normalize_features, normalize_xpos

from .utils import (
    get_next_id_number,
    read_annotations,
    read_text_lines,
    safe_type_to_type,
    sort_annotations_set,
)


def brat_to_conllu(  # noqa: C901, PLR0912, PLR0913, PLR0915
    input_directory: str | Path,
    output_directory: str | Path,
    feature_set: dict[str, Any],
    ref_conllu: str | Path | None = None,
    sents_per_doc: int | None = None,
    output_root: bool | None = None,  # noqa: FBT001
) -> None:
    """Convert Brat annotations back to CoNLL-U format."""
    if not input_directory:
        msg = 'Must provide input directory'
        raise FileNotFoundError(msg)

    if not output_directory:
        msg = 'Must provide output directory'
        raise FileNotFoundError(msg)

    if not Path(input_directory).is_dir():
        msg = f'Input directory not found: {input_directory}'
        raise FileNotFoundError(msg)

    ann_files = sorted(str(p) for p in Path(input_directory).glob('*.ann'))

    if len(ann_files) == 0:
        msg = f'No annotation files found: {input_directory}'
        raise FileNotFoundError(msg)

    # get metadata from directory if present
    meta_path = Path(input_directory) / 'metadata.json'
    if meta_path.exists():
        with meta_path.open('r', encoding='utf-8') as file:
            metadata = json.load(file)

        ref_conllu = metadata.get('conllu_filename')
        sents_per_doc = metadata.get('sents_per_doc')
        output_root = metadata.get('output_root')
        meta_error = 'none found in metadata file.'

    else:
        meta_error = 'no metadata file found in input directory.'

    assert ref_conllu is not None, f'No ref_conllu value passed and {meta_error}'
    assert sents_per_doc is not None, f'No sents_per_doc value passed and {meta_error}'
    assert output_root is not None, f'No output_root value passed and {meta_error}'

    # check if reference CoNLL-U file exists
    if not Path(ref_conllu).exists():
        msg = f'Reference CONLLU file not found: {ref_conllu}'
        raise FileNotFoundError(msg)

    # check if output directory exists, create if not
    output_path = Path(output_directory)
    if not output_path.is_dir():
        output_path.mkdir(parents=True, exist_ok=True)

    output_path = Path(output_directory) / f'{Path(ref_conllu).name}-from_brat.conllu'

    # load reference CoNLL-U data
    with open(ref_conllu, encoding='utf-8') as file:
        reference = conllu.parse(file.read())

    # load annotation data
    annotations, _lines = _get_annotations(ann_files)

    entities = [ann for ann in annotations if ann['type'] == 'T']
    relations = [ann for ann in annotations if ann['type'] == 'R']

    # add relation info to entities
    processed = []
    for relation in relations:
        head_id: int = relation['head']
        dep_id: int = relation['dep']
        deprel: str = relation.get('deprel', 'unknown_dep')
        if dep_id in processed:
            for entity in entities:
                if entity['id'] == dep_id:
                    entity.setdefault('deps', []).append((deprel, head_id))
                    break
        else:
            for entity in entities:
                if entity['id'] == dep_id:
                    entity['head'] = head_id
                    entity['deprel'] = deprel
                    processed.append(dep_id)
                    break

    # split into sentences
    annotated_sentences = []
    sentence: list[dict[str, Any]] = []

    for entity in entities:
        if entity['upos'] == 'ROOT':
            if sentence:
                annotated_sentences.append(sort_annotations_set(sentence))
                sentence = []
        else:
            sentence.append(entity)

    if sentence:
        annotated_sentences.append(sort_annotations_set(sentence))

    # generate output CoNLL-U
    for idx, ann_sentence in enumerate(annotated_sentences):
        try:
            ref_sentence = reference[idx]
        except IndexError:
            msg = f'Missing reference sentence for annotated sentence {idx + 1}.'
            raise ValueError(msg) from None

        sent_id = ref_sentence.metadata.get('sent_id', str(idx + 1))

        if len(ref_sentence) != len(ann_sentence):
            msg = (
                f'Sentence length mismatch at sentence {sent_id}:'
                f' reference has {len(ref_sentence)} tokens, but found {len(ann_sentence)} annotated tokens.'
            )
            raise ValueError(msg)

        # create concordance between CONLLU token no. and Brat token id
        concordance = {token['id']: i for i, token in enumerate(ann_sentence, start=1)}

        for token, entity in zip(ref_sentence, ann_sentence):
            # test that lowercased versions of tokens are the same
            if token['form'].lower() != entity['form'].lower():  # type: ignore [union-attr]
                msg = (
                    f'Token mismatch in sentence {sent_id}:'
                    f' reference token "{token["form"]}" does not match annotated token "{entity["form"]}".'
                    f' Context: {ref_sentence.metadata.get("text", "")}'
                )
                raise ValueError(msg)

            token_upos = token['upos']
            entity_deprel = safe_type_to_type(entity.get('deprel', '_'))  # type: ignore [arg-type]
            # quick fix for sum/esse as auxiliary verbs
            entity_upos = 'AUX' if entity_deprel == 'aux' else safe_type_to_type(entity['upos'])  # type: ignore [arg-type]
            if token_upos != entity_upos:
                token['xpos'] = normalize_xpos(entity_upos, token['xpos'])
                token['feats'] = feature_dict_to_string(normalize_features(entity_upos, token['feats'], feature_set))
                token['upos'] = entity_upos

            entity_head = concordance.get(entity.get('head'), '_')  # type: ignore [arg-type]
            entity_deprel = safe_type_to_type(entity.get('deprel', '_'))  # type: ignore [arg-type]

            token['head'] = entity_head
            token['deprel'] = entity_deprel

            # extended dep rels
            deps = entity.get('deps')
            if deps and isinstance(deps, list):
                new_deps = [(concordance.get(i[0], 0), i[1]) for i in deps]
                if entity_head and entity_deprel:
                    new_deps.append((concordance.get(entity_head, 0), entity_deprel))

                if new_deps:
                    token['deps'] = new_deps
            elif entity_head and entity_deprel:
                token['deps'] = [(entity_deprel, concordance.get(entity_head, 0))]

        # fix full stop dependencies if present
        sent_root = None
        for token in ref_sentence:
            # fix full stop dependencies if present
            if token['head'] == 0:
                sent_root = token['id']

            if token['upos'] == 'PUNCT' and sent_root:
                token['head'] = sent_root
                token['deps'] = ['punct', sent_root]
                sent_root = None

    with open(output_path, 'w', encoding='utf-8') as file:
        for sent in reference:
            file.write(sent.serialize())


def _get_annotations(annotation_files: list[str]) -> tuple[list[dict[str, Any]], list[str]]:  # noqa: C901
    """Load annotations from a list of BRAT .ann files.

    Arguments:
        annotation_files: List of paths to BRAT .ann files.

    Returns:
        A tuple containing:
            - A list of annotation dictionaries from all files, with adjusted offsets and remapped IDs.
            - A list of strings representing the concatenated document text lines.

    """
    annotations = []
    lines = []

    for ann_file in annotation_files:
        annotations.append(read_annotations(ann_file))
        lines.append(read_text_lines(ann_file.replace('.ann', '.txt')))

    # fixes / checks

    # adjust offsets
    base_offset = 0

    for file_anns, file_lines in zip(annotations, lines):
        for ann in file_anns:
            if ann['type'] == 'T':
                ann['start'] += base_offset  # type: ignore [operator]
                ann['end'] += base_offset  # type: ignore [operator]

        base_offset += sum(len(line) for line in file_lines)

    # determine the next free sequential ID for each type
    next_free: dict[str, int] = {}
    next_free['T'] = get_next_id_number([a for sublist in annotations for a in sublist], 'T')
    next_free['R'] = get_next_id_number([a for sublist in annotations for a in sublist], 'R')

    # remap IDs
    reserved: dict[str, list[int]] = {}

    for file_anns in annotations:
        id_map: dict[str, dict[int, int]] = {}

        for ann in file_anns:
            ann_id: int = ann['id']  # type: ignore [assignment]
            ann_type: str = ann['type']  # type: ignore [assignment]

            if ann_id in reserved[ann_type]:
                # ID collision, assign a new ID
                new_id = next_free[ann_type]
                next_free[ann_type] += 1

                id_map.setdefault(ann_type, {})[ann_id] = new_id
                reserved[ann_type].append(new_id)
                ann['id'] = new_id

            else:
                # no collision, keep the same ID
                id_map.setdefault(ann_type, {})[ann_id] = ann_id
                reserved[ann_type].append(ann_id)

        # remap ID references
        for ann in file_anns:
            if ann['type'] == 'R':  # only relations have references
                head_id: int = ann['head']  # type: ignore [assignment]
                dep_id: int = ann['dep']  # type: ignore [assignment]

                if head_id in id_map.get('T', {}):
                    ann['head'] = id_map['T'][head_id]

                if dep_id in id_map.get('T', {}):
                    ann['dep'] = id_map['T'][dep_id]

    return [a for sublist in annotations for a in sublist], [line for sublist in lines for line in sublist]
