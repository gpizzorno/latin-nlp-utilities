# Original code (2015) by Filip Ginter and Sampo Pyysalo.
# modified by Gabe Pizzorno (2021)
import json
import unicodedata
from importlib.resources import files
from pathlib import Path

import regex as re

THISDIR = Path(__file__).resolve().parent

# Constants for the column indices
ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC = range(10)
COLNAMES = ['ID', 'FORM', 'LEMMA', 'POS', 'XPOS', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']
TOKENSWSPACE = MISC + 1  # one extra constant
AUX = MISC + 2  # another extra constant
COP = MISC + 3  # another extra constant

UPOS_TAGS = [
    'ADJ',
    'ADP',
    'ADV',
    'AUX',
    'CCONJ',
    'DET',
    'INTJ',
    'NOUN',
    'NUM',
    'PART',
    'PRON',
    'PROPN',
    'PUNCT',
    'SCONJ',
    'SYM',
    'VERB',
    'X',
]

# Global variables:
curr_line = 0  # Current line in the input file
sentence_line = 0  # The line in the input file on which the current sentence starts
sentence_id = None  # The most recently read sentence id
line_of_first_empty_node = None
line_of_first_enhanced_orphan = None
error_counter = {}  # key: error type value: error count
# langspec files which you should warn about in case they are missing (can be deprel, edeprel, feat_val, tokens_w_space)
warn_on_missing_files = set()
warn_on_undoc_feats = (
    ''  # filled after reading docfeats.json; printed when an unknown feature is encountered in the data)
)
warn_on_undoc_deps = (
    ''  # filled after reading docdeps.json; printed when an unknown relation is encountered in the data
)
spaceafterno_in_effect = (
    False  # needed to check that no space after last word of sentence does not co-occur with new paragraph or document
)
featdata = {}  # key: language code (feature-value-UPOS data loaded from feats.json)
auxdata = {}  # key: language code (auxiliary/copula data loaded from data.json)
depreldata = {}  # key: language code (deprel data loaded from deprels.json)
sentence_mapid = {}
error_log = []
tree_counter = 0  # Counter for the number of trees processed


def warn(msg, error_type, testlevel=0, testid='some-test', lineno=True, nodelineno=0, nodeid=0):  # noqa: PLR0913
    """If lineno is True, print the number of the line last read from input.

    Note that once we have read a sentence, this is the number of the empty line
    after the sentence, hence we probably do not want to print it.
    If we still have an error that pertains to an individual node, and we know
    the number of the line where the node appears, we can supply it via
    nodelineno. Nonzero nodelineno means that lineno value is ignored.
    If lineno is False, print the number and starting line of the current tree.
    """
    global error_log, sentence_mapid, curr_line, sentence_line, sentence_id, error_counter, tree_counter  # noqa: PLW0602

    error_counter[error_type] = error_counter.get(error_type, 0) + 1
    order = 0

    alt_id = sentence_mapid.get(sentence_id, {}).get('alt_id') if sentence_mapid else 0
    order = sentence_mapid.get(sentence_id, {}).get('order') if sentence_mapid else 0

    if nodelineno:
        line_no = nodelineno
    elif lineno:
        line_no = curr_line
    else:
        line_no = sentence_line

    entry = {
        'alt_id': alt_id,
        'testlevel': testlevel,
        'error_type': error_type,
        'testid': testid,
        'msg': msg,
        'node_id': nodeid if nodeid else None,
        'line_no': line_no,
        'tree_counter': tree_counter or None,
    }

    error_log.append((sentence_id, order, testlevel, entry))


# Support functions
def is_whitespace(line):
    """Check if the line is empty or contains only whitespace characters."""
    return re.match(r'^\s+$', line)


def is_word(cols):
    """Check if the columns represent a word."""
    return re.match(r'^[1-9][0-9]*$', cols[ID])


def is_multiword_token(cols):
    """Check if the columns represent a multiword token."""
    return re.match(r'^[1-9][0-9]*-[1-9][0-9]*$', cols[ID])


def is_empty_node(cols):
    """Check if the columns represent an empty node."""
    return re.match(r'^[0-9]+\.[1-9][0-9]*$', cols[ID])


def parse_empty_node_id(cols):
    """Parse the ID of an empty node into a tuple (word_id, empty_id)."""
    m = re.match(r'^([0-9]+)\.([0-9]+)$', cols[ID])
    assert m, 'parse_empty_node_id with non-empty node'
    return m.groups()


def shorten(string):
    """Shorten a string to 25 characters, adding '...' if it exceeds that length."""
    return string if len(string) <= 25 else f'{string[:20]}[...]'  # noqa: PLR2004


def lspec2ud(deprel):
    """Convert a language-specific dependency relation to a universal dependency relation."""
    return deprel.split(':', 1)[0]


# Level 1 tests. Only CoNLL-U backbone. Values can be empty or non-UD.
sentid_re = re.compile(r'^# sent_id\s*=\s*(\S+)$')


def trees(inp, tag_sets, level, lang):  # noqa: C901, PLR0912, PLR0915
    """`inp` a file-like object yielding lines as unicode `tag_sets`, leve, and lang are needed for choosing the tests.

    This function does elementary checking of the input and yields one
    sentence at a time from the input stream.
    """
    global curr_line, sentence_line, sentence_id  # noqa: PLW0603
    comments = []  # List of comment lines to go with the current sentence
    lines = []  # List of token/word lines of the current sentence
    # In case of wrong number of columns check the remaining lines of the
    # sentence but do not yield the sentence for further processing.
    corrupted = False
    testlevel = 1
    testclass = 'Format'

    for line_counter, line in enumerate(inp):
        curr_line = line_counter + 1
        line = line.rstrip('\n')  # noqa: PLW2901
        if is_whitespace(line):
            testid = 'pseudo-empty-line'
            testmessage = 'Spurious line that appears empty but is not; there are whitespace characters.'
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)

            # We will pretend that the line terminates a sentence in order to avoid subsequent misleading error messages.
            if lines:
                if not corrupted:
                    yield comments, lines
                comments = []
                lines = []
                corrupted = False

        elif not line:  # empty line
            if lines:  # sentence done
                if not corrupted:
                    yield comments, lines
                comments = []
                lines = []
                corrupted = False
            else:
                testid = 'extra-empty-line'
                testmessage = 'Spurious empty line. Only one empty line is expected after every sentence.'
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

        elif line[0] == '#':
            # We will really validate sentence ids later. But now we want to remember everything that looks like a
            # sentence id and use it in the error messages. Line numbers themselves may not be sufficient if we
            # are reading multiple files from a pipe.
            match = sentid_re.match(line)

            if match:
                sentence_id = match.group(1)

            if not lines:  # before sentence
                comments.append(line)

            else:
                testid = 'misplaced-comment'
                testmessage = 'Spurious comment line. Comments are only allowed before a sentence.'
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

        elif line[0].isdigit():
            validate_unicode_normalization(line)
            if not lines:  # new sentence
                sentence_line = curr_line

            cols = line.split('\t')
            if len(cols) != 10:  # noqa: PLR2004
                testid = 'number-of-columns'
                testmessage = f'The line has {len(cols)} columns but 10 are expected. The contents of the columns will not be checked.'  # noqa: E501
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)
                corrupted = True

            # If there is an unexpected number of columns, do not test their contents. Maybe the contents belongs
            # to a different column. And we could see an exception if a column value is missing.
            else:
                lines.append(cols)
                validate_cols_level1(cols)
                if level > 1:
                    validate_cols(cols, tag_sets, level, lang)

        else:  # A line which is neither a comment nor a token/word, nor empty. That's bad!
            testid = 'invalid-line'
            testmessage = f"Spurious line: '{line}'. All non-empty lines should start with a digit or the # character."
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)

    if comments or lines:  # These should have been yielded on an empty line!
        testid = 'missing-empty-line'
        testmessage = 'Missing empty line after the last sentence.'
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)

        if not corrupted:
            yield comments, lines


# Tests applicable to a single row indpendently of the others
def validate_unicode_normalization(text):
    """Test letters composed of multiple Unicode characters.

    Tests for cases such as a base letter plus combining diacritics, ensures they conform to NFC normalization (canonical
    decomposition followed by canonical composition).
    """
    normalized_text = unicodedata.normalize('NFC', text)
    if text != normalized_text:
        # Find the first unmatched character and include it in the report.
        firsti = -1
        firstj = -1
        inpfirst = ''
        nfcfirst = ''
        tcols = text.split('\t')
        ncols = normalized_text.split('\t')
        for i in range(len(tcols)):
            for j in range(len(tcols[i])):
                if tcols[i][j] != ncols[i][j]:
                    firsti = i
                    firstj = j
                    inpfirst = unicodedata.name(tcols[i][j])
                    nfcfirst = unicodedata.name(ncols[i][j])
                    break

            if firsti >= 0:
                break

        testlevel = 1
        testclass = 'Unicode'
        testid = 'unicode-normalization'
        testmessage = (
            f'Unicode not normalized: {COLNAMES[firsti]}.character[{firstj}] is {inpfirst}, should be {nfcfirst}.'
        )
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)


whitespace_re = re.compile(r'.*\s', re.U)
whitespace2_re = re.compile(r'.*\s\s', re.U)


def validate_cols_level1(cols):  # noqa: C901
    """Perform tests that can run on a single line and pertain only to format, not to predefined sets of UD tags."""
    testlevel = 1
    testclass = 'Format'

    # Some whitespace may be permitted in FORM, LEMMA and MISC but not elsewhere.
    for col_idx in range(MISC + 1):
        if col_idx >= len(cols):
            break  # this has been already reported in trees()

        # Must never be empty
        if not cols[col_idx]:
            testid = 'empty-column'
            testmessage = f'Empty value in column {COLNAMES[col_idx]}.'
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)

        else:
            # Must never have leading/trailing whitespace
            if cols[col_idx][0].isspace():
                testid = 'leading-whitespace'
                testmessage = f'Leading whitespace not allowed in column {COLNAMES[col_idx]}.'
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

            if cols[col_idx][-1].isspace():
                testid = 'trailing-whitespace'
                testmessage = f'Trailing whitespace not allowed in column {COLNAMES[col_idx]}.'
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

            # Must never contain two consecutive whitespace characters
            if whitespace2_re.match(cols[col_idx]):
                testid = 'repeated-whitespace'
                testmessage = (
                    f'Two or more consecutive whitespace characters not allowed in column {COLNAMES[col_idx]}.'
                )
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

    # These columns must not have whitespace
    for col_idx in (ID, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS):
        if col_idx >= len(cols):
            break  # this has been already reported in trees()

        if whitespace_re.match(cols[col_idx]):
            testid = 'invalid-whitespace'
            testmessage = f"White space not allowed in column {COLNAMES[col_idx]}: '{cols[col_idx]}'."
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)

    # Check for the format of the ID value. (ID must not be empty.)
    if not (is_word(cols) or is_empty_node(cols) or is_multiword_token(cols)):
        testid = 'invalid-word-id'
        testmessage = f"Unexpected ID format '{cols[ID]}'."
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)


# Tests applicable to the whole tree
interval_re = re.compile(r'^([0-9]+)-([0-9]+)$', re.U)


def validate_ID_sequence(tree):  # noqa: C901, N802, PLR0912, PLR0915
    """Validate that the ID sequence is correctly formed.

    Besides issuing a warning if an error is found, it also returns False to
    the caller so it can avoid building a tree from corrupt ids.
    """
    ok = True
    testlevel = 1
    testclass = 'Format'
    words = []
    tokens = []
    current_word_id, next_empty_id = 0, 1

    for cols in tree:
        if not is_empty_node(cols):
            next_empty_id = 1  # reset sequence

        if is_word(cols):
            t_id = int(cols[ID])
            current_word_id = t_id
            words.append(t_id)

            # Not covered by the previous interval?
            if not (tokens and tokens[-1][0] <= t_id and tokens[-1][1] >= t_id):
                tokens.append((t_id, t_id))  # nope - let's make a default interval for it

        elif is_multiword_token(cols):
            match = interval_re.match(cols[ID])  # Check the interval against the regex

            if not match:  # This should not happen. The function is_multiword_token() would then not return True.
                testid = 'invalid-word-interval'
                testmessage = f"Spurious word interval definition: '{cols[ID]}'."
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)
                ok = False
                continue

            beg, end = int(match.group(1)), int(match.group(2))
            if not ((not words and beg >= 1) or (words and beg >= words[-1] + 1)):
                testid = 'misplaced-word-interval'
                testmessage = 'Multiword range not before its first word.'
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)
                ok = False
                continue

            tokens.append((beg, end))

        elif is_empty_node(cols):
            word_id, empty_id = (int(i) for i in parse_empty_node_id(cols))
            if word_id != current_word_id or empty_id != next_empty_id:
                testid = 'misplaced-empty-node'
                testmessage = f'Empty node id {cols[ID]}, expected {current_word_id}.{next_empty_id}'
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)
                ok = False

            next_empty_id += 1

    # Now let's do some basic sanity checks on the sequences
    wrdstrseq = ','.join(str(x) for x in words)
    expstrseq = ','.join(str(x) for x in range(1, len(words) + 1))  # Words should form a sequence 1, 2, ...

    if wrdstrseq != expstrseq:
        testid = 'word-id-sequence'
        testmessage = f"Words do not form a sequence. Got '{wrdstrseq}'. Expected '{expstrseq}'."
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)
        ok = False

    # Check elementary sanity of word intervals.
    # Remember that these are not just multi-word tokens. Here we have intervals even for single-word tokens (b = e)!
    for b, e in tokens:
        if e < b:  # end before beginning
            testid = 'reversed-word-interval'
            testmessage = f'Spurious token interval {b}-{e}'
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)
            ok = False
            continue

        if b < 1 or e > len(words):  # out of range
            testid = 'word-interval-out'
            testmessage = f'Spurious token interval {b}-{e} (out of range)'
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)
            ok = False
            continue

    return ok


def validate_token_ranges(tree):
    """Check that the word ranges for multiword tokens are valid."""
    testlevel = 1
    testclass = 'Format'
    covered = set()

    for cols in tree:
        if not is_multiword_token(cols):
            continue

        m = interval_re.match(cols[ID])
        if not m:  # This should not happen. The function is_multiword_token() would then not return True.
            testid = 'invalid-word-interval'
            testmessage = f"Spurious word interval definition: '{cols[ID]}'."
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)
            continue

        start, end = m.groups()
        try:
            start, end = int(start), int(end)

        except ValueError:
            msg = 'internal error'
            raise AssertionError(msg) from None  # RE should assure that this works

        if (
            not start < end
        ):  # # #!!! This was already tested above in validate_ID_sequence()! Should we remove it from there?
            testid = 'reversed-word-interval'
            testmessage = f'Spurious token interval {start}-{end}'
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)
            continue

        if covered & set(range(start, end + 1)):
            testid = 'overlapping-word-intervals'
            testmessage = f'Range overlaps with others: {cols[ID]}'
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)

        covered |= set(range(start, end + 1))


def validate_newlines(inp):
    """Check that the input uses only unix-style line endings."""
    if inp.newlines and inp.newlines != '\n':
        testlevel = 1
        testclass = 'Format'
        testid = 'non-unix-newline'
        testmessage = 'Only the unix-style LF line terminator is allowed.'
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)


# Level 2 tests. Tree structure, universal tags and deprels. Note that any well-formed Feature = Valid pair is allowed
# (because it could be language-specific) and any word form or lemma can contain spaces (because language-specific
# guidelines may permit it).


# Metadata tests
def validate_sent_id(comments, known_ids, lcode):
    """Validate the sent_id metadata in the comments of a CoNLL-U file."""
    testlevel = 2
    testclass = 'Metadata'
    matched = []

    for c in comments:
        match = sentid_re.match(c)

        if match:
            matched.append(match)

        elif c.startswith((' # sent_id', ' #sent_id')):
            testid = 'invalid-sent-id'
            testmessage = (
                f"Spurious sent_id line: '{c}' Should look like '# sent_id = xxxxx' where xxxxx is not whitespace. \
                              Forward slash reserved for special purposes."
            )
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)

    if not matched:
        testid = 'missing-sent-id'
        testmessage = 'Missing the sent_id attribute.'
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)

    elif len(matched) > 1:
        testid = 'multiple-sent-id'
        testmessage = 'Multiple sent_id attributes.'
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)

    else:
        # Uniqueness of sentence ids should be tested treebank-wide, not just file-wide.
        # For that to happen, all three files should be tested at once.
        sid = matched[0].group(1)
        if sid in known_ids:
            testid = 'non-unique-sent-id'
            testmessage = f"Non-unique sent_id attribute '{sid}'."
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)

        if sid.count('/') > 1 or (sid.count('/') == 1 and lcode not in {'ud', 'shopen'}):
            testid = 'slash-in-sent-id'
            testmessage = f"The forward slash is reserved for special use in parallel treebanks: '{sid}'"
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)

        known_ids.add(sid)


newdoc_re = re.compile(r'^#\s*newdoc(\s|$)')
newpar_re = re.compile(r'^#\s*newpar(\s|$)')
text_re = re.compile(r'^#\s*text\s* = \s*(.+)$')


def validate_text_meta(comments, tree, check_space_after):  # noqa: C901, PLR0912, PLR0915
    """Validate the text, newdoc and newpar metadata in the comments of a CoNLL-U file."""
    # Remember if SpaceAfter=No applies to the last word of the sentence.
    # This is not prohibited in general but it is prohibited at the end of a paragraph or document.
    global spaceafterno_in_effect  # noqa: PLW0603
    testlevel = 2
    testclass = 'Metadata'
    newdoc_matched = []
    newpar_matched = []
    text_matched = []

    for c in comments:
        newdoc_match = newdoc_re.match(c)

        if newdoc_match:
            newdoc_matched.append(newdoc_match)

        newpar_match = newpar_re.match(c)
        if newpar_match:
            newpar_matched.append(newpar_match)

        text_match = text_re.match(c)
        if text_match:
            text_matched.append(text_match)

    if len(newdoc_matched) > 1:
        testid = 'multiple-newdoc'
        testmessage = 'Multiple newdoc attributes.'
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)

    if len(newpar_matched) > 1:
        testid = 'multiple-newpar'
        testmessage = 'Multiple newpar attributes.'
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)

    if (newdoc_matched or newpar_matched) and spaceafterno_in_effect:
        testid = 'spaceafter-newdocpar'
        testmessage = (
            'New document or paragraph starts when the last token of the previous sentence says SpaceAfter=No.'
        )
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)

    if not text_matched:
        testid = 'missing-text'
        testmessage = 'Missing the text attribute.'
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)

    elif len(text_matched) > 1:
        testid = 'multiple-text'
        testmessage = 'Multiple text attributes.'
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)

    else:
        stext = text_matched[0].group(1)
        if stext[-1].isspace():
            testid = 'text-trailing-whitespace'
            testmessage = 'The text attribute must not end with whitespace.'
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)

        # Validate the text against the SpaceAfter attribute in MISC.
        skip_words = set()
        mismatch_reported = (
            0  # do not report multiple mismatches in the same sentence; they usually have the same cause
        )

        for cols in tree:
            if len(cols) <= MISC:
                # This error has been reported elsewhere but we cannot check MISC now.
                continue

            if 'NoSpaceAfter=Yes' in cols[MISC]:  # I leave this without the split("|") to catch all
                testid = 'nospaceafter-yes'
                testmessage = "'NoSpaceAfter=Yes' should be replaced with 'SpaceAfter=No'."
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

            if '.' in cols[ID]:  # empty node
                if 'SpaceAfter=No' in cols[MISC]:  # I leave this without the split("|") to catch all
                    testid = 'spaceafter-empty-node'
                    testmessage = "'SpaceAfter=No' cannot occur with empty nodes."
                    warn(testmessage, testclass, testlevel=testlevel, testid=testid)

                continue

            if '-' in cols[ID]:  # multi-word token
                beg, end = cols[ID].split('-')
                try:
                    begi, endi = int(beg), int(end)

                except ValueError:
                    # This error has been reported elsewhere.
                    begi, endi = 1, 0

                # If we see a multi-word token, add its words to an ignore-set - these will be skipped,
                # and also checked for absence of SpaceAfter=No
                for i in range(begi, endi + 1):
                    skip_words.add(str(i))

            elif cols[ID] in skip_words:
                if 'SpaceAfter=No' in cols[MISC]:
                    testid = 'spaceafter-mwt-node'
                    testmessage = "'SpaceAfter=No' cannot occur with words that are part of a multi-word token."
                    warn(testmessage, testclass, testlevel=testlevel, testid=testid)

                continue

            else:
                # Err, I guess we have nothing to do here. :)
                pass

            # So now we have either a multi-word token or a word which is also a token in its entirety.
            if not stext.startswith(cols[FORM]):
                if not mismatch_reported:
                    testid = 'text-form-mismatch'
                    testmessage = (
                        f"Mismatch between the text attribute and the FORM field. Form[{cols[ID]}] is '{cols[FORM]}' \
                                  but text is '{stext[: len(cols[FORM]) + 20]}...'"
                    )
                    warn(testmessage, testclass, testlevel=testlevel, testid=testid, lineno=False)
                    mismatch_reported = 1

            else:
                stext = stext[len(cols[FORM]) :]  # eat the form
                if 'SpaceAfter=No' in cols[MISC].split('|'):
                    spaceafterno_in_effect = True

                else:
                    spaceafterno_in_effect = False
                    if check_space_after and (stext) and not stext[0].isspace():
                        testid = 'missing-spaceafter'
                        testmessage = (
                            f"'SpaceAfter=No' is missing in the MISC field of node #{cols[ID]}",
                            f" because the text is '{shorten(cols[FORM] + stext)}'.",
                        )
                        warn(testmessage, testclass, testlevel=testlevel, testid=testid)

                    stext = stext.lstrip()

        if stext:
            testid = 'text-extra-chars'
            testmessage = (
                f"Extra characters at the end of the text attribute, not accounted for in the FORM fields: '{stext}'"
            )
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)


# Tests applicable to a single row indpendently of the others
def validate_cols(cols, tag_sets, level, lang):
    """Perform all tests that can run on a single line. Done as soon as the line is read, called from trees() if level>1."""
    if is_word(cols) or is_empty_node(cols):
        validate_character_constraints(cols)  # level 2
        validate_upos(cols, tag_sets)  # level 2
        validate_features(
            cols,
            tag_sets,
            level,
            lang,
        )  # level 2 and up (relevant code checks whether higher level is required)

    elif is_multiword_token(cols):
        validate_token_empty_vals(cols)

    # else do nothing; we have already reported wrong ID format at level 1
    if is_word(cols):
        validate_deprels(cols, tag_sets, level)  # level 2 and up

    elif is_empty_node(cols):
        validate_empty_node_empty_vals(cols)  # level 2

    if level > 3:  # noqa: PLR2004
        validate_whitespace(cols, tag_sets)  # level 4 (it is language-specific; to disallow everywhere, use --lang ud)


def validate_token_empty_vals(cols):
    """Check that a multi-word token has _ empty values in all fields except MISC.

    This is required by UD guidelines although it is not a problem in general,
    therefore a level 2 test.
    """
    assert is_multiword_token(cols), 'internal error'
    for col_idx in range(LEMMA, MISC):  # all columns except the first two (ID, FORM) and the last one (MISC)
        if cols[col_idx] != '_':
            testlevel = 2
            testclass = 'Format'
            testid = 'mwt-nonempty-field'
            testmessage = (
                f"A multi-word token line must have '_' in the column {COLNAMES[col_idx]}. Now: '{cols[col_idx]}'."
            )
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)


def validate_empty_node_empty_vals(cols):
    """Check that an empty node has _ empty values in HEAD and DEPREL.

    This is required by UD guidelines but not necessarily by CoNLL-U, therefore
    a level 2 test.
    """
    assert is_empty_node(cols), 'internal error'
    for col_idx in (HEAD, DEPREL):
        if cols[col_idx] != '_':
            testlevel = 2
            testclass = 'Format'
            testid = 'mwt-nonempty-field'
            testmessage = f"An empty node must have '_' in the column {COLNAMES[col_idx]}. Now: '{cols[col_idx]}'."
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)


# Ll ... lowercase Unicode letters
# Lm ... modifier Unicode letters (e.g., superscript h)
# Lo ... other Unicode letters (all caseless scripts, e.g., Arabic)
# M .... combining diacritical marks
# Underscore is allowed between letters but not at beginning, end, or next to another underscore.
edeprelpart_resrc = r'[\p{Ll}\p{Lm}\p{Lo}\p{M}]+(_[\p{Ll}\p{Lm}\p{Lo}\p{M}]+)*'
# There must be always the universal part, consisting only of ASCII letters.
# There can be up to three additional, colon-separated parts: subtype, preposition and case.
# One of them, the preposition, may contain Unicode letters. We do not know which one it is
# (only if there are all four parts, we know it is the third one).
# ^[a-z]+(:[a-z]+)?(:[\p{Ll}\p{Lm}\p{Lo}\p{M}]+(_[\p{Ll}\p{Lm}\p{Lo}\p{M}]+)*)?(:[a-z]+)?$
edeprel_resrc = rf'^[a-z]+(:[a-z]+)?(:{edeprelpart_resrc})?(:[a-z]+)?$'
edeprel_re = re.compile(edeprel_resrc, re.U)


def validate_character_constraints(cols):
    """Check general constraints on valid characters, e.g. that UPOS only contains [A-Z]."""
    testlevel = 2

    if is_multiword_token(cols):
        return

    if len(cols) <= UPOS:
        return  # this has been already reported in trees()

    if not (re.match(r'^[A-Z]+$', cols[UPOS]) or (is_empty_node(cols) and cols[UPOS] == '_')):
        testclass = 'Morpho'
        testid = 'invalid-upos'
        testmessage = f"Invalid UPOS value '{cols[UPOS]}'."
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)

    if not (re.match(r'^[a-z]+(:[a-z]+)?$', cols[DEPREL]) or (is_empty_node(cols) and cols[DEPREL] == '_')):
        testclass = 'Syntax'
        testid = 'invalid-deprel'
        testmessage = f"Invalid DEPREL value '{cols[DEPREL]}'."
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)

    try:
        deps = deps_list(cols)  # noqa: F841

    except ValueError:
        testclass = 'Enhanced'
        testid = 'invalid-deps'
        testmessage = f"Failed to parse DEPS: '{cols[DEPS]}'."
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)
        return

    if any(deprel for head, deprel in deps_list(cols) if not edeprel_re.match(deprel)):
        testclass = 'Enhanced'
        testid = 'invalid-edeprel'
        testmessage = f"Invalid enhanced relation type: '{cols[DEPS]}'."
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)


attr_val_re = re.compile(
    r'^([A-Z][A-Za-z0-9]*(?:\[[a-z0-9]+\])?)=(([A-Z0-9][A-Z0-9a-z]*)(,([A-Z0-9][A-Z0-9a-z]*))*)$',
    re.U,
)
val_re = re.compile(r'^[A-Z0-9][A-Za-z0-9]*', re.U)


def validate_features(cols, tag_sets, level, lang):  # noqa: C901, PLR0912, PLR0915
    """Check general constraints on feature-value format.

    On level 4 and higher,
    also checks that a feature-value pair is listed as approved. (Every pair
    must be allowed on level 2 because it could be defined as language-specific.
    To disallow non-universal features, test on level 4 with language 'ud'.)
    """
    global warn_on_undoc_feats  # noqa: PLW0603
    testclass = 'Morpho'

    if len(cols) <= FEATS:
        return None  # this has been already reported in trees()

    feats = cols[FEATS]
    if feats == '_':
        return True

    # List of permited features is language-specific.
    # The current token may be in a different language due to code switching.
    featset = tag_sets[FEATS]
    altlang = get_alt_language(cols[MISC])

    if altlang:
        lang = altlang
        featset = get_featdata_for_language(altlang)

    feat_list = feats.split('|')
    if [f.lower() for f in feat_list] != sorted(f.lower() for f in feat_list):
        testlevel = 2
        testid = 'unsorted-features'
        testmessage = f"Morphological features must be sorted: '{feats}'."
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)

    attr_set = set()  # I'll gather the set of features here to check later that none is repeated.
    for f in feat_list:
        match = attr_val_re.match(f)
        if match is None:
            testlevel = 2
            testid = 'invalid-feature'
            testmessage = (
                f"Spurious morphological feature: '{f}'.",
                'Should be of the form Feature=Value and must start with [A-Z] and only contain [A-Za-z0-9].',
            )
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)
            attr_set.add(f)  # to prevent misleading error "Repeated features are disallowed"

        else:
            # Check that the values are sorted as well
            attr = match.group(1)
            attr_set.add(attr)
            values = match.group(2).split(',')

            if len(values) != len(set(values)):
                testlevel = 2
                testid = 'repeated-feature-value'
                testmessage = f"Repeated feature values are disallowed: '{feats}'"
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

            if [v.lower() for v in values] != sorted(v.lower() for v in values):
                testlevel = 2
                testid = 'unsorted-feature-values'
                testmessage = f"If a feature has multiple values, these must be sorted: '{f}'"
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

            for v in values:
                if not val_re.match(v):
                    testlevel = 2
                    testid = 'invalid-feature-value'
                    testmessage = (
                        f"Spurious value '{v}' in '{f}'. Must start with [A-Z0-9] and only contain [A-Za-z0-9]."
                    )
                    warn(testmessage, testclass, testlevel=testlevel, testid=testid)

                # Level 2 tests character properties and canonical order but not that the f-v pair is known.
                # Level 4 also checks whether the feature value is on the list.
                # If only universal feature-value pairs are allowed, test on level 4 with lang = 'ud'.
                if level > 3 and featset is not None:  # noqa: PLR2004
                    testlevel = 4
                    # The featset is no longer a simple set of feature-value pairs.
                    # It is a complex database that we read from feats.json.

                    if attr not in featset:
                        testid = 'feature-unknown'
                        testmessage = f'Feature {attr} is not documented for language [{lang}].'

                        if not altlang and len(warn_on_undoc_feats) > 0:
                            # If some features were excluded because they are not documented,
                            # tell the user when the first unknown feature is encountered in the data.
                            # Then erase this (long) introductory message and do not repeat it with
                            # other instances of unknown features.
                            testmessage += f'\n\n{warn_on_undoc_feats}'
                            warn_on_undoc_feats = ''

                        warn(testmessage, testclass, testlevel=testlevel, testid=testid)

                    else:
                        lfrecord = featset[attr]
                        if lfrecord['permitted'] == 0:
                            testid = 'feature-not-permitted'
                            testmessage = f'Feature {attr} is not permitted in language [{lang}].'

                            if not altlang and len(warn_on_undoc_feats) > 0:
                                testmessage += f'\n\n{warn_on_undoc_feats}'
                                warn_on_undoc_feats = ''

                            warn(testmessage, testclass, testlevel=testlevel, testid=testid)

                        else:
                            values = (
                                lfrecord['uvalues']
                                + lfrecord['lvalues']
                                + lfrecord['unused_uvalues']
                                + lfrecord['unused_lvalues']
                            )
                            if v not in values:
                                testid = 'feature-value-unknown'
                                testmessage = f'Value {v} is not documented for feature {attr} in language [{lang}].'

                                if not altlang and len(warn_on_undoc_feats) > 0:
                                    testmessage += f'\n\n{warn_on_undoc_feats}'
                                    warn_on_undoc_feats = ''

                                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

                            elif cols[UPOS] not in lfrecord['byupos']:
                                testid = 'feature-upos-not-permitted'
                                testmessage = (
                                    f'Feature {attr} is not permitted with UPOS {cols[UPOS]} in language [{lang}].'
                                )

                                if not altlang and len(warn_on_undoc_feats) > 0:
                                    testmessage += f'\n\n{warn_on_undoc_feats}'
                                    warn_on_undoc_feats = ''

                                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

                            elif v not in lfrecord['byupos'][cols[UPOS]] or lfrecord['byupos'][cols[UPOS]][v] == 0:
                                testid = 'feature-value-upos-not-permitted'
                                testmessage = (
                                    f'Value {v} of feature {attr} is not permitted',
                                    f' with UPOS {cols[UPOS]} in language [{lang}].',
                                )

                                if not altlang and len(warn_on_undoc_feats) > 0:
                                    testmessage += f'\n\n{warn_on_undoc_feats}'
                                    warn_on_undoc_feats = ''

                                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

    if len(attr_set) != len(feat_list):
        testlevel = 2
        testid = 'repeated-feature'
        testmessage = f"Repeated features are disallowed: '{feats}'."
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)
        return None
    return None


def validate_upos(cols, tag_sets):
    """Check that the UPOS tag is valid and known."""
    if len(cols) <= UPOS:
        return  # this has been already reported in trees()

    if is_empty_node(cols) and cols[UPOS] == '_':
        return

    if tag_sets[UPOS] is not None and cols[UPOS] not in tag_sets[UPOS]:
        testlevel = 2
        testclass = 'Morpho'
        testid = 'unknown-upos'
        testmessage = "Unknown UPOS tag: '{cols[UPOS]}'."
        warn(testmessage, testclass, testlevel=testlevel, testid=testid)


def validate_deprels(cols, tag_sets, level):  # noqa: C901
    """Check that the DEPREL tag is valid and known."""
    global warn_on_undoc_deps  # noqa: PLW0603
    if len(cols) <= DEPREL:
        return  # this has been already reported in trees()

    # List of permited relations is language-specific.
    # The current token may be in a different language due to code switching.
    deprelset = tag_sets[DEPREL]
    # # #!!! Unlike with features and auxiliaries, with deprels it is less clear
    # # #!!! whether we actually want to switch the set of labels when the token
    # # #!!! belongs to another language. If the set is changed at all, then it
    # # #!!! should be a union of the main language and the token language.
    # # #!!! Otherwise we risk that, e.g., we have allowed 'flat:name' for our
    # # #!!! language, the maintainers of the other language have not allowed it,
    # # #!!! and then we could not use it when the foreign language is active.
    # # #!!! (This has actually happened in French GSD.)
    altlang = None
    # altlang = get_alt_language(cols[MISC])
    # if altlang:
    #    deprelset = get_depreldata_for_language(altlang)
    # Test only the universal part if testing at universal level.
    deprel = cols[DEPREL]
    testlevel = 4

    if level < 4:  # noqa: PLR2004
        deprel = lspec2ud(deprel)
        testlevel = 2

    if deprelset is not None and deprel not in deprelset:
        testclass = 'Syntax'
        testid = 'unknown-deprel'
        # If some relations were excluded because they are not documented,
        # tell the user when the first unknown relation is encountered in the data.
        # Then erase this (long) introductory message and do not repeat it with
        # other instances of unknown relations.
        testmessage = f"Unknown DEPREL label: '{cols[DEPREL]}'"

        if not altlang and len(warn_on_undoc_deps) > 0:
            testmessage += f'\n\n{warn_on_undoc_deps}'
            warn_on_undoc_deps = ''

        warn(testmessage, testclass, testlevel=testlevel, testid=testid)

    if len(cols) <= DEPS:
        return  # this has been already reported in trees()

    if tag_sets.get(DEPS) is not None and cols[DEPS] != '_':
        for head_deprel in cols[DEPS].split('|'):
            try:
                head, deprel = head_deprel.split(':', 1)

            except ValueError:
                testclass = 'Enhanced'
                testid = 'invalid-head-deprel'  # but it would have probably triggered another error above
                testmessage = f"Malformed head:deprel pair '{head_deprel}'."
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)
                continue

            if level < 4:  # noqa: PLR2004
                deprel = lspec2ud(deprel)

            if deprel not in tag_sets[DEPS]:
                warn_on_missing_files.add('edeprel')
                testclass = 'Enhanced'
                testid = 'unknown-edeprel'
                testmessage = f"Unknown enhanced relation type '{deprel}' in '{head_deprel}'"
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)


# Tests applicable to the whole sentence
def subset_to_words_and_empty_nodes(tree):
    """Only picks word and empty node lines, skips multiword token lines."""
    return [cols for cols in tree if is_word(cols) or is_empty_node(cols)]


def deps_list(cols):
    """Parse the DEPS column into a list of (head, deprel) pairs."""
    if len(cols) <= DEPS:
        return None  # this has been already reported in trees()

    deps = [] if cols[DEPS] == '_' else [hd.split(':', 1) for hd in cols[DEPS].split('|')]

    if any(hd for hd in deps if len(hd) != 2):  # noqa: PLR2004
        msg = f'malformed DEPS: {cols[DEPS]}'
        raise ValueError(msg)

    return deps


basic_head_re = re.compile(r'^(0|[1-9][0-9]*)$', re.U)
enhanced_head_re = re.compile(r'^(0|[1-9][0-9]*)(\.[1-9][0-9]*)?$', re.U)


def validate_id_references(tree):  # noqa: C901
    """Validate that HEAD and DEPS reference existing IDs."""
    testlevel = 2
    word_tree = subset_to_words_and_empty_nodes(tree)
    ids = {cols[ID] for cols in word_tree}

    for cols in word_tree:
        if len(cols) <= HEAD:
            return  # this has been already reported in trees()

        # Test the basic HEAD only for non-empty nodes.
        # We have checked elsewhere that it is empty for empty nodes.
        if not is_empty_node(cols):
            match = basic_head_re.match(cols[HEAD])
            if match is None:
                testclass = 'Format'
                testid = 'invalid-head'
                testmessage = f"Invalid HEAD: '{cols[HEAD]}'."
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

            if not (cols[HEAD] in ids or cols[HEAD] == '0'):
                testclass = 'Syntax'
                testid = 'unknown-head'
                testmessage = f"Undefined HEAD (no such ID): '{cols[HEAD]}'."
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

        if len(cols) <= DEPS:
            return  # this has been already reported in trees()

        try:
            deps = deps_list(cols)
        except ValueError:
            # Similar errors have probably been reported earlier.
            testclass = 'Format'
            testid = 'invalid-deps'
            testmessage = f"Failed to parse DEPS: '{cols[DEPS]}'."
            warn(testmessage, testclass, testlevel=testlevel, testid=testid)
            continue

        for head, _deprel in deps:
            match = enhanced_head_re.match(head)
            if match is None:
                testclass = 'Format'
                testid = 'invalid-ehead'
                testmessage = f"Invalid enhanced head reference: '{head}'."
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

            if not (head in ids or head == '0'):
                testclass = 'Enhanced'
                testid = 'unknown-ehead'
                testmessage = f"Undefined enhanced head reference (no such ID): '{head}'."
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)


def validate_root(tree):  # noqa: C901
    """Check that DEPREL is "root" iff HEAD is 0."""
    testlevel = 2
    for cols in tree:
        if is_word(cols):
            if len(cols) <= HEAD:
                continue  # this has been already reported in trees()

            if cols[HEAD] == '0' and lspec2ud(cols[DEPREL]) != 'root':
                testclass = 'Syntax'
                testid = '0-is-not-root'
                testmessage = "DEPREL must be 'root' if HEAD is 0."
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

            if cols[HEAD] != '0' and lspec2ud(cols[DEPREL]) == 'root':
                testclass = 'Syntax'
                testid = 'root-is-not-0'
                testmessage = "DEPREL cannot be 'root' if HEAD is not 0."
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

        if is_word(cols) or is_empty_node(cols):
            if len(cols) <= DEPS:
                continue  # this has been already reported in trees()

            try:
                deps = deps_list(cols)
            except ValueError:
                # Similar errors have probably been reported earlier.
                testclass = 'Format'
                testid = 'invalid-deps'
                testmessage = f"Failed to parse DEPS: '{cols[DEPS]}'."
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)

                continue

            for head, deprel in deps:
                if head == '0' and lspec2ud(deprel) != 'root':
                    testclass = 'Enhanced'
                    testid = 'enhanced-0-is-not-root'
                    testmessage = "Enhanced relation type must be 'root' if head is 0."
                    warn(testmessage, testclass, testlevel=testlevel, testid=testid)

                if head != '0' and lspec2ud(deprel) == 'root':
                    testclass = 'Enhanced'
                    testid = 'enhanced-root-is-not-0'
                    testmessage = "Enhanced relation type cannot be 'root' if head is not 0."
                    warn(testmessage, testclass, testlevel=testlevel, testid=testid)


def validate_deps(tree):  # noqa: C901
    """Validate that DEPS is correctly formatted and that there are no self-loops in DEPS."""
    testlevel = 2
    node_line = sentence_line - 1
    for cols in tree:
        node_line += 1
        if not (is_word(cols) or is_empty_node(cols)):
            continue

        if len(cols) <= DEPS:
            continue  # this has been already reported in trees()

        try:
            deps = deps_list(cols)
            heads = [float(h) for h, d in deps]

        except ValueError:
            # Similar errors have probably been reported earlier.
            testclass = 'Format'
            testid = 'invalid-deps'
            testmessage = f"Failed to parse DEPS: '{cols[DEPS]}'."
            warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodelineno=node_line)

            return

        if heads != sorted(heads):
            testclass = 'Format'
            testid = 'unsorted-deps'
            testmessage = f"DEPS not sorted by head index: '{cols[DEPS]}'"
            warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodelineno=node_line)

        else:
            lasth = None
            lastd = None
            for h, d in deps:
                if h == lasth:
                    if d < lastd:
                        testclass = 'Format'
                        testid = 'unsorted-deps-2'
                        testmessage = f"DEPS pointing to head '{h}' not sorted by relation type: '{cols[DEPS]}'"
                        warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodelineno=node_line)

                    elif d == lastd:
                        testclass = 'Format'
                        testid = 'repeated-deps'
                        testmessage = f"DEPS contain multiple instances of the same relation '{h}:{d}'"
                        warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodelineno=node_line)

                lasth = h
                lastd = d
                # # #!!! This is now also tested above in validate_root(). We must reorganize testing of the enhanced structure
                # so that the same thing is not tested multiple times.
                # Like in the basic representation, head 0 implies relation root and vice versa.
                # Note that the enhanced graph may have multiple roots (coordination of predicates).
                # ud = lspec2ud(d)
                # if h == '0' and ud != 'root':
                #  warn("Illegal relation '%s:%s' in DEPS: must be 'root' if head is 0" % (h, d), 'Format', nodelineno=node_line)
                # if ud == 'root' and h != '0':
                #  warn("Illegal relation '%s:%s' in DEPS: cannot be 'root' if head is not 0" % (h, d),
                # 'Format', nodelineno=node_line)

        try:
            id_ = float(cols[ID])
        except ValueError:
            # This error has been reported previously.
            return

        if id_ in heads:
            testclass = 'Enhanced'
            testid = 'deps-self-loop'
            testmessage = f"Self-loop in DEPS for '{cols[ID]}'"
            warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodelineno=node_line)


def validate_misc(tree):
    """Validate MISC column.

    In general, the MISC column can contain almost anything. However, if there
    is a vertical bar character, it is interpreted as the separator of two
    MISC attributes, which may or may not have the form of attribute = value pair.
    In general it is not forbidden that the same attribute appears several times
    with different values, but this should not happen for selected attributes
    that are described in the UD documentation.
    """
    testlevel = 2
    testclass = 'Format'
    node_line = sentence_line - 1
    for cols in tree:
        node_line += 1

        if not (is_word(cols) or is_empty_node(cols)):
            continue

        if len(cols) <= MISC:
            continue  # this has been already reported in trees()

        if cols[MISC] == '_':
            continue

        misc = [ma.split('=', 1) for ma in cols[MISC].split('|')]
        mamap = {}
        for ma in misc:
            if re.match(r'^(SpaceAfter|Lang|Translit|LTranslit|Gloss|LId|LDeriv)$', ma[0]):
                mamap.setdefault(ma[0], 0)
                mamap[ma[0]] = mamap[ma[0]] + 1

        for a in list(mamap):
            if mamap[a] > 1:
                testid = 'repeated-misc'
                testmessage = f"MISC attribute '{a}' not supposed to occur twice"
                warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodelineno=node_line)


def build_tree(sentence, single_root):  # noqa: PLR0911
    """Build a tree structure from the sentence.

    Takes the list of non-comment lines (line = list of columns) describing
    a sentence. Returns a dictionary with items providing easier access to the
    tree structure. In case of fatal problems (missing HEAD etc.) returns None
    but does not report the error (presumably it has already been reported).

    tree ... dictionary:
      nodes ... array of word lines, i.e., lists of columns;
          mwt and empty nodes are skipped, indices equal to ids (nodes[0] is empty)
      children ... array of sets of children indices (numbers, not strings);
          indices to this array equal to ids (children[0] are the children of the root)
      linenos ... array of line numbers in the file, corresponding to nodes
          (needed in error messages)
    """
    testlevel = 2
    testclass = 'Syntax'
    global sentence_line  # the line of the first token/word of the current tree (skipping comments!)  # noqa: PLW0602
    node_line = sentence_line - 1
    children = {}  # node -> set of children
    tree = {
        'nodes': [['0', '_', '_', '_', '_', '_', '_', '_', '_', '_']],  # add artificial node 0
        'children': [],
        'linenos': [sentence_line],  # for node 0
    }

    for cols in sentence:
        node_line += 1

        if not is_word(cols):
            continue

        # Even MISC may be needed when checking the annotation guidelines
        # (for instance, SpaceAfter=No must not occur inside a goeswith span).
        if len(cols) <= MISC:
            # This error has been reported on lower levels, do not report it here.
            # Do not continue to check annotation if there are elementary flaws.
            return None

        try:
            id_ = int(cols[ID])
        except ValueError:
            # This error has been reported on lower levels, do not report it here.
            # Do not continue to check annotation if there are elementary flaws.
            return None

        try:
            head = int(cols[HEAD])
        except ValueError:
            # This error has been reported on lower levels, do not report it here.
            # Do not continue to check annotation if there are elementary flaws.
            return None

        if head == id_:
            testid = 'head-self-loop'
            testmessage = f'HEAD==ID for {cols[ID]}'
            warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodelineno=node_line)
            return None

        tree['nodes'].append(cols)
        tree['linenos'].append(node_line)
        children.setdefault(cols[HEAD], set()).add(id_)  # Incrementally build the set of children of every node.

    for cols in tree['nodes']:
        tree['children'].append(sorted(children.get(cols[ID], [])))

    # Check that there is just one node with the root relation.
    if len(tree['children'][0]) > 1 and single_root:
        testid = 'multiple-roots'
        testmessage = f'Multiple root words: {tree["children"][0]}'
        warn(testmessage, testclass, testlevel=testlevel, testid=testid, lineno=False)
        return None

    # Return None if there are any cycles. Avoid surprises when working with the graph.
    # Presence of cycles is equivalent to presence of unreachable nodes.
    projection = set()
    get_projection(0, tree, projection)
    unreachable = set(range(1, len(tree['nodes']) - 1)) - projection
    if unreachable:
        testid = 'non-tree'
        testmessage = (
            f'Non-tree structure. Words {", ".join([str(w) for w in sorted(unreachable)])}',
            ' are not reachable from the root 0.',
        )
        warn(testmessage, testclass, testlevel=testlevel, testid=testid, lineno=False)
        return None

    return tree


def get_projection(id, tree, projection):  # noqa: A002
    """Collect node ids in the set called projection.

    Like proj() above, but works with the tree data structure.
    """
    for child in tree['children'][id]:
        if child in projection:
            continue  # cycle is or will be reported elsewhere

        projection.add(child)
        get_projection(child, tree, projection)

    return projection


def build_egraph(sentence):
    """Build an enhanced graph from the sentence.

    Takes the list of non-comment lines (line = list of columns) describing
    a sentence. Returns a dictionary with items providing easier access to the
    enhanced graph structure. In case of fatal problems returns None
    but does not report the error (presumably it has already been reported).
    However, once the graph has been found and built, this function verifies
    that the graph is connected and generates an error if it is not.

    egraph ... dictionary:
      nodes ... dictionary of dictionaries, each corresponding to a word or an empty node; mwt lines are skipped
          keys equal to node ids (i.e. strings that look like integers or decimal numbers; key 0 is the artificial root node)
          value is a dictionary-record:
              cols ... array of column values from the input line corresponding to the node
              children ... set of children ids (strings)
              lineno ... line number in the file (needed in error messages)
    """
    global sentence_line  # the line of the first token/word of the current tree (skipping comments!)  # noqa: PLW0602
    node_line = sentence_line - 1
    egraph_exists = False  # enhanced deps are optional
    rootnode = {
        'cols': ['0', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
        'deps': [],
        'parents': set(),
        'children': set(),
        'lineno': sentence_line,
    }
    egraph = {'0': rootnode}  # structure described above
    nodeids = set()

    for cols in sentence:
        node_line += 1

        if is_multiword_token(cols):
            continue

        if len(cols) <= MISC:
            # This error has been reported on lower levels, do not report it here.
            # Do not continue to check annotation if there are elementary flaws.
            return None

        try:
            deps = deps_list(cols)
            heads = [h for h, d in deps]
        except ValueError:
            # This error has been reported on lower levels, do not report it here.
            # Do not continue to check annotation if there are elementary flaws.
            return None

        if is_empty_node(cols):
            egraph_exists = True

        nodeids.add(cols[ID])
        # The graph may already contain a record for the current node if one of
        # the previous nodes is its child. If it doesn't, we will create it now.
        egraph.setdefault(cols[ID], {})
        egraph[cols[ID]]['cols'] = cols
        egraph[cols[ID]]['deps'] = deps_list(cols)
        egraph[cols[ID]]['parents'] = {h for h, d in deps}
        egraph[cols[ID]].setdefault('children', set())
        egraph[cols[ID]]['lineno'] = node_line

        # Incrementally build the set of children of every node.
        for h in heads:
            egraph_exists = True
            egraph.setdefault(h, {})
            egraph[h].setdefault('children', set()).add(cols[ID])

    # We are currently testing the existence of enhanced graphs separately for each sentence.
    # It is thus possible to have one sentence with connected egraph and another without enhanced dependencies.
    if not egraph_exists:
        return None

    # Check that the graph is connected. The UD v2 guidelines do not license unconnected graphs.
    # Compute projection of every node. Beware of cycles.
    projection = set()
    get_graph_projection('0', egraph, projection)
    unreachable = nodeids - projection

    if unreachable:
        sur = sorted(unreachable)
        testlevel = 2
        testclass = 'Enhanced'
        testid = 'unconnected-egraph'
        testmessage = f'Enhanced graph is not connected. Nodes {sur} are not reachable from any root'
        warn(testmessage, testclass, testlevel=testlevel, testid=testid, lineno=False)
        return None

    return egraph


def get_graph_projection(id, graph, projection):  # noqa: A002
    """Collect node ids in the set called projection.

    Like proj() above, but works with the enhanced graph data structure.
    """
    for child in graph[id]['children']:
        if child in projection:
            continue  # skip cycles

        projection.add(child)
        get_graph_projection(child, graph, projection)

    return projection


# Level 3 tests. Annotation content vs. the guidelines (only universal tests).
def validate_upos_vs_deprel(id, tree):  # noqa: A002, C901
    """Check that the dependent word belongs to an expected part-of-speech category.

    Occasionally we may have to check the children of the node, too.
    """
    testlevel = 3
    testclass = 'Syntax'
    cols = tree['nodes'][id]
    # This is a level 3 test, we will check only the universal part of the relation.
    deprel = lspec2ud(cols[DEPREL])
    childrels = {lspec2ud(tree['nodes'][x][DEPREL]) for x in tree['children'][id]}

    # Certain relations are reserved for nominals and cannot be used for verbs.
    # Nevertheless, they can appear with adjectives or adpositions if they are promoted due to ellipsis.
    # Unfortunately, we cannot enforce this test because a word can be cited
    # rather than used, and then it can take a nominal function even if it is
    # a verb, as in this Upper Sorbian sentence where infinitives are appositions:
    # [hsb] Z werba danci "rejować" móže substantiw nastać danco "reja", adjektiw danca "rejowanski" a adwerb dance "rejowansce",
    # ale tež z substantiwa martelo "hamor" móže nastać werb marteli "klepać z hamorom", adjektiw martela "hamorowy"
    # a adwerb martele "z hamorom".
    # if re.match(r"^(nsubj|obj|iobj|obl|vocative|expl|dislocated|nmod|appos)", deprel) and
    # re.match(r"^(VERB|AUX|ADV|SCONJ|CCONJ)", cols[UPOS]):
    #    warn("Node %s: '%s' should be a nominal but it is '%s'" % (cols[ID], deprel, cols[UPOS]), 'Syntax', lineno = False)
    # Determiner can alternate with a pronoun.
    if deprel == 'det' and not re.match(r'^(DET|PRON)', cols[UPOS]) and 'fixed' not in childrels:
        testid = 'rel-upos-det'
        testmessage = f"'det' should be 'DET' or 'PRON' but it is '{cols[UPOS]}'"
        warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])

    # Nummod is for "number phrases" only. This could be interpreted as NUM only,
    # but some languages treat some cardinal numbers as NOUNs, and in
    # https://github.com/UniversalDependencies/docs/issues/596,
    # we concluded that the validator will tolerate them.
    if deprel == 'nummod' and not re.match(r'^(NUM|NOUN|SYM)$', cols[UPOS]):
        testid = 'rel-upos-nummod'
        testmessage = f"'nummod' should be 'NUM' but it is '{cols[UPOS]}'"
        warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])

    # Advmod is for adverbs, perhaps particles but not for prepositional phrases or clauses.
    # Nevertheless, we should allow adjectives because they can be used as adverbs in some languages.
    # https://github.com/UniversalDependencies/docs/issues/617 #issuecomment-488261396
    # Bohdan reports that some DET can modify adjectives in a way similar to ADV.
    # I am not sure whether advmod is the best relation for them but the alternative det is not much better, so maybe we should
    # not enforce it. Adding DET to the tolerated UPOS tags.
    if (
        deprel == 'advmod'
        and not re.match(r'^(ADV|ADJ|CCONJ|DET|PART|SYM)', cols[UPOS])
        and 'fixed' not in childrels
        and 'goeswith' not in childrels
    ):
        testid = 'rel-upos-advmod'
        testmessage = f"'advmod' should be 'ADV' but it is '{cols[UPOS]}'"
        warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])

    # Known expletives are pronouns. Determiners and particles are probably acceptable, too.
    if deprel == 'expl' and not re.match(r'^(PRON|DET|PART)$', cols[UPOS]):
        testid = 'rel-upos-expl'
        testmessage = f"'expl' should normally be 'PRON' but it is '{cols[UPOS]}'"
        warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])

    # Auxiliary verb/particle must be AUX.
    if deprel == 'aux' and not re.match(r'^(AUX)', cols[UPOS]):
        testid = 'rel-upos-aux'
        testmessage = f"'aux' should be 'AUX' but it is '{cols[UPOS]}'"
        warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])

    # Copula is an auxiliary verb/particle (AUX) or a pronoun (PRON|DET).
    if deprel == 'cop' and not re.match(r'^(AUX|PRON|DET|SYM)', cols[UPOS]):
        testid = 'rel-upos-cop'
        testmessage = f"'cop' should be 'AUX' or 'PRON'/'DET' but it is '{cols[UPOS]}'"
        warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])

    # Case is normally an adposition, maybe particle.
    # However, there are also secondary adpositions and they may have the original POS tag:
    # NOUN: [cs] pomocí, prostřednictvím
    # VERB: [en] including
    # Interjection can also act as case marker for vocative, as in Sanskrit: भोः भगवन् / bhoḥ bhagavan / oh sir.
    if deprel == 'case' and re.match(r'^(PROPN|ADJ|PRON|DET|NUM|AUX)', cols[UPOS]) and 'fixed' not in childrels:
        testid = 'rel-upos-case'
        testmessage = f"'case' should not be '{cols[UPOS]}'"
        warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])

    # Mark is normally a conjunction or adposition, maybe particle but definitely not a pronoun.
    if (
        deprel == 'mark'
        and re.match(r'^(NOUN|PROPN|ADJ|PRON|DET|NUM|VERB|AUX|INTJ)', cols[UPOS])
        and 'fixed' not in childrels
    ):
        testid = 'rel-upos-mark'
        testmessage = f"'mark' should not be '{cols[UPOS]}'"
        warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])

    # Cc is a conjunction, possibly an adverb or particle.
    if (
        deprel == 'cc'
        and re.match(r'^(NOUN|PROPN|ADJ|PRON|DET|NUM|VERB|AUX|INTJ)', cols[UPOS])
        and 'fixed' not in childrels
    ):
        testid = 'rel-upos-cc'
        testmessage = f"'cc' should not be '{cols[UPOS]}'"
        warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])

    if cols[DEPREL] == 'punct' and cols[UPOS] != 'PUNCT':
        testid = 'rel-upos-punct'
        testmessage = f"'punct' must be 'PUNCT' but it is '{cols[UPOS]}'"
        warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])

    if cols[UPOS] == 'PUNCT' and not re.match(r'^(punct|root)', deprel):
        testid = 'upos-rel-punct'
        testmessage = f"'PUNCT' must be 'punct' but it is '{cols[DEPREL]}'"
        warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])


def validate_left_to_right_relations(id, tree):  # noqa: A002
    """Validate that certain relations go left-to-right.

    Certain UD relations must always go left-to-right. Here we currently check the rule for the basic dependencies.
    The same should also be tested for the enhanced dependencies!
    """
    testlevel = 3
    testclass = 'Syntax'
    cols = tree['nodes'][id]

    if is_multiword_token(cols):
        return

    if len(cols) <= DEPREL:
        return  # this has been already reported in trees()

    # According to the v2 guidelines, apposition should also be left-headed,
    # although the definition of apposition may need to be improved.
    if re.match(r'^(conj|fixed|flat|goeswith|appos)', cols[DEPREL]):
        ichild = int(cols[ID])
        iparent = int(cols[HEAD])
        if ichild < iparent:
            # We must recognize the relation type in the test id so we can manage exceptions for legacy treebanks.
            # For conj, flat, and fixed the requirement was introduced already before UD 2.2, and all treebanks in UD 2.3
            # passed it. For appos and goeswith the requirement was introduced before UD 2.4 and legacy treebanks
            # are allowed to fail it.
            testid = f'right-to-left-{lspec2ud(cols[DEPREL])}'
            testmessage = f"Relation '{cols[DEPREL]}' must go left-to-right."
            warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])


def validate_single_subject(id, tree):  # noqa: A002
    """Check that predicate has only one subject.

    An xcomp dependent normally has no subject, but in some languages the
    requirement may be weaker: it could have an overt subject if it is
    correferential with a particular argument of the matrix verb. Hence we do
    not check zero subjects of xcomp dependents at present.
    Furthermore, in some situations we must allow two subjects (but not three or more).
    If a clause acts as a nonverbal predicate of another clause, and if there is
    no copula, then we must attach two subjects to the predicate of the inner
    clause: one is the predicate of the inner clause, the other is the predicate
    of the outer clause. This could in theory be recursive but in practice it isn't.
    See also issue 34 (https://github.com/UniversalDependencies/tools/issues/34).
    """
    subjects = sorted([x for x in tree['children'][id] if re.search(r'subj', lspec2ud(tree['nodes'][x][DEPREL]))])
    if len(subjects) > 2:  # noqa: PLR2004
        # We test for more than 2, but in the error message we still say more than 1,
        # so that we do not have to explain the exceptions.
        testlevel = 3
        testclass = 'Syntax'
        testid = 'too-many-subjects'
        testmessage = f'Node has more than one subject: {subjects!s}'
        warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])


def validate_orphan(id, tree):  # noqa: A002
    """Validate the orphan relation.

    The orphan relation is used to attach an unpromoted orphan to the promoted
    orphan in gapping constructions. A common error is that the promoted orphan
    gets the orphan relation too. The parent of orphan is typically attached
    via a conj relation, although some other relations are plausible too.
    """
    # This is a level 3 test, we will check only the universal part of the relation.
    deprel = lspec2ud(tree['nodes'][id][DEPREL])

    if deprel == 'orphan':
        pid = int(tree['nodes'][id][HEAD])
        pdeprel = lspec2ud(tree['nodes'][pid][DEPREL])

        # We include advcl because gapping (or something very similar) can also
        # occur in subordinate clauses: "He buys companies like my mother [does] vegetables."
        # In theory, a similar pattern could also occur with reparandum.
        # A similar pattern also occurs with acl, e.g. in Latvian:
        # viņš ēd tos ābolus, ko pirms tam [ēda] tārpi ('he eats the same apples, which where [eaten] by worms before that')
        # Other clausal heads (ccomp, csubj) may be eligible as well, e.g. in Latvian
        # (see also issue 635 19.9.2019):
        # atjēdzos, ka bez angļu valodas nekur [netikšu] '[I] realised, that [I will get] nowhere without English'
        if not re.match(r'^(conj|parataxis|root|csubj|ccomp|advcl|acl|reparandum)$', pdeprel):
            testlevel = 3
            testclass = 'Syntax'
            testid = 'orphan-parent'
            testmessage = f"The parent of 'orphan' should normally be 'conj' but it is '{pdeprel}'."
            warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])


def validate_functional_leaves(id, tree):  # noqa: A002, C901
    """Check for known exceptions if function-word nodes are not leaves."""
    testlevel = 3
    testclass = 'Syntax'
    # This is a level 3 test, we will check only the universal part of the relation.
    deprel = lspec2ud(tree['nodes'][id][DEPREL])

    if re.match(r'^(case|mark|cc|aux|cop|det|fixed|goeswith|punct)$', deprel):
        idparent = id
        for idchild in tree['children'][id]:
            # This is a level 3 test, we will check only the universal part of the relation.
            pdeprel = lspec2ud(tree['nodes'][idparent][DEPREL])
            # # #!!! We should also check that 'det' does not have children except for a limited set of exceptions!
            # # #!!! (see https://universaldependencies.org/u/overview/syntax.html #function-word-modifiers)
            cdeprel = lspec2ud(tree['nodes'][idchild][DEPREL])
            # The guidelines explicitly say that negation can modify any function word
            # (see https://universaldependencies.org/u/overview/syntax.html #function-word-modifiers).
            # We cannot recognize negation simply by deprel; we have to look at the
            # part-of-speech tag and the Polarity feature as well.
            cupos = tree['nodes'][idchild][UPOS]
            cfeats = tree['nodes'][idchild][FEATS].split('|')
            if (
                pdeprel != 'punct'
                and cdeprel == 'advmod'
                and re.match(r'^(PART|ADV)$', cupos)
                and 'Polarity = Neg' in cfeats
            ):
                continue

            # Punctuation should not depend on function words if it can be projectively
            # attached to a content word. But sometimes it cannot. Czech example:
            # "Budou - li však zbývat , ukončíme" (lit. "will - if however remain , we-stop")
            # "však" depends on "ukončíme" while "budou" and "li" depend nonprojectively
            # on "zbývat" (which depends on "ukončíme"). "Budou" is aux and "li" is mark.
            # Yet the hyphen must depend on one of them because any other attachment would
            # be non-projective. Here we assume that if the parent of a punctuation node
            # is attached nonprojectively, punctuation can be attached to it to avoid its
            # own nonprojectivity.
            gap = get_gap(idparent, tree)
            if gap and cdeprel == 'punct':
                continue

            # Auxiliaries, conjunctions and case markers will tollerate a few special
            # types of modifiers.
            # Punctuation should normally not depend on a functional node. However,
            # it is possible that a functional node such as auxiliary verb is in
            # quotation marks or brackets ("must") and then these symbols should depend
            # on the functional node. We temporarily allow punctuation here, until we
            # can detect precisely the bracket situation and disallow the rest.
            # According to the guidelines
            # (https://universaldependencies.org/u/overview/syntax.html #function-word-modifiers),
            # mark can have a limited set of adverbial/oblique dependents, while the same
            # is not allowed for nodes attached as case. Nevertheless, there are valid
            # objections against this (see https://github.com/UniversalDependencies/docs/issues/618)
            # and we may want to revisit the guideline in UD v3. For the time being,
            # we make the validator more benevolent to 'case' too. (If we now force people
            # to attach adverbials higher, information will be lost and later reversal
            # of the step will not be possible.)
            # Coordinating conjunctions usually depend on a non-first conjunct, i.e.,
            # on a node whose deprel is 'conj'. However, there are paired conjunctions
            # such as "both-and", "either-or". Here the first part is attached to the
            # first conjunct. Since some function nodes (mark, case, aux, cop) can be
            # coordinated, we must allow 'cc' children under these nodes, too. However,
            # we do not want to allow 'cc' under another 'cc'. (Still, 'cc' can have
            # a 'conj' dependent. In "and/or", "or" will depend on "and" as 'conj'.)
            if re.match(r'^(mark|case)$', pdeprel) and not re.match(
                r'^(advmod|obl|goeswith|fixed|reparandum|conj|cc|punct)$',
                cdeprel,
            ):
                testid = 'leaf-mark-case'
                testmessage = (
                    f"'{pdeprel}' not expected to have children ({idparent}:{tree['nodes'][idparent][FORM]}",
                    f':{pdeprel} --> {idchild}:{tree["nodes"][idchild][FORM]}:{cdeprel})',
                )
                warn(
                    testmessage,
                    testclass,
                    testlevel=testlevel,
                    testid=testid,
                    nodeid=id,
                    nodelineno=tree['linenos'][idchild],
                )

            # # #!!! The pdeprel regex in the following test should probably include "det".
            # # #!!! I forgot to add it well in advance of release 2.4, so I am leaving it
            # # #!!! out for now, so that people don't have to deal with additional load
            # # #!!! of errors.
            if re.match(r'^(aux|cop)$', pdeprel) and not re.match(
                r'^(goeswith|fixed|reparandum|conj|cc|punct)$',
                cdeprel,
            ):
                testid = 'leaf-aux-cop'
                testmessage = (
                    f"'{pdeprel}' not expected to have children ({idparent}:{tree['nodes'][idparent][FORM]}",
                    f':{pdeprel} --> {idchild}:{tree["nodes"][idchild][FORM]}:{cdeprel})',
                )
                warn(
                    testmessage,
                    testclass,
                    testlevel=testlevel,
                    testid=testid,
                    nodeid=id,
                    nodelineno=tree['linenos'][idchild],
                )

            if re.match(r'^(cc)$', pdeprel) and not re.match(r'^(goeswith|fixed|reparandum|conj|punct)$', cdeprel):
                testid = 'leaf-cc'
                testmessage = (
                    f"'{pdeprel}' not expected to have children ({idparent}:{tree['nodes'][idparent][FORM]}",
                    f':{pdeprel} --> {idchild}:{tree["nodes"][idchild][FORM]}:{cdeprel})',
                )
                warn(
                    testmessage,
                    testclass,
                    testlevel=testlevel,
                    testid=testid,
                    nodeid=id,
                    nodelineno=tree['linenos'][idchild],
                )

            # Fixed expressions should not be nested, i.e., no chains of fixed relations.
            # As they are supposed to represent functional elements, they should not have
            # other dependents either, with the possible exception of conj.
            # # #!!! We also allow a punct child, at least temporarily, because of fixed
            # # #!!! expressions that have a hyphen in the middle (e.g. Russian "вперед-назад").
            # # #!!! It would be better to keep these expressions as one token. But sometimes
            # # #!!! the tokenizer is out of control of the UD data providers and it is not
            # # #!!! practical to retokenize.
            elif pdeprel == 'fixed' and not re.match(r'^(goeswith|reparandum|conj|punct)$', cdeprel):
                testid = 'leaf-fixed'
                testmessage = (
                    f"'{pdeprel}' not expected to have children ({idparent}:{tree['nodes'][idparent][FORM]}",
                    f':{pdeprel} --> {idchild}:{tree["nodes"][idchild][FORM]}:{cdeprel})',
                )
                warn(
                    testmessage,
                    testclass,
                    testlevel=testlevel,
                    testid=testid,
                    nodeid=id,
                    nodelineno=tree['linenos'][idchild],
                )

            # Goeswith cannot have any children, not even another goeswith.
            elif pdeprel == 'goeswith':
                testid = 'leaf-goeswith'
                testmessage = (
                    f"'{pdeprel}' not expected to have children ({idparent}",
                    f':{tree["nodes"][idparent][FORM]}:{pdeprel} --> {idchild}:{tree["nodes"][idchild][FORM]}:{cdeprel})',
                )
                warn(
                    testmessage,
                    testclass,
                    testlevel=testlevel,
                    testid=testid,
                    nodeid=id,
                    nodelineno=tree['linenos'][idchild],
                )

            # Punctuation can exceptionally have other punct children if an exclamation
            # mark is in brackets or quotes. It cannot have other children.
            elif pdeprel == 'punct' and cdeprel != 'punct':
                testid = 'leaf-punct'
                testmessage = (
                    f"'{pdeprel}' not expected to have children ({idparent}:{tree['nodes'][idparent][FORM]}",
                    f':{pdeprel} --> {idchild}:{tree["nodes"][idchild][FORM]}:{cdeprel})',
                )
                warn(
                    testmessage,
                    testclass,
                    testlevel=testlevel,
                    testid=testid,
                    nodeid=id,
                    nodelineno=tree['linenos'][idchild],
                )


def collect_ancestors(id, tree, ancestors):  # noqa: A002
    """Collect the ancestors of a node in a list.

    Usage: ancestors = collect_ancestors(nodeid, nodes, [])
    """
    pid = int(tree['nodes'][int(id)][HEAD])
    if pid == 0:
        ancestors.append(0)
        return ancestors

    if pid in ancestors:
        # Cycle has been reported on level 2. But we must jump out of it now.
        return ancestors

    ancestors.append(pid)
    return collect_ancestors(pid, tree, ancestors)


def get_caused_nonprojectivities(id, tree):  # noqa: A002
    """Check whether a node is in a gap of a nonprojective edge.

    Report true only if the node's parent is not in the same gap.
    (We use this function to check that a punctuation node does not cause
    nonprojectivity. But if it has been dragged to the gap with a larger subtree,
    then we do not blame it.)

    tree ... dictionary:
      nodes ... array of word lines, i.e., lists of columns; mwt/empty nodes are skipped, indices equal to ids (nodes[0] is empty)
      children ... array of sets of children indices (int); array indices equal to ids (children[0] are the children of the root)
      linenos ... array of line numbers in the file, corresponding to nodes (needed in error messages)
    """
    iid = int(id)  # just to be sure
    # We need to find all nodes that are not ancestors of this node and lie
    # on other side of this node than their parent. First get the set of ancestors.
    ancestors = collect_ancestors(iid, tree, [])
    maxid = len(tree['nodes']) - 1
    # Get the lists of nodes to either side of id.
    # Do not look beyond the parent (if it is in the same gap, it is the parent's responsibility).
    pid = int(tree['nodes'][iid][HEAD])

    if pid < iid:
        left = range(pid + 1, iid)  # ranges are open from the right (i.e. iid-1 is the last number)
        right = range(iid + 1, maxid + 1)

    else:
        left = range(1, iid)
        right = range(iid + 1, pid)

    # Exclude nodes whose parents are ancestors of id.
    sancestors = set(ancestors)
    leftna = [x for x in left if int(tree['nodes'][x][HEAD]) not in sancestors]
    rightna = [x for x in right if int(tree['nodes'][x][HEAD]) not in sancestors]
    leftcross = [x for x in leftna if int(tree['nodes'][x][HEAD]) > iid]
    rightcross = [x for x in rightna if int(tree['nodes'][x][HEAD]) < iid]

    # Once again, exclude nonprojectivities that are caused by ancestors of id.
    if pid < iid:
        rightcross = [x for x in rightcross if int(tree['nodes'][x][HEAD]) > pid]

    else:
        leftcross = [x for x in leftcross if int(tree['nodes'][x][HEAD]) < pid]

    # Do not return just a boolean value. Return the nonprojective nodes so we can report them.
    return sorted(leftcross + rightcross)


def get_gap(id, tree):  # noqa: A002
    """Get the gap between a node and its parent."""
    iid = int(id)  # just to be sure
    pid = int(tree['nodes'][iid][HEAD])

    rangebetween = range(iid + 1, pid) if iid < pid else range(pid + 1, iid)

    gap = set()
    if rangebetween:
        projection = set()
        get_projection(pid, tree, projection)
        gap = set(rangebetween) - projection

    return gap


def validate_goeswith_span(id, tree):  # noqa: A002
    """Validate the goeswith relation.

    The relation 'goeswith' is used to connect word parts that are separated
    by whitespace and should be one word instead. We assume that the relation
    goes left-to-right, which is checked elsewhere. Here we check that the
    nodes really were separated by whitespace. If there is another node in the
    middle, it must be also attached via 'goeswith'. The parameter id refers to
    the node whose goeswith children we test.
    """
    testlevel = 3
    testclass = 'Syntax'
    gwchildren = sorted([x for x in tree['children'][id] if lspec2ud(tree['nodes'][x][DEPREL]) == 'goeswith'])
    if gwchildren:
        gwlist = sorted([id, *gwchildren])
        gwrange = list(range(id, int(tree['nodes'][gwchildren[-1]][ID]) + 1))

        # All nodes between me and my last goeswith child should be goeswith too.
        if gwlist != gwrange:
            testid = 'goeswith-gap'
            testmessage = f'Violation of guidelines: gaps in goeswith group {gwlist!s} ! =  {gwrange!s}.'
            warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])

        # Non-last node in a goeswith range must have a space after itself.
        nospaceafter = [x for x in gwlist[:-1] if 'SpaceAfter=No' in tree['nodes'][x][MISC].split('|')]
        if nospaceafter:
            testid = 'goeswith-nospace'
            testmessage = "'goeswith' cannot connect nodes that are not separated by whitespace"
            warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])


def validate_fixed_span(id, tree):  # noqa: A002
    """Validate the fixed relation.

    Like with goeswith, the fixed relation should not in general skip words that
    are not part of the fixed expression. Unlike goeswith however, there can be
    an intervening punctuation symbol.

    Update 2019-04-13: The rule that fixed expressions cannot be discontiguous
    has been challenged with examples from Swedish and Coptic, see
    https://github.com/UniversalDependencies/docs/issues/623
    For the moment, I am turning this test off. In the future, we should
    distinguish fatal errors from warnings and then this test will perhaps be
    just a warning.
    """
    # return None  # # #!!! temporarily turned off
    fxchildren = sorted([i for i in tree['children'][id] if lspec2ud(tree['nodes'][i][DEPREL]) == 'fixed'])
    if fxchildren:
        fxlist = sorted([id, *fxchildren])
        fxrange = list(range(id, int(tree['nodes'][fxchildren[-1]][ID]) + 1))
        # All nodes between me and my last fixed child should be either fixed or punct.
        fxdiff = set(fxrange) - set(fxlist)
        fxgap = [i for i in fxdiff if lspec2ud(tree['nodes'][i][DEPREL]) != 'punct']
        if fxgap:
            testlevel = 3
            testclass = 'Syntax'
            testid = 'fixed-gap'
            testmessage = f'Gaps in fixed expression {fxlist!s}'
            warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])


def validate_projective_punctuation(id, tree):  # noqa: A002
    """Punctuation is not supposed to cause nonprojectivity or to be attached nonprojectively."""
    testlevel = 3
    testclass = 'Syntax'
    # This is a level 3 test, we will check only the universal part of the relation.
    deprel = lspec2ud(tree['nodes'][id][DEPREL])

    if deprel == 'punct':
        nonprojnodes = get_caused_nonprojectivities(id, tree)
        if nonprojnodes:
            testid = 'punct-causes-nonproj'
            testmessage = f'Punctuation must not cause non-projectivity of nodes {nonprojnodes}'
            warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])

        gap = get_gap(id, tree)
        if gap:
            testid = 'punct-is-nonproj'
            testmessage = f'Punctuation must not be attached non-projectively over nodes {sorted(gap)}'
            warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=id, nodelineno=tree['linenos'][id])


def validate_annotation(tree):
    """Check universally valid consequences of the annotation guidelines."""
    for node in tree['nodes']:
        id = int(node[ID])  # noqa: A001
        validate_upos_vs_deprel(id, tree)
        validate_left_to_right_relations(id, tree)
        validate_single_subject(id, tree)
        validate_orphan(id, tree)
        validate_functional_leaves(id, tree)
        validate_fixed_span(id, tree)
        validate_goeswith_span(id, tree)
        validate_projective_punctuation(id, tree)


def validate_enhanced_annotation(graph):
    """Check universally valid consequences of the annotation guidelines in the enhanced representation.

    Currently tests only phenomena specific to the
    enhanced dependencies; however, we should also test things that are
    required in the basic dependencies (such as left-to-right coordination),
    unless it is obvious that in enhanced dependencies such things are legal.
    """
    testlevel = 3
    testclass = 'Enhanced'
    # Enhanced dependencies should not contain the orphan relation.
    # However, all types of enhancements are optional and orphans are excluded
    # only if this treebank addresses gapping. We do not know it until we see
    # the first empty node.
    global line_of_first_empty_node  # noqa: PLW0603
    global line_of_first_enhanced_orphan  # noqa: PLW0603

    for id in graph:  # noqa: A001
        if is_empty_node(graph[id]['cols']) and not line_of_first_empty_node:
            # # #!!! This may not be exactly the first occurrence because the ids (keys) are not sorted.
            line_of_first_empty_node = graph[id]['lineno']

            # Empty node itself is not an error. Report it only for the first time
            # and only if an orphan occurred before it.
            if line_of_first_enhanced_orphan:
                testid = 'empty-node-after-eorphan'
                testmessage = (
                    'Empty node means that we address gapping and there should be no orphans in the enhanced graph;',
                    f' but we saw one on line {line_of_first_enhanced_orphan}',
                )
                warn(
                    testmessage,
                    testclass,
                    testlevel=testlevel,
                    testid=testid,
                    nodeid=id,
                    nodelineno=graph[id]['lineno'],
                )

        udeprels = {lspec2ud(d) for h, d in graph[id]['deps']}
        if 'orphan' in udeprels:
            if not line_of_first_enhanced_orphan:
                # # #!!! This may not be exactly the first occurrence because the ids (keys) are not sorted.
                line_of_first_enhanced_orphan = graph[id]['lineno']

            # If we have seen an empty node, then the orphan is an error.
            if line_of_first_empty_node:
                testid = 'eorphan-after-empty-node'
                testmessage = (
                    "'orphan' not allowed in enhanced graph",
                    f' because we saw an empty node on line {line_of_first_empty_node}',
                )
                warn(
                    testmessage,
                    testclass,
                    testlevel=testlevel,
                    testid=testid,
                    nodeid=id,
                    nodelineno=graph[id]['lineno'],
                )


# Level 4 tests. Language-specific formal tests. Now we can check in which words spaces are permitted,
# and which Feature = Value pairs are defined.
def validate_whitespace(cols, tag_sets):
    """Check a single line for disallowed whitespace.

    Here we assume that all language-independent whitespace-related tests have
    already been done in validate_cols_level1(), so we only check for words
    with spaces that are explicitly allowed in a given language.
    """
    testlevel = 4
    testclass = 'Format'

    for col_idx in (FORM, LEMMA):
        if col_idx >= len(cols):
            break  # this has been already reported in trees()

        if whitespace_re.match(cols[col_idx]) is not None:
            # Whitespace found - does it pass?
            for regex in tag_sets[TOKENSWSPACE]:
                if regex.fullmatch(cols[col_idx]):
                    break
            else:
                warn_on_missing_files.add('tokens_w_space')
                testid = 'invalid-word-with-space'
                testmessage = (
                    f"'{cols[col_idx]}' in column {COLNAMES[col_idx]} is not on the list of exceptions",
                    'allowed to contain whitespace (data/tokens_w_space.LANG files).',
                )
                warn(testmessage, testclass, testlevel=testlevel, testid=testid)


# Level 5 tests. Annotation content vs. the guidelines, language-specific.
def validate_auxiliary_verbs(cols, children, nodes, line, lang, auxlist):  # noqa: ARG001, PLR0913
    """Verify that the UPOS:AUX is used only with lemmas known to act as auxiliary verbs or particles in the given language.

    auxlist ... list of known auxiliary lemmas for the language
    cols ... columns of the head node
    children ... list of ids
    nodes ... dictionary where we can translate the node id into its CoNLL-U columns
    line ... line number of the node within the file
    lang ... language code
    """
    if cols[UPOS] == 'AUX' and cols[LEMMA] != '_':
        altlang = get_alt_language(cols[MISC])
        if altlang:
            lang = altlang
            auxlist, coplist = get_auxdata_for_language(altlang)

        auxdict = {}
        if auxlist != []:
            auxdict = {lang: auxlist}

        if lang == 'shopen':
            # 'desu', 'kudasai', 'yo' and 'sa' are romanized Japanese.
            lspecauxs = ['desu', 'kudasai', 'yo', 'sa']
            for ilang in auxdict:
                ilspecauxs = auxdict[ilang]
                lspecauxs = lspecauxs + ilspecauxs
        else:
            lspecauxs = auxdict.get(lang)

        if not lspecauxs:
            testlevel = 5
            testclass = 'Morpho'
            testid = 'aux-lemma'
            testmessage = (
                f"'{cols[LEMMA]}' is not an auxiliary verb in language [{lang}]",
                '(there are no known approved auxiliaries in this language)',
            )
            warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=cols[ID], nodelineno=line)

        elif cols[LEMMA] not in lspecauxs:
            testlevel = 5
            testclass = 'Morpho'
            testid = 'aux-lemma'
            testmessage = f"'{cols[LEMMA]}' is not an auxiliary verb in language [{lang}]"
            warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=cols[ID], nodelineno=line)


def validate_copula_lemmas(cols, children, nodes, line, lang, coplist):  # noqa: ARG001, PLR0913
    """Verify that the relation cop is used only with lemmas that are known to act as copulas in the given language.

    cols ... columns of the head node
    children ... list of ids
    nodes ... dictionary where we can translate the node id into its CoNLL-U columns
    line ... line number of the node within the file

    """
    if cols[DEPREL] == 'cop' and cols[LEMMA] != '_':
        altlang = get_alt_language(cols[MISC])
        if altlang:
            lang = altlang
            auxlist, coplist = get_auxdata_for_language(altlang)

        copdict = {}
        if coplist != []:
            copdict = {lang: coplist}

        # In Slavic languages, the iteratives are still variants of "to be",
        # although they have a different lemma (derived from the main one).
        # In addition, Polish and Russian also have pronominal copulas ("to" = "this/that").
        # 'orv': ['быти', 'не быти'] See above (AUX verbs) for the comment on affirmative vs. negative lemma.
        # Lauma says that all four should be copulas despite the fact that
        # kļūt and tapt correspond to English "to become", which is not
        # copula in UD. See also the discussion in
        # https://github.com/UniversalDependencies/docs/issues/622
        # 'lv':  ['būt', 'kļūt', 'tikt', 'tapt'],
        # Two writing systems are used in Sanskrit treebanks (Devanagari and Latin) and we must list both spellings.
        # Jack: [sms] i'lla = to not be
        # Jack says about Erzya:
        # The copula is represented by the independent copulas ульнемс (preterit) and улемс (non-past),
        # and the dependent morphology -оль (both preterit and non-past).
        # The neg арась occurs in locative/existential negation, and its
        # positive counterpart is realized in the three copulas above.
        # The neg аш in [mdf] is locative/existential negation.
        # Niko says about Komi:
        # Past tense copula is вӧвны, and in the future it is лоны, and both have a few frequentative forms.
        # 'быть' is Russian copula and it is occasionally used in spoken Komi due to code switching.
        # Komi Permyak: овлыны = to be (habitual) [Jack Rueter]
        # Sino-Tibetan languages.
        # See https://github.com/UniversalDependencies/docs/issues/653 for a discussion about Chinese copulas.
        # 是(shi4) and 为/為(wei2) should be interchangeable.
        # Sam: In Cantonese, 為 is used only in the high-standard variety, not in colloquial speech.
        if lang == 'shopen':
            # 'desu' is romanized Japanese.
            lspeccops = ['desu']
            for ilang in copdict:
                ilspeccops = copdict[ilang]
                lspeccops = lspeccops + ilspeccops
        else:
            lspeccops = copdict.get(lang)

        if not lspeccops:
            testlevel = 5
            testclass = 'Syntax'
            testid = 'cop-lemma'
            testmessage = (
                f"'{cols[LEMMA]}' is not a copula in language [{lang}]",
                '(there are no known approved copulas in this language)',
            )
            warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=cols[ID], nodelineno=line)

        elif cols[LEMMA] not in lspeccops:
            testlevel = 5
            testclass = 'Syntax'
            testid = 'cop-lemma'
            testmessage = f"'{cols[LEMMA]}' is not a copula in language [{lang}]"
            warn(testmessage, testclass, testlevel=testlevel, testid=testid, nodeid=cols[ID], nodelineno=line)


def validate_lspec_annotation(tree, lang, tag_sets):
    """Check language-specific consequences of the annotation guidelines."""
    # # #!!! Building the information about the tree is repeated and has been done in the other functions before.
    # # #!!! We should remember the information and not build it several times!
    global sentence_line  # the line of the first token/word of the current tree (skipping comments!)  # noqa: PLW0602
    node_line = sentence_line - 1
    lines = {}  # node id -> line number of that node (for error messages)
    nodes = {}  # node id -> columns of that node
    children = {}  # node -> set of children

    for cols in tree:
        node_line += 1

        if not is_word(cols):
            continue

        if len(cols) <= HEAD:
            # This error has been reported on lower levels, do not report it here.
            # Do not continue to check annotation if there are elementary flaws.
            return

        if cols[HEAD] == '_':
            # This error has been reported on lower levels, do not report it here.
            # Do not continue to check annotation if there are elementary flaws.
            return

        try:
            id_ = int(cols[ID])  # noqa: F841
        except ValueError:
            # This error has been reported on lower levels, do not report it here.
            # Do not continue to check annotation if there are elementary flaws.
            return

        try:
            head = int(cols[HEAD])  # noqa: F841
        except ValueError:
            # This error has been reported on lower levels, do not report it here.
            # Do not continue to check annotation if there are elementary flaws.
            return

        # Incrementally build the set of children of every node.
        lines.setdefault(cols[ID], node_line)
        nodes.setdefault(cols[ID], cols)
        children.setdefault(cols[HEAD], set()).add(cols[ID])

    for cols in tree:
        if not is_word(cols):
            continue

        myline = lines.get(cols[ID], sentence_line)
        mychildren = children.get(cols[ID], [])
        validate_auxiliary_verbs(cols, mychildren, nodes, myline, lang, tag_sets[AUX])
        validate_copula_lemmas(cols, mychildren, nodes, myline, lang, tag_sets[COP])


# Main part
def validate(inp, lang, level, check_tree_text, single_root, check_space_after, tag_sets, known_sent_ids):  # noqa: PLR0913
    """Validate a single input file."""
    global tree_counter  # noqa: PLW0603
    for comments, sentence in trees(inp, tag_sets, level, lang):
        tree_counter += 1
        # the individual lines have been validated already in trees()
        # here go tests which are done on the whole tree
        idseqok = validate_ID_sequence(sentence)  # level 1
        validate_token_ranges(sentence)  # level 1
        if level > 1:
            validate_sent_id(comments, known_sent_ids, lang)  # level 2

            if check_tree_text:
                validate_text_meta(comments, sentence, check_space_after)  # level 2

            validate_root(sentence)  # level 2
            validate_id_references(sentence)  # level 2
            validate_deps(sentence)  # level 2 and up
            validate_misc(sentence)  # level 2 and up

            # Avoid building tree structure if the sequence of node ids is corrupted.
            if idseqok:
                tree = build_tree(sentence, single_root)  # level 2 test: tree is single-rooted, connected, cycle-free
                egraph = build_egraph(sentence)  # level 2 test: egraph is connected

            else:
                tree = None
                egraph = None

            if tree:
                if level > 2:  # noqa: PLR2004
                    validate_annotation(tree)  # level 3
                    if level > 4:  # noqa: PLR2004
                        validate_lspec_annotation(sentence, lang, tag_sets)  # level 5
            else:
                testlevel = 2
                testclass = 'Format'
                testid = 'skipped-corrupt-tree'
                testmessage = 'Skipping annotation tests because of corrupt tree structure.'
                warn(testmessage, testclass, testlevel=testlevel, testid=testid, lineno=False)

            if egraph and level > 2:  # noqa: PLR2004
                validate_enhanced_annotation(egraph)  # level 3

        # validate_newlines(inp)  # level 1


def load_file(filename):
    """Load a file and return its content as a list of lines."""
    res = set()
    resource_file = files('latin_utilities').joinpath(filename)
    with resource_file.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()  # noqa: PLW2901

            if not line or line.startswith('#'):
                continue

            res.add(line)

    return res


def load_feat_set(filename_langspec, lcode, add_features):
    """Load the list of permitted feature-value pairs and returns it as a set."""
    global featdata  # noqa: PLW0603
    global warn_on_undoc_feats  # noqa: PLW0603

    resource_file = files('latin_utilities').joinpath(filename_langspec)
    with resource_file.open('r', encoding='utf-8') as f:
        all_features_0 = json.load(f)

    featdata = all_features_0['features']
    featset = get_featdata_for_language(lcode)
    if add_features:
        add_features_file = files('latin_utilities').joinpath(add_features)
        with add_features_file.open('r', encoding='utf-8') as file:
            xtra_features = json.load(file)
            for f_name, f_dict in xtra_features.items():
                featset[f_name] = f_dict

    # Prepare a global message about permitted features and values. We will add
    # it to the first error message about an unknown feature. Note that this
    # global information pertains to the default validation language and it
    # should not be used with code-switched segments in alternative languages.
    msg = ''
    if lcode not in featdata:
        msg += f'No feature-value pairs have been permitted for language [{lcode}].\n'
        msg += (
            'They can be permitted at the address below (if the language has an ISO code and is registered with UD):\n'
        )
        msg += 'https://quest.ms.mff.cuni.cz/udvalidator/cgi-bin/unidep/langspec/specify_feature.pl\n'
        warn_on_undoc_feats = msg

    else:
        # Identify feature values that are permitted in the current language.
        for f in featset:
            for e in featset[f]['errors']:
                msg += f'ERROR in _{lcode}/feat/{f}.md: {e}\n'

        res = set()

        for f in featset:
            if featset[f]['permitted'] > 0:
                for v in featset[f]['uvalues']:
                    res.add(f'{f}={v}')

                for v in featset[f]['lvalues']:
                    res.add(f'{f}={v}')

        sorted_documented_features = sorted(res)
        msg += f'The following {len(sorted_documented_features)} feature values are currently permitted in language [{lcode}]:\n'
        msg += ', '.join(sorted_documented_features) + '\n'
        msg += 'If a language needs a feature that is not documented in the universal guidelines, the feature must\n'
        msg += 'have a language-specific documentation page in a prescribed format.\n'
        msg += 'See https://universaldependencies.org/contributing_language_specific.html for further guidelines.\n'
        msg += 'All features including universal must be specifically turned on for each language in which they are used.\n'
        msg += 'See https://quest.ms.mff.cuni.cz/udvalidator/cgi-bin/unidep/langspec/specify_feature.pl for details.\n'
        warn_on_undoc_feats = msg

    return featset


def get_featdata_for_language(lcode):
    """Search the previously loaded database of feature-value combinations.

    Returns the lists for a given language code. For most CoNLL-U files,
    this function is called only once at the beginning. However, some files
    contain code-switched data and we may temporarily need to validate
    another language.
    """
    global featdata  # noqa: PLW0602
    # # #!!! If lcode is 'ud', we should permit all universal feature-value pairs,
    # # #!!! regardless of language-specific documentation.
    # Do not crash if the user asks for an unknown language.
    if lcode not in featdata:
        return {}  # # #!!! or None?

    return featdata[lcode]


def load_deprel_set(filename_langspec, lcode):
    """Load the list of permitted relation types and returns it as a set."""
    global depreldata  # noqa: PLW0603
    global warn_on_undoc_deps  # noqa: PLW0603

    resource_file = files('latin_utilities').joinpath(filename_langspec)
    with resource_file.open('r', encoding='utf-8') as f:
        all_deprels_0 = json.load(f)

    depreldata = all_deprels_0['deprels']
    deprelset = get_depreldata_for_language(lcode)
    # Prepare a global message about permitted relation labels. We will add
    # it to the first error message about an unknown relation. Note that this
    # global information pertains to the default validation language and it
    # should not be used with code-switched segments in alternative languages.
    msg = ''

    if len(deprelset) == 0:
        msg += f'No dependency relation types have been permitted for language [{lcode}].\n'
        msg += (
            'They can be permitted at the address below (if the language has an ISO code and is registered with UD):\n'
        )
        msg += 'https://quest.ms.mff.cuni.cz/udvalidator/cgi-bin/unidep/langspec/specify_deprel.pl\n'

    else:
        # Identify dependency relations that are permitted in the current language.
        # If there are errors in documentation, identify the erroneous doc file.
        # Note that depreldata[lcode] may not exist even though we have a non-empty
        # set of relations, if lcode is 'ud'.
        if lcode in depreldata:
            for r in depreldata[lcode]:
                file = re.sub(r':', r'-', r)
                if file == 'aux':
                    file = 'aux_'

                for e in depreldata[lcode][r]['errors']:
                    msg += f'ERROR in _{lcode}/dep/{file}.md: {e}\n'

        sorted_documented_relations = sorted(deprelset)
        msg += f'The following {len(sorted_documented_relations)} relations are currently permitted in language [{lcode}]:\n'
        msg += ', '.join(sorted_documented_relations) + '\n'
        msg += (
            'If a language needs a relation subtype that is not documented in the universal guidelines, the relation\n'
        )
        msg += 'must have a language-specific documentation page in a prescribed format.\n'
        msg += 'See https://universaldependencies.org/contributing_language_specific.html for further guidelines.\n'
        msg += 'Documented dependency relations can be specifically turned on/off for each language in which they are used.\n'
        msg += 'See https://quest.ms.mff.cuni.cz/udvalidator/cgi-bin/unidep/langspec/specify_deprel.pl for details.\n'

    # Save the message in a global variable.
    # We will add it to the first error message about an unknown feature in the data.
    warn_on_undoc_deps = msg

    return deprelset


def get_depreldata_for_language(lcode):
    """Search the previously loaded database of dependency relation labels.

    Returns the lists for a given language code. For most CoNLL-U files,
    this function is called only once at the beginning. However, some files
    contain code-switched data and we may temporarily need to validate
    another language.
    """
    global depreldata  # noqa: PLW0602
    deprelset = set()

    # If lcode is 'ud', we should permit all universal dependency relations,
    # regardless of language-specific documentation.
    # # #!!! We should be able to take them from the documentation JSON files instead of listing them here.
    if lcode == 'ud':
        deprelset = {
            'nsubj',
            'obj',
            'iobj',
            'csubj',
            'ccomp',
            'xcomp',
            'obl',
            'vocative',
            'expl',
            'dislocated',
            'advcl',
            'advmod',
            'discourse',
            'aux',
            'cop',
            'mark',
            'nmod',
            'appos',
            'nummod',
            'acl',
            'amod',
            'det',
            'clf',
            'case',
            'conj',
            'cc',
            'fixed',
            'flat',
            'compound',
            'list',
            'parataxis',
            'orphan',
            'goeswith',
            'reparandum',
            'punct',
            'root',
            'dep',
        }

    elif lcode in depreldata:
        for r in depreldata[lcode]:
            if depreldata[lcode][r]['permitted'] > 0:
                deprelset.add(r)

    return deprelset


def load_set(f_name_ud, f_name_langspec, validate_langspec=False, validate_enhanced=False):
    """Load a list of values from the two files, and returns their set.

    If f_name_langspec doesn't exist, loads nothing and returns
    None (ie this taglist is not checked for the given language). If f_name_langspec
    is None, only loads the UD one. This is probably only useful for CPOS which doesn't
    allow language-specific extensions. Set validate_langspec = True when loading basic dependencies.
    That way the language specific deps will be checked to be truly extensions of UD ones.
    Set validate_enhanced = True when loading enhanced dependencies. They will be checked to be
    truly extensions of universal relations, too; but a more relaxed regular expression will
    be checked because enhanced relations may contain stuff that is forbidden in the basic ones.
    """
    res = load_file(f_name_ud)  # Now res holds UD

    # Next load and optionally check the langspec extensions
    if f_name_langspec is not None and f_name_langspec != f_name_ud and Path.exists(f_name_langspec):
        l_spec = load_file(f_name_langspec)
        for v in l_spec:
            if validate_enhanced:
                # We are reading the list of language-specific dependency relations in the enhanced representation
                # (i.e., the DEPS column, not DEPREL). Make sure that they match the regular expression that
                # restricts enhanced dependencies.
                if not edeprel_re.match(v):
                    testlevel = 4
                    testclass = 'Enhanced'
                    testid = 'edeprel-def-regex'
                    testmessage = (
                        f"Spurious language-specific enhanced relation '{v}'",
                        ' - it does not match the regular expression that restricts enhanced relations.',
                    )
                    warn(testmessage, testclass, testlevel=testlevel, testid=testid, lineno=False)
                    continue

            elif validate_langspec and not re.match(r'^[a-z]+(:[a-z]+)?$', v):
                # We are reading the list of language-specific dependency relations in the basic representation
                # (i.e., the DEPREL column, not DEPS). Make sure that they match the regular expression that
                # restricts basic dependencies. (In particular, that they do not contain extensions allowed in
                # enhanced dependencies, which should be listed in a separate file.)
                testlevel = 4
                testclass = 'Syntax'
                testid = 'deprel-def-regex'
                testmessage = (
                    f"Spurious language-specific relation '{v}' - in basic UD, it must match '^[a-z]+(:[a-z]+)?'."
                )
                warn(testmessage, testclass, testlevel=testlevel, testid=testid, lineno=False)
                continue

            if validate_langspec or validate_enhanced:
                try:
                    parts = v.split(':')
                    if parts[0] not in res and parts[0] != 'ref':
                        testlevel = 4
                        testclass = 'Syntax'
                        testid = 'deprel-def-universal-part'
                        testmessage = (
                            f"Spurious language-specific relation '{v}' - not an extension of any UD relation."
                        )
                        warn(testmessage, testclass, testlevel=testlevel, testid=testid, lineno=False)
                        continue
                except ValueError:
                    # If the relation does not contain a colon, it is not a valid UD relation.
                    testlevel = 4
                    testclass = 'Syntax'
                    testid = 'deprel-def-universal-part'
                    testmessage = f"Spurious language-specific relation '{v}' - not an extension of any UD relation."
                    warn(testmessage, testclass, testlevel=testlevel, testid=testid, lineno=False)
                    continue
            res.add(v)

    return res


def get_auxdata_for_language(lcode):
    """Search the previously loaded database of auxiliary/copula lemmas.

    Returns the AUX and COP lists for a given language code. For most CoNLL-U files,
    this function is called only once at the beginning. However, some files
    contain code-switched data and we may temporarily need to validate
    another language.
    """
    global auxdata  # noqa: PLW0602
    # If any of the functions of the lemma is other than cop.PRON, it counts as an auxiliary.
    # If any of the functions of the lemma is cop.*, it counts as a copula.
    auxlist = []
    coplist = []

    if lcode == 'shopen':
        for lcode1, lemmalist in auxdata.items():
            auxlist = auxlist + [
                x for x in lemmalist if len([y for y in lemmalist[x]['functions'] if y['function'] != 'cop.PRON']) > 0
            ]
            coplist = coplist + [
                x
                for x in lemmalist
                if len([y for y in lemmalist[x]['functions'] if re.match(r'^cop\.', y['function'])]) > 0
            ]
    else:
        lemmalist = auxdata.get(lcode, {}).keys()
        auxlist = [
            x for x in lemmalist if len([y for y in auxdata[lcode][x]['functions'] if y['function'] != 'cop.PRON']) > 0
        ]
        coplist = [
            x
            for x in lemmalist
            if len([y for y in auxdata[lcode][x]['functions'] if re.match(r'^cop\.', y['function'])]) > 0
        ]

    return auxlist, coplist


def get_alt_language(misc):
    """Take the value of the MISC column for a token and check Lang attribute.

    If it exists, return the language code specified in the Lang attribute.
    This is useful for code switching, if a phrase is in a language different
    from the main language of the document. The validator can then temporarily
    switch to a different set of language-specific tests.
    """
    misclist = misc.split('|')
    p = re.compile(r'Lang=(.+)')

    for attr in misclist:
        m = p.match(attr)
        if m:
            return m.group(1)

    return None


def validate_conllu(input, lang, level, add_features, sentence_concordance=None):  # noqa: A002
    """Validate a CoNLL-U file.

    input = file to check
    lang = language to check (two-letter code). If specified, it will use language-specific files in the data directory.
    level:
       - 1: Test only CoNLL-U backbone.
       - 2: UD format.
       - 3: UD contents.
       - 4: Language-specific labels.
       - 5: Language-specific contents.
    add_features = dictionary of additional features to add to validator
    sentence_concordance = dictionary mapping sentence ids to some other id system (e.g. brat doc/line numbers)
    """
    if sentence_concordance is None:
        sentence_concordance = {}
    global tree_counter, auxdata, sentence_mapid, error_log  # noqa: PLW0602, PLW0603
    tree_counter = 0
    sentence_mapid = sentence_concordance

    single_root = True  # Whether to allow trees with several root words
    check_tree_text = True  # Do not test tree text - internal use
    check_space_after = True  # Do not test presence of SpaceAfter=No.

    # Level of validation
    if level < 1:
        print(f'Level must not be less than 1; changing from {level} to 1')
        level = 1

    # No language-specific tests for levels 1-3
    # Anyways, any Feature = Value pair should be allowed at level 3 (because it may be language-specific),
    # and any word form or lemma can contain spaces (because language-specific guidelines may allow it).
    # We can also test language 'ud' on level 4; then it will require that no language-specific features are present.
    if level < 4:  # noqa: PLR2004
        lang = 'ud'

    # Sets of tags for every column that needs to be checked, plus (in v2) other sets, like the allowed tokens with space
    tagsets = {XPOS: None, UPOS: None, FEATS: None, DEPREL: None, DEPS: None, TOKENSWSPACE: None, AUX: None}

    if lang:
        tagsets[UPOS] = UPOS_TAGS
        tagsets[FEATS] = load_feat_set('data/feats.json', lang, add_features)
        tagsets[DEPREL] = load_deprel_set('data/deprels.json', lang)
        # All relations available in DEPREL are also allowed in DEPS.
        # In addition, there might be relations that are only allowed in DEPS.
        # One of them, "ref", is universal and we currently mention it directly
        # in the code, although there is also a file "edeprel.ud".
        tagsets[DEPS] = (
            tagsets[DEPREL] | {'ref'} | load_set('data/deprel.ud', 'edeprel.' + lang, validate_enhanced=True)
        )
        tagsets[TOKENSWSPACE] = load_set('data/tokens_w_space.ud', 'tokens_w_space.' + lang)
        tagsets[TOKENSWSPACE] = [
            re.compile(regex, re.U) for regex in tagsets[TOKENSWSPACE]
        ]  # ...turn into compiled regular expressions
        # Read the list of auxiliaries from the JSON file.
        # This file must not be edited directly!
        # Use the web interface at https://quest.ms.mff.cuni.cz/udvalidator/cgi-bin/unidep/langspec/specify_auxiliary.pl instead!

        data_file = files('latin_utilities').joinpath('data/data.json')
        with data_file.open('r', encoding='utf-8') as file:
            jsondata = json.load(file)

        auxdata = jsondata['auxiliaries']
        tagsets[AUX], tagsets[COP] = get_auxdata_for_language(lang)

    with open(input, encoding='utf-8') as f:
        input_data = f.readlines()

    known_sent_ids = set()
    validate(input_data, lang, level, check_tree_text, single_root, check_space_after, tagsets, known_sent_ids)

    # format log entries
    if error_log:
        error_log.sort(key=lambda x: (x[1], x[3]['line_no']))
        current_key = error_log[0][0]
        output_log = [f'{current_key}:']
        for item in error_log:
            key, ord, level, entry = item  # noqa: A001

            if key != current_key:
                current_key = key
                output_log.append('')
                output_log.append(f'{current_key}:')

            line_no = entry['line_no']
            alt_id = entry['alt_id']
            tree_counter = entry['tree_counter']
            line = f'Line {line_no}' if line_no else ''
            sentence = f'Sentence {alt_id}' if alt_id else ''
            output_log.append(
                f'{line} {sentence}: [L{entry["testlevel"]} {entry["error_type"]} {entry["testid"]}] {entry["msg"]}',
            )
    else:
        output_log = [f'File {input} is valid.']

    return output_log
