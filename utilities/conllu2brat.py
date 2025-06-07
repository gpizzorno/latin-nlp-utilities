import codecs
from pathlib import Path

import regex as re  # https://pypi.org/project/regex/


# Based on https://github.com/nlplab/brat/blob/master/tools/conllXtostandoff.py
def conllu_to_brat(  # noqa: C901, PLR0915
    filename,
    output_directory,
    sents_per_doc=None,  # max number of sentences per output document, None = no splitting into documents
    output_root=True,  # whether to output an explicit root note
):
    """Convert a CONLLU formatted file to Brat's standoff format."""

    # functions
    def maptype(s):
        """Rewrite for characters in CoNLL-X types that cannot be directly used in identifiers in brat-flavored standoff."""
        charmap = {
            '<': '_lt_',
            '>': '_gt_',
            '+': '_plus_',
            '?': '_question_',
            '&': '_amp_',
            ':': '_',
            '.': '_period_',
            '!': '_exclamation_',
        }
        return ''.join([charmap.get(c, c) for c in s])

    def tokstr(start, end, ttype, idnum, text):
        # sanity checks
        assert '\n' not in text, f'ERROR: newline in entity "{text}"'
        assert text == text.strip(), f'ERROR: tagged span contains extra whitespace: "{text}"'
        return f'T{idnum}\t{maptype(ttype)} {start} {end}\t{text}'

    def depstr(depid, headid, rel, idnum):
        return f'R{idnum}\t{maptype(rel)} Arg1:T{headid} Arg2:T{depid}'

    def output(filename, output_directory, sents_per_doc, output_root, docnum, sentences):  # noqa: PLR0913
        # add doc numbering if there is a sentence count limit,
        # implying multiple outputs per input
        fn_base = f'{Path(filename).name}-doc-{str(docnum).zfill(3)}' if sents_per_doc else Path(filename).name

        outfn = Path(output_directory) / fn_base
        with (
            codecs.open(f'{outfn}.txt', 'w', encoding='UTF-8') as txtout,
            codecs.open(f'{outfn}.ann', 'w', encoding='UTF-8') as soout,
        ):
            offset, idnum, ridnum = 0, 1, 1
            doctext = ''

            for si, sentence in enumerate(sentences):  # noqa: B007
                tokens, deps = sentence

            idmap = {}  # store mapping from per-sentence token sequence IDs to document-unique token IDs
            prev_form = None  # output tokens

            if output_root:
                tokens = [('0', 'ROOT', 'ROOT'), *tokens]  # add an explicit root node with seq ID 0 (zero)

            for ID, form, POS in tokens:  # noqa: N806
                if prev_form is not None:
                    doctext = doctext + ' '
                    offset += 1

                # output a token annotation
                print(tokstr(offset, offset + len(form), POS, idnum, form), file=soout)
                assert ID not in idmap, 'Error in data: dup ID'
                idmap[ID] = idnum
                idnum += 1

                doctext = doctext + form
                offset += len(form)

                prev_form = form

            # output dependencies
            for dep, head, rel in deps:
                # if root is not added, skip deps to the root (idx 0)
                if not output_root and head == '0':
                    continue

                print(depstr(idmap[dep], idmap[head], rel, ridnum), file=soout)
                ridnum += 1

            if si + 1 != len(sentences):
                doctext = f'{doctext}\n'
                offset += 1

        print(doctext, file=txtout)

    # main process
    docnum = 1
    sentences = []

    with codecs.open(filename, encoding='UTF-8') as file:
        tokens, deps = [], []
        lines = file.readlines()

        for line_no, line in enumerate(lines):
            line = line.strip()  # noqa: PLW2901

            if len(line) > 0 and line[0] == '#':  # igore lines starting with "#" as comments
                continue

            if re.match(r'^\s*$', line):
                # blank lines separate sentences
                if len(tokens) > 0:
                    sentences.append((tokens, deps))
                tokens, deps = [], []

                # limit sentences per output "document"
                if sents_per_doc and len(sentences) >= sents_per_doc:
                    output(filename, output_directory, sents_per_doc, output_root, docnum, sentences)
                    sentences = []
                    docnum += 1

                continue

            # Assume it's a normal line. The format is tab-separated with ten fields
            fields = line.split('\t')

            assert len(fields) == 10, f'Format error on line {line_no}: expected 10 fields, got {len(fields)}: {line}'  # noqa: PLR2004
            # ID, form, POS = fields[0], fields[1], fields[4]
            ID, form, POS = fields[0], fields[1], fields[3]  # use UPOS instead of XPOS  # noqa: N806
            head, rel = fields[6], fields[7]

            tokens.append((ID, form, POS))
            # allow value "_" for HEAD to indicate no dependency
            if head != '_':
                deps.append((ID, head, rel))

        # process leftovers, if any
        if len(tokens) > 0:
            sentences.append((tokens, deps))

        if len(sentences) > 0:
            output(filename, output_directory, sents_per_doc, output_root, docnum, sentences)
