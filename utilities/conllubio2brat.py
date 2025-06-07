"""Converts CONLL-U format files with IOB tags to Brat standoff format."""

import codecs
from pathlib import Path

import regex as re  # https://pypi.org/project/regex/


def conllubio_to_brat(filename, output_directory):  # noqa: C901, PLR0915
    """Convert a CONLL-formatted file with IOB tags into Brat's standoff format for annotation."""

    def quote(s):
        return s in ('"',)

    def space(t1, t2, quote_count=None):
        # Helper for reconstructing sentence text. Given the text of two
        # consecutive tokens, returns a heuristic estimate of whether a
        # space character should be placed between them.

        if re.match(r'^[\(]$', t1):
            return False
        if re.match(r'^[.,\)\?\!]$', t2):
            return False
        if quote(t1) and quote_count is not None and quote_count % 2 == 1:
            return False

        return not (quote(t2) and quote_count is not None and quote_count % 2 == 1)

    def tagstr(start, end, ttype, idnum, text):
        # sanity checks
        assert '\n' not in text, f'ERROR: newline in entity "{text}"'
        assert text == text.strip(), f'ERROR: tagged span contains extra whitespace: "{text}"'
        return f'T{idnum}\t{ttype} {start} {end}\t{text}'

    def output(filename, output_directory, docnum, sentences):
        outfn = Path(output_directory) / f'{Path(filename).name}-doc-{str(docnum).zfill(3)}'
        with (
            codecs.open(f'{outfn}.txt', 'w', encoding='UTF-8') as txtout,
            codecs.open(f'{outfn}.ann', 'w', encoding='UTF-8') as soout,
        ):
            offset, idnum = 0, 1
            doctext = ''

            for si, sentence in enumerate(sentences):
                prev_token = None
                curr_start, curr_type = None, None
                quote_count = 0

                for token, ttag, ttype in sentence:
                    if curr_type is not None and (ttag != 'I' or ttype != curr_type):
                        # a previously started tagged sequence does not
                        # continue into this position.
                        print(tagstr(curr_start, offset, curr_type, idnum, doctext[curr_start:offset]), file=soout)
                        idnum += 1
                        curr_start, curr_type = None, None

                    if prev_token is not None and space(prev_token, token, quote_count):
                        doctext = doctext + ' '
                        offset += 1

                    if curr_type is None and ttag != 'O':
                        # a new tagged sequence begins here
                        curr_start, curr_type = offset, ttype

                    doctext = doctext + token
                    offset += len(token)

                    if quote(token):
                        quote_count += 1

                    prev_token = token

                # leftovers?
                if curr_type is not None:
                    print(tagstr(curr_start, offset, curr_type, idnum, doctext[curr_start:offset]), file=soout)
                    idnum += 1

                if si + 1 != len(sentences):
                    doctext = doctext + '\n'
                    offset += 1

            print(doctext, file=txtout)

    # main process
    docnum = 1
    sentences = []

    with codecs.open(filename, encoding='UTF-8') as f:
        # store (token, BIO-tag, type) triples for sentence
        current = []
        lines = f.readlines()

        for line_no, line in enumerate(lines):
            line = line.strip()  # noqa: PLW2901

            if re.match(r'^\s*$', line):
                # blank lines separate sentences
                if len(current) > 0:
                    sentences.append(current)
                current = []
                continue
            if re.match(r'^===*\s+O\s*$', line) or re.match(r'^-DOCSTART-', line):
                # special character sequence separating documents
                if len(sentences) > 0:
                    output(filename, output_directory, docnum, sentences)
                sentences = []
                docnum += 1
                continue

            if (
                line_no + 2 < len(lines)
                and re.match(r'^\s*$', lines[line_no + 1])
                and re.match(r'^-+\s+O\s*$', lines[line_no + 2])
            ):
                # heuristic match for likely doc before current line
                if len(sentences) > 0:
                    output(filename, output_directory, docnum, sentences)
                sentences = []
                docnum += 1
                # go on to process current normally

            # format = word, POS and BIO tag separated by space
            m = re.match(r'^(\S+)\s\S+\s(\S+)$', line)
            assert m, f'Error parsing line {line_no + 1}: {line}'
            token, tag = m.groups()

            # parse tag
            m = re.match(r'^([BIO])((?:-[A-Za-z_]+)?)$', tag)
            assert m, f'ERROR: failed to parse tag "{tag}" in {line_no}'
            ttag, ttype = m.groups()
            if len(ttype) > 0 and ttype[0] == '-':
                ttype = ttype[1:]

            current.append((token, ttag, ttype))

        # process leftovers, if any
        if len(current) > 0:
            sentences.append(current)

        if len(sentences) > 0:
            output(filename, output_directory, docnum, sentences)
