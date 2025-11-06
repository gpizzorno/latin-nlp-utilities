"""Convert Brat annotations to CoNLL-U format."""

import json
from pathlib import Path

import regex as re  # https://pypi.org/project/regex/

from .utils import feature_dict_to_string, load_lang_features, normalize_features, normalize_xpos


# define helper functions
def conll2lists(filename, sents_per_doc):
    """Convert a CoNLL-U file to lists of sentences and IDs."""
    conllu_o_ids, conllu_o_sentences = [], []
    sentid_re = re.compile(r'^# sent_id\s*=\s*(\S+)$')

    with open(filename) as file:
        raw_lines = [line.strip() for line in file.readlines()]

    sent = []
    for line in raw_lines:
        if line:
            if line[0] == '#':
                match = sentid_re.match(line)
                if match:
                    conllu_o_ids.append(match.group(1))
                    if sent:
                        conllu_o_sentences.append(sent)
                        sent = []
                else:
                    continue
            else:
                sent.append(line.split('\t'))
    if sent:
        conllu_o_sentences.append(sent)

    sentence_concordance = {}
    doc, sent = 1, 1
    for idx, sent_id in enumerate(conllu_o_ids, start=1):
        sentence_concordance[sent_id] = {'alt_id': f'Brat {doc}:{sent}', 'order': idx}

        if sent == sents_per_doc:
            sent = 1
            doc += 1
        else:
            sent += 1

    return conllu_o_ids, conllu_o_sentences, sentence_concordance


def parse_id(line):
    """Parse an ID from a line."""
    m = re.match(r'^(([TR#])(\S*))', line)
    assert m, f'Failed to parse ID: {line}'
    return m.groups()


def parse_key_value(kv):
    """Parse a key-value pair from a string."""
    m = re.match(r'^(\S+):(\S+)$', kv)
    assert m, f'Failed to parse key-value pair: {kv}'
    return m.groups()


def remap_key_values(kvs, idmap):
    """Remap key-value pairs based on an ID map."""
    remapped = []
    for kv in kvs:
        k, v = parse_key_value(kv)
        v = idmap.get(v, v)
        remapped.append(f'{k}:{v}')
    return remapped


def remap_relation_idrefs(line, idmap):
    """Remap ID references in a relation line."""
    fields = line.split('\t')
    assert len(fields) >= 2, 'format error'  # noqa: PLR2004

    type_args = fields[1].split(' ')
    assert len(type_args) >= 3, 'format error'  # noqa: PLR2004

    args = type_args[1:]
    args = remap_key_values(args, idmap)
    fields[1] = ' '.join(type_args[:1] + args)

    return '\t'.join(fields)


def remap_attrib_idrefs(line, idmap):
    """Remap ID references in an attribute line."""
    fields = line.split('\t')
    assert len(fields) >= 2, 'format error'  # noqa: PLR2004

    type_args = fields[1].split(' ')
    assert len(type_args) >= 2, 'format error'  # noqa: PLR2004

    args = type_args[1:]
    args = [idmap.get(a, a) for a in args]
    fields[1] = ' '.join(type_args[:1] + args)

    return '\t'.join(fields)


def fix_annotations(annotations):  # noqa: C901
    """Fix the annotations by sorting, renumbering, and remapping IDs."""
    textbound, relations, comments = [], [], []
    for ann in annotations:
        vals = ann.strip().split('\t')
        if ann[0] == 'T':
            upos, *offsets = vals[1].split()
            word = vals[2]
            # Store all offsets as a single string (handles discontinuous spans)
            textbound.append([vals[0][0], vals[0][1:], upos, ' '.join(offsets), word])
        elif ann[0] == 'R':
            # format = TYPE, ID, REL, ARG1_VALUE, ARG2_VALUE
            args = vals[1].split()
            relations.append([vals[0][0], vals[0][1:], args[0], args[1][5:], args[2][5:]])
        elif ann[0] == '#':
            comments.append(ann)
        else:
            msg = f'Unknown annotation category {ann[0]}'
            raise ValueError(msg)

    textbound.sort(key=lambda x: int(x[3].split(';')[0].split(' ')[0]))  # sort by first offset start
    relations.sort(key=lambda x: int(x[1]))  # sort by id

    # change ids and generate id map
    id_map = {}
    changed = False
    for i, ann in enumerate(textbound, start=int(textbound[0][1])):
        if ann[1] != i:
            changed = True
        id_map[f'T{ann[1]}'] = f'T{i}'
        ann[1] = i

    # if texbound ids needed amending, then fix relation references
    if changed:
        for ann in relations:
            ann[3] = id_map.get(ann[3])
            ann[4] = id_map.get(ann[4])

    # compile results
    new_annotations = []
    for ann in textbound:
        _type, _id, upos, offsets, word = ann
        new_annotations.append(f'{_type}{_id}\t{upos} {offsets}\t{word}\n')

    for ann in relations:
        _type, _id, rel, val1, val2 = ann
        new_annotations.append(f'{_type}{_id}\t{rel} Arg1:{val1} Arg2:{val2}\n')

    return new_annotations + comments


def join_annotations(ann_files):  # noqa: C901, PLR0912, PLR0915
    """Process each .ann in turn, keeping track of the "base" offset from (conceptual) catenation of the texts."""
    anns, texts = [], []
    for fn in ann_files:
        with open(fn) as file:
            anns.append(file.readlines())

        txtfn = re.sub(r'\.ann$', '.txt', fn)
        with open(txtfn) as file:
            texts.append(file.readlines())

    baseoff = 0
    for i in range(len(anns)):
        # fix annotations (e.g. lines in wrong order, renumbered textbound entries, etc.)
        anns[i] = fix_annotations(anns[i])

        # revise textbound annotation offsets by the base
        for j in range(len(anns[i])):
            line = anns[i][j]
            # see http://brat.nlplab.org/standoff.html for format
            if not line or line[0] != 'T':
                continue

            m = re.match(r'^(T\d+\t\S+) (\d+ \d+(?:;\d+ \d+)*)(\t.*\n?)', line)
            assert m, f'failed to parse "{line}"'
            begin, offsets, end = m.groups()

            new_offsets = []
            for offset in offsets.split(';'):
                startoff, endoff = offset.split(' ')
                startoff = int(startoff) + baseoff
                endoff = int(endoff) + baseoff
                new_offsets.append(f'{startoff} {endoff}')

            offsets = ';'.join(new_offsets)

            anns[i][j] = f'{begin} {offsets}{end}'

        baseoff += sum(len(line) for line in texts[i])

    # determine the full set of IDs currently in use in any of the .anns
    reserved_id = {}
    for i in range(len(anns)):
        for line in anns[i]:
            aid, idchar, idseq = parse_id(line)
            reserved_id[aid] = (idchar, idseq)

    # use that to determine the next free "sequential" ID for each
    # initial character in use in IDs.
    idchars = {aid[0] for aid in reserved_id}
    next_free_seq = {}

    for c in idchars:
        maxseq = 1

        for aid in [a for a in reserved_id if a[0] == c]:
            idchar, idseq = reserved_id[aid]
            try:
                idseq = int(idseq)
                maxseq = max(idseq, maxseq)
            except ValueError:  # non-int ID tail; harmless here
                pass

        next_free_seq[c] = maxseq + 1

    # next, remap IDs: process each .ann in turn, keeping track of
    # which IDs are in use, and assign the next free ID in case of
    # collisions from catenation. Also, remap ID references accordingly.
    reserved = {}
    for i in range(len(anns)):
        idmap = {}
        for j in range(len(anns[i])):
            line = anns[i][j]
            aid, idchar, idseq = parse_id(line)

            if aid not in reserved:
                reserved[aid] = True

            else:
                newid = f'{idchar}{next_free_seq[idchar]}'
                next_free_seq[idchar] += 1

                assert aid not in idmap

                idmap[aid] = newid
                line = '\t'.join([newid, *line.split('\t')[1:]])
                reserved[newid] = True

            anns[i][j] = line

        # remap ID references
        for j in range(len(anns[i])):
            line = anns[i][j].rstrip()
            tail = anns[i][j][len(line) :]
            aid, idchar, idseq = parse_id(line)

            if idchar == 'T':  # textbound; can't refer to anything
                pass

            elif idchar == 'R':  # relation
                line = remap_relation_idrefs(line, idmap)

            elif idchar == '#':  # note
                # line = remap_note_idrefs(line, idmap)
                pass

            else:
                print(f'Warning: unrecognized annotation, cannot remap ID references: {line}')

            anns[i][j] = line + tail

    annotations = []
    for i in range(len(anns)):
        for line in anns[i]:
            fields = line.strip().split('\t')
            if fields[0][0] == 'T':
                upos, *offsets = fields[1].split(' ')
                word = fields[2]
                annotations.append([fields[0][0], fields[0][1:], upos, ' '.join(offsets), word])
            else:
                annotations.append(fields)

    return annotations


def get_sentence_text(conll_list):
    """Get the text of a sentence from a CoNLL-U list."""
    tokens = [i[1] for i in conll_list]
    fs = ''
    if tokens[-1] == '.':
        fs = tokens.pop(-1)

    return ' '.join(tokens) + fs


def brat_to_conllu(input_dir, conllu_path, sents_per_doc, lang, additional_features=None, dalme=False):  # noqa: C901, PLR0912, PLR0913, PLR0915
    """Convert Brat annotations to CoNLL-U format."""
    ann_files = sorted(str(p) for p in Path(input_dir).glob('*.ann'))

    # determine filenames
    og_path = Path(conllu_path)
    conllu_dir = og_path.parent
    filename_stem = og_path.stem
    output_filename = f'{filename_stem}-fixeddep.conllu'

    # get original (i.e. pre-annotation) CONLLU data
    conllu_o_ids, conllu_o_sentences, sentence_concordance = conll2lists(conllu_path, sents_per_doc)

    # load feature data
    featset = load_lang_features(lang, additional_features, dalme)

    # join annotations
    annotations = join_annotations(ann_files)

    tokens = [i for i in annotations if i[0][0] == 'T']
    relations = [i for i in annotations if i[0][0] == 'R']
    # notes = [i for i in annotations if i[0][0] == '#']
    annotated_tokens = {}  # value format: ID TOKEN UPOS HEAD DEPREL DEPS

    for token_data in tokens:
        upos = token_data[2]
        _id = int(token_data[1])
        token = token_data[4]
        annotated_tokens[_id] = [_id, token, upos, None, None, []]

    processed_targets = []
    for relation in relations:
        rel, arg1, arg2 = relation[1].split(' ')
        source = int(arg1[6:])
        target = int(arg2[6:])
        if target in processed_targets:
            annotated_tokens[target][5].append((source, rel))
        else:
            annotated_tokens[target][3] = source
            annotated_tokens[target][4] = rel
            processed_targets.append(target)

    annotated_tokens = list(annotated_tokens.values())

    # split into sentences
    annotated_sentences = []
    sentence = []
    for token_data in annotated_tokens:
        if token_data[1] == 'ROOT':
            if sentence:
                annotated_sentences.append(sentence)
                sentence = []
        else:
            sentence.append(token_data)

    if sentence:
        annotated_sentences.append(sentence)

    conllu_output = []
    for idx, sentence in enumerate(annotated_sentences):
        og_sent = conllu_o_sentences[idx]
        conllu_output.append(f'# sent_id = {conllu_o_ids[idx]}')
        conllu_output.append(f'# text = {get_sentence_text(og_sent)}')
        # create concordance between CONLLU token no. and Brat token id
        concordance = {token[0]: i for i, token in enumerate(sentence, start=1)}
        # apply fixes to original CONLLU data
        for i, token in enumerate(sentence):
            _id, word, upos, head, deprel, deps = token
            # test that lowercased versions of tokens are the same
            assert og_sent[i][1].lower() == word.lower(), (
                f'token mismatch "{og_sent[i][1]}" != "{word}". Context =  {get_sentence_text(og_sent)}'
            )  # verify token

            # amend UPOS, update XPOS, and reconcile and update FEATS
            if deprel == 'aux':  # quick fix for sum/esse as aux
                upos = 'AUX'

            og_upos = og_sent[i][3]
            if og_upos != upos:
                og_sent[i][4] = normalize_xpos(upos, og_sent[i][4])
                og_sent[i][5] = feature_dict_to_string(normalize_features(upos, og_sent[i][5], featset))
                og_sent[i][3] = upos

            # update relations. If there is no data we fill with '_', which is not permitted
            # under CoNLLU standard, hence it will fail validation
            og_sent[i][6] = concordance.get(head, 0) if head else '_'  # assign HEAD
            og_sent[i][7] = deprel if deprel else '_'  # assign relation

            # extended dep rels
            new_deps = [(concordance.get(i[0], 0), i[1]) for i in deps] if deps else []
            if head and deprel:
                new_deps.append((concordance.get(head, 0), deprel))

            if new_deps:
                og_sent[i][8] = '|'.join([f'{i[0]}:{i[1]}' for i in sorted(new_deps, key=lambda x: int(x[0]))])
            else:
                og_sent[i][8] = '_'

        # add fixed lines to output
        sent_root = None
        for line in og_sent:
            # fix full stop dependencies if present
            if line[6] == 0:
                sent_root = line[0]

            if line[3] == 'PUNCT' and sent_root:
                line[6] = sent_root
                line[8] = f'{sent_root}:punct'
                sent_root = None

            conllu_output.append('\t'.join([str(i) for i in line]))

        conllu_output.append('')

    with open(f'{conllu_dir}/{output_filename}', 'w') as file:
        for line in conllu_output:
            file.write(f'{line}\n')

    with open(f'{input_dir}/brat_conllu_sentence_concordance.json', 'w') as file:
        file.write(json.dumps(sentence_concordance))
