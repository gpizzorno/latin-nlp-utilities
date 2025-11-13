"""Utility functions for converting CoNLL-U formatted data to BRAT standoff format."""

from __future__ import annotations

from pathlib import Path

import conllu

from .utils import (
    type_to_safe_type,
    write_annotations,
    write_auxiliary_files,
    write_text,
)


# Based on https://github.com/nlplab/brat/blob/master/tools/conllXtostandoff.py
def conllu_to_brat(
    conllu_filename: str,
    output_directory: str,
    sents_per_doc: int | None = None,
    output_root: bool = True,  # noqa: FBT001
) -> None:
    """Convert a CONLLU formatted file to Brat's standoff format.

    Arguments:
        conllu_filename: Path to the input CONLLU file.
        output_directory: Directory to write the output BRAT files.
        sents_per_doc: Maximum number of sentences per output document. If None, all sentences
            are written to a single document.
        output_root: Whether to include an explicit ROOT node in the output.

    """
    # check if conllu file exists
    if not Path(conllu_filename).is_file():
        msg = f'Input CONLLU file not found: {conllu_filename}'
        raise FileNotFoundError(msg)

    # check if output directory exists, create if not
    output_path = Path(output_directory)
    if not output_path.is_dir():
        output_path.mkdir(parents=True, exist_ok=True)

    docnum = 0 if sents_per_doc is None else 1
    metadata = {
        'conllu_filename': conllu_filename,
        'sents_per_doc': sents_per_doc,
        'output_root': output_root,
    }
    sentences: list[tuple[str, list[dict[str, str | int]], list[dict[str, str | int]]]] = []

    with open(conllu_filename, encoding='utf-8') as data_file:
        for idx, sentence in enumerate(conllu.parse_incr(data_file), start=1):
            entities: list[dict[str, str | int]] = []
            relations: list[dict[str, str | int]] = []
            sent_id: str = sentence.metadata.get('sent_id', str(idx))

            if output_root:
                # add an explicit root node with seq ID 0 (zero)
                entities.append({'type': 'T', 'id': 0, 'form': 'ROOT', 'upos': 'ROOT'})

            for token in sentence:
                entities.append({'type': 'T', **{k: v for k, v in token.items() if k in ['id', 'form', 'upos']}})
                if token.get('head', '_') != '_':  # allow value "_" for HEAD to indicate no dependency
                    # if root is not added, skip deps to the root (idx 0)
                    if not output_root and token['head'] == 0:
                        continue
                    relations.append({'type': 'R', **{k: v for k, v in token.items() if k in ['id', 'head', 'deprel']}})

            sentences.append((sent_id, entities, relations))

            # limit sentences per output "document"
            if sents_per_doc and len(sentences) >= sents_per_doc:
                _write_document(sentences, conllu_filename, output_directory, docnum)
                sentences = []
                docnum += 1

    # process leftovers, if any
    if len(sentences) > 0:
        _write_document(sentences, conllu_filename, output_directory, docnum)

    write_auxiliary_files(output_directory, metadata)


def _write_document(  # noqa: C901, PLR0915
    sentences: list[tuple[str, list[dict[str, str | int]], list[dict[str, str | int]]]],
    ref_filename: str,
    output_directory: str,
    docnum: int = 0,
) -> None:
    """Write a single document to BRAT format.

    Arguments:
        sentences: A list of sentences, each represented as a tuple containing the sentence ID,
            a list of entity annotations, and a list of relation annotations.
        ref_filename: The reference filename to base the output filename on.
        output_directory: The directory to write the output files to.
        docnum: An optional document number to append to the output filename.

    """
    # Remove .conllu extension if present to avoid .conllu.ann and .conllu.txt files
    base_name = Path(ref_filename).stem if Path(ref_filename).suffix == '.conllu' else Path(ref_filename).name
    fn_base = f'{base_name}-doc-{str(docnum).zfill(3)}' if docnum != 0 else base_name
    output_path = Path(output_directory) / fn_base

    offset = 0
    next_ent_id = 1
    next_rel_id = 1
    doctext = []
    annotations = []

    for sentence in sentences:
        sent_id, entities, relations = sentence

        tokens = []
        id_map = {}  # store mapping from per-sentence sequence IDs to document-unique IDs

        # output entities
        for entity in entities:
            ent_id = entity['id']

            if ent_id in id_map:
                msg = f'Duplicate entity ID {ent_id} in sentence {sent_id}.'
                raise ValueError(msg)

            id_map[ent_id] = next_ent_id
            entity['id'] = next_ent_id
            next_ent_id += 1

            form: str = entity.get('form')  # type: ignore [assignment]

            if not form:
                msg = f'Missing FORM for entity ID {ent_id} in sentence {sent_id}.'
                raise ValueError(msg)

            tokens.append(form)
            entity['start'] = offset
            entity['end'] = offset + len(form)
            upos = entity.get('upos')
            if not upos or upos == '_':
                upos = 'X'
            entity['upos'] = type_to_safe_type(upos)  # type: ignore [arg-type]
            offset += len(form) + 1  # +1 for space

            annotations.append(entity)

        # Add the text for this sentence
        if tokens:
            doctext.append(' '.join(tokens))

        # output relations
        for relation in relations:
            head_id = relation['head']
            dep_id = relation['id']

            # Skip relations where head or dep is None (from HEAD='_')
            if head_id is None or dep_id is None:
                continue

            if head_id not in id_map or dep_id not in id_map:
                msg = f'Invalid relation IDs in sentence {sent_id}: head {head_id}, dep {dep_id}.'
                raise ValueError(msg)

            relation['head'] = id_map[head_id]
            relation['dep'] = id_map[dep_id]
            relation['id'] = next_rel_id
            deprel = relation.get('deprel')
            if not deprel or deprel == '_':
                deprel = 'X'
            relation['deprel'] = type_to_safe_type(deprel)  # type: ignore [arg-type]
            next_rel_id += 1

            annotations.append(relation)

    write_annotations(f'{output_path}.ann', annotations)
    write_text(f'{output_path}.txt', doctext)
