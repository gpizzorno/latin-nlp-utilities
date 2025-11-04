# Code from CoNLL 2018 UD shared task by Milan Straka, Martin Popel: https://universaldependencies.org/conll18/evaluation.html
# updated for evaluation of enhanced dependencies in IWPT 2020 shared task by Gosse Bouma: https://github.com/UniversalDependencies/tools/blob/master/iwpt20_xud_eval.py
# further updated by Gabe Pizzorno to compute evaluation data with and without dependency relations + error management +
# Python module only setup

import unicodedata

# CoNLL-U column names
ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC = range(10)

# Content and functional relations
CONTENT_DEPRELS = {
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
    'nmod',
    'appos',
    'nummod',
    'acl',
    'amod',
    'conj',
    'fixed',
    'flat',
    'compound',
    'list',
    'parataxis',
    'orphan',
    'goeswith',
    'reparandum',
    'root',
    'dep',
}

FUNCTIONAL_DEPRELS = {
    'aux',
    'cop',
    'mark',
    'det',
    'clf',
    'case',
    'cc',
}

UNIVERSAL_FEATURES = {
    'PronType',
    'NumType',
    'Poss',
    'Reflex',
    'Foreign',
    'Abbr',
    'Gender',
    'Animacy',
    'Number',
    'Case',
    'Definite',
    'Degree',
    'VerbForm',
    'Mood',
    'Tense',
    'Aspect',
    'Voice',
    'Evident',
    'Polarity',
    'Person',
    'Polite',
}


class UDError(Exception):
    """Raised when there is an error in the UD data or evaluation process."""


CASE_DEPRELS = {'obl', 'nmod', 'conj', 'advcl'}
UNIVERSAL_DEPREL_EXTENSIONS = {'pass', 'relcl', 'xsubj'}


def process_enhanced_deps(deps):
    """Modify the set of deps produced by system to be in accordance with gold treebank type.

    Return a (filtered) list of (hd, dependency_path) tuples.
    """
    edeps = []
    if deps == '_' or not deps:
        return edeps
    for edep in deps.split('|'):
        if ':' not in edep:
            continue
        (hd, path) = edep.split(':', 1)
        steps = path.split('>')
        edeps.append((hd, steps))
    return edeps


def load_conllu(file, treebank_type, eval_deprels):  # noqa: C901, PLR0912, PLR0915
    """Load given CoNLL-U file into internal representation."""

    # Internal representation classes
    class UDRepresentation:
        def __init__(self):
            # Characters of all the tokens in the whole file.
            # Whitespace between tokens is not included.
            self.characters = []
            # List of UDSpan instances with start&end indices into `characters`.
            self.tokens = []
            # List of UDWord instances.
            self.words = []
            # List of UDSpan instances with start&end indices into `characters`.
            self.sentences = []

    class UDSpan:
        def __init__(self, start, end):
            self.start = start
            # Note that self.end marks the first position **after the end** of span,
            # so we can use characters[start:end] or range(start, end).
            self.end = end

    class UDWord:
        def __init__(self, span, columns, is_multiword, eval_deprels):
            # Span of this word (or MWT, see below) within ud_representation.characters.
            self.span = span
            # 10 columns of the CoNLL-U file: ID, FORM, LEMMA,...
            self.columns = columns
            # is_multiword==True means that this word is part of a multi-word token.
            # In that case, self.span marks the span of the whole multi-word token.
            self.is_multiword = is_multiword

            if eval_deprels:
                # Reference to the UDWord instance representing the HEAD (or None if root).
                self.parent = None
                # List of references to UDWord instances representing functional-deprel children.
                self.functional_children = []
                # Only consider universal FEATS.
                self.columns[FEATS] = '|'.join(
                    sorted(feat for feat in columns[FEATS].split('|') if feat.split('=', 1)[0] in UNIVERSAL_FEATURES),
                )
                # Let's ignore language-specific deprel subtypes.
                self.columns[DEPREL] = columns[DEPREL].split(':')[0]
                # Precompute which deprels are CONTENT_DEPRELS and which FUNCTIONAL_DEPRELS
                self.is_content_deprel = self.columns[DEPREL] in CONTENT_DEPRELS
                self.is_functional_deprel = self.columns[DEPREL] in FUNCTIONAL_DEPRELS
                # store enhanced deps --GB
                # split string positions and enhanced labels as well?
                self.columns[DEPS] = process_enhanced_deps(columns[DEPS])

    ud = UDRepresentation()

    # Load the CoNLL-U file
    index, sentence_start = 0, None
    line_id = None

    while True:
        line = file.readline()
        if not line:
            break

        line = line.rstrip('\r\n')

        # Handle sentence start boundaries
        if sentence_start is None:
            # Skip comments
            if line.startswith('#'):
                continue

            # Start a new sentence
            ud.sentences.append(UDSpan(index, 0))
            sentence_start = len(ud.words)

        if not line:
            if eval_deprels:
                # Add parent and children UDWord links and check there are no cycles
                def process_word(word, line_id=line_id, sentence_start=sentence_start):
                    if word.parent == 'remapping':
                        msg = f'There is a cycle in a sentence: {line_id}'
                        raise UDError(msg)

                    if word.parent is None:
                        head = int(word.columns[HEAD])
                        if head < 0 or head > len(ud.words) - sentence_start:
                            msg = f"HEAD '{word.columns[HEAD]}' points outside of the sentence: {line_id}"
                            raise UDError(msg)
                        if head:
                            parent = ud.words[sentence_start + head - 1]
                            word.parent = 'remapping'
                            process_word(parent, line_id, sentence_start)
                            word.parent = parent

                position = (
                    sentence_start  # need to incrementally keep track of current position for loop detection in relcl
                )
                for word in ud.words[sentence_start:]:
                    process_word(word)
                    enhanced_deps = word.columns[DEPS]

                    # replace head positions of enhanced dependencies with parent word object -- GB
                    processed_deps = []
                    for head, steps in word.columns[DEPS]:  # (3,['conj:en','obj:voor'])
                        hd = int(head)
                        parent = (
                            ud.words[sentence_start + hd - 1] if hd else hd
                        )  # just assign '0' to parent for root cases
                        processed_deps.append((parent, steps))

                    enhanced_deps = processed_deps

                    # ignore rel>rel dependencies, and instead append the original hd/rel edge
                    # note that this also ignores other extensions (like adding lemma's)
                    # note that this sometimes introduces duplicates (if orig hd/rel was already included in DEPS)
                    if treebank_type['no_gapping']:  # enhancement 1
                        processed_deps = []
                        for parent, steps in enhanced_deps:
                            if len(steps) > 1:
                                processed_deps.append((word.parent, [word.columns[DEPREL]]))
                            elif (parent, steps) in processed_deps:
                                pass
                            else:
                                processed_deps.append((parent, steps))
                        enhanced_deps = processed_deps

                    # for a given conj node, any rel other than conj in DEPS can be ignored
                    if treebank_type['no_shared_parents_in_coordination']:  # enhancement  2
                        for hd, steps in enhanced_deps:
                            if len(steps) == 1 and steps[0].startswith('conj'):
                                enhanced_deps = [(hd, steps)]

                    # deprels not matching ud_hd/ud_dep are spurious.
                    # czech/pud estonian/ewt syntagrus finnish/pud
                    # TO DO: treebanks that do not mark xcomp and relcl subjects
                    if treebank_type['no_shared_dependents_in_coordination']:  # enhancement  3
                        processed_deps = []
                        for hd, steps in enhanced_deps:
                            duplicate = 0
                            for hd2, steps2 in enhanced_deps:
                                if (
                                    steps == steps2 and hd2 == word.columns[HEAD] and hd != hd2
                                ):  # checking only for ud_hd here, check for ud_dep as well?
                                    duplicate = 1
                            if not (duplicate):
                                processed_deps.append((hd, steps))
                        enhanced_deps = processed_deps

                    # if treebank does not have control relations: subjects of xcomp parents in system are to be skipped
                    # note that rel is actually a path sometimes rel1>rel2 in theory rel2 could be subj?
                    # from lassy-small: 7:conj:en>nsubj:pass|7:conj:en>nsubj:xsubj    (7,['conj:en','nsubj:xsubj'])
                    if treebank_type['no_control']:  # enhancement 4
                        processed_deps = []
                        for parent, steps in enhanced_deps:
                            include = 1
                            if parent and parent.columns[DEPREL] == 'xcomp':
                                for rel in steps:
                                    if rel.startswith('nsubj'):
                                        include = 0
                            if include:
                                processed_deps.append((parent, steps))
                        enhanced_deps = processed_deps

                    if treebank_type['no_external_arguments_of_relative_clauses']:  # enhancement 5
                        processed_deps = []
                        for parent, steps in enhanced_deps:
                            if steps[0] == 'ref':
                                processed_deps.append(
                                    (word.parent, [word.columns[DEPREL]]),
                                )  # append the original relation
                            # ignore external argument link
                            # external args are deps of an acl:relcl where that acl also is a dependent
                            # of external arg (i.e. ext arg introduces a cycle)
                            elif (
                                parent
                                and parent.columns[DEPREL].startswith('acl')
                                and int(parent.columns[HEAD]) == position - sentence_start
                            ):
                                # print('removed external argument')
                                pass
                            else:
                                processed_deps.append((parent, steps))
                        enhanced_deps = processed_deps

                    # treebanks where no lemma info has been added
                    if treebank_type['no_case_info']:  # enhancement number 6
                        processed_deps = []
                        for hd, steps in enhanced_deps:
                            processed_steps = []
                            for dep in steps:
                                depparts = dep.split(':')
                                if (
                                    depparts[0] in CASE_DEPRELS
                                    and len(depparts) == 2  # noqa: PLR2004
                                    and depparts[1] not in UNIVERSAL_DEPREL_EXTENSIONS
                                ):
                                    dep = depparts[0]  # noqa: PLW2901
                                processed_steps.append(dep)
                            processed_deps.append((hd, processed_steps))
                        enhanced_deps = processed_deps

                    position += 1
                    word.columns[DEPS] = enhanced_deps

                # func_children cannot be assigned within process_word
                # because it is called recursively and may result in adding one child twice.
                for word in ud.words[sentence_start:]:
                    if word.parent and word.is_functional_deprel:
                        word.parent.functional_children.append(word)

                if len(ud.words) == sentence_start:
                    msg = 'There is a sentence with 0 tokens (possibly a double blank line)'
                    raise UDError(msg)

                # Check there is a single root node
                if len([word for word in ud.words[sentence_start:] if word.parent is None]) != 1:
                    msg = 'There are multiple roots in a sentence'
                    raise UDError(msg)

                # End the sentence
                ud.sentences[-1].end = index
                sentence_start = None
                continue

            ud.sentences[-1].end = index
            sentence_start = None
            continue

        # Read next token/word
        columns = line.split('\t')
        if len(columns) != 10:  # noqa: PLR2004
            msg = f'Line {line_id} does not contain 10 tab-separated columns: {columns}'
            raise UDError(msg)

        # Skip empty nodes
        # After collapsing empty nodes into the enhancements, these should not occur --GB
        if '.' in columns[ID]:
            msg = f'The collapsed CoNLL-U line still contains empty nodes: {line}'
            raise UDError(msg)

        # Delete spaces from FORM, so gold.characters == system.characters
        # even if one of them tokenizes the space. Use any Unicode character
        # with category Zs.
        columns[FORM] = ''.join(filter(lambda c: unicodedata.category(c) != 'Zs', columns[FORM]))
        if not columns[FORM]:
            msg = 'There is an empty FORM in the CoNLL-U file'
            raise UDError(msg)

        # Save token
        ud.characters.extend(columns[FORM])
        ud.tokens.append(UDSpan(index, index + len(columns[FORM])))
        index += len(columns[FORM])

        # Handle multi-word tokens to save word(s)
        # When matching words of gold file and system file, we first match the tokens.
        # The words which are also tokens are matched as tokens, but words in multi-word
        # tokens have to be handled differently.
        #
        # To handle multi-word tokens, we start by finding "multi-word spans".
        # Multi-word span is a span in the original text such that
        # - it contains at least one multi-word token
        # - all multi-word tokens in the span (considering both gold and system ones)
        #   are completely inside the span (i.e., they do not "stick out")
        # - the multi-word span is as small as possible
        #
        # For every multi-word span, we align the gold and system words completely
        # inside this span using LCS on their FORMs. The words not intersecting
        # (even partially) any multi-word span are then aligned as tokens.
        if '-' in columns[ID]:
            try:
                start, end = map(int, columns[ID].split('-'))
            except:  # noqa: E722
                msg = f"Cannot parse multi-word token ID '{columns[ID]}'"
                raise UDError(msg)  # noqa: B904

            for _ in range(start, end + 1):
                word_line = file.readline().rstrip('\r\n')
                word_columns = word_line.split('\t')
                if len(word_columns) != 10:  # noqa: PLR2004
                    msg = f"The CoNLL-U line does not contain 10 tab-separated columns: '{word_line}'"
                    raise UDError(msg)
                ud.words.append(UDWord(ud.tokens[-1], word_columns, is_multiword=True, eval_deprels=eval_deprels))

        # Basic tokens/words
        else:
            try:
                word_id = int(columns[ID])
            except:  # noqa: E722
                msg = f"Cannot parse word ID '{columns[ID]}'"
                raise UDError(msg)  # noqa: B904

            if word_id != len(ud.words) - sentence_start + 1:
                msg = (
                    f"Incorrect word ID '{columns[ID]}' for word '{columns[FORM]}',",
                    f"expected '{len(ud.words) - sentence_start + 1}'",
                )
                raise UDError(msg)

            if eval_deprels:
                try:
                    head_id = int(columns[HEAD])
                except:  # noqa: E722
                    msg = f"Cannot parse HEAD '{columns[HEAD]}'"
                    raise UDError(msg)  # noqa: B904

                if head_id < 0:
                    msg = 'HEAD cannot be negative'
                    raise UDError(msg)

            ud.words.append(UDWord(ud.tokens[-1], columns, is_multiword=False, eval_deprels=eval_deprels))

    if sentence_start is not None:
        msg = 'The CoNLL-U file does not end with empty line'
        raise UDError(msg)

    return ud


def evaluate(gold_ud, system_ud, eval_deprels=True):  # noqa: C901, PLR0915
    """Evaluate the gold and system treebanks (loaded using load_conllu)."""

    class Score:
        def __init__(self, gold_total, system_total, correct, aligned_total=None):
            self.correct = correct
            self.gold_total = gold_total
            self.system_total = system_total
            self.aligned_total = aligned_total
            self.precision = correct / system_total if system_total else 0.0
            self.recall = correct / gold_total if gold_total else 0.0
            self.f1 = (
                2 * correct / (system_total + gold_total)
                if system_total and gold_total and system_total + gold_total
                else 0.0
            )
            self.aligned_accuracy = correct / aligned_total if aligned_total else aligned_total

    class AlignmentWord:
        def __init__(self, gold_word, system_word):
            self.gold_word = gold_word
            self.system_word = system_word

    class Alignment:
        def __init__(self, gold_words, system_words):
            self.gold_words = gold_words
            self.system_words = system_words
            self.matched_words = []
            self.matched_words_map = {}

        def append_aligned_words(self, gold_word, system_word):
            self.matched_words.append(AlignmentWord(gold_word, system_word))
            self.matched_words_map[system_word] = gold_word

    def spans_score(gold_spans, system_spans):
        correct, gi, si = 0, 0, 0
        while gi < len(gold_spans) and si < len(system_spans):
            if system_spans[si].start < gold_spans[gi].start:
                si += 1
            elif gold_spans[gi].start < system_spans[si].start:
                gi += 1
            else:
                correct += gold_spans[gi].end == system_spans[si].end
                si += 1
                gi += 1

        return Score(len(gold_spans), len(system_spans), correct)

    def alignment_score(alignment, key_fn=None, filter_fn=None):
        if filter_fn is not None:
            gold = sum(1 for gold in alignment.gold_words if filter_fn(gold))
            system = sum(1 for system in alignment.system_words if filter_fn(system))
            aligned = sum(1 for word in alignment.matched_words if filter_fn(word.gold_word))
        else:
            gold = len(alignment.gold_words)
            system = len(alignment.system_words)
            aligned = len(alignment.matched_words)

        if key_fn is None:
            # Return score for whole aligned words
            return Score(gold, system, aligned)

        def gold_aligned_gold(word):
            return word

        def gold_aligned_system(word):
            return alignment.matched_words_map.get(word, 'NotAligned') if word is not None else None

        correct = 0
        for words in alignment.matched_words:
            if filter_fn is None or filter_fn(words.gold_word):
                if key_fn(words.gold_word, gold_aligned_gold) == key_fn(words.system_word, gold_aligned_system):
                    correct += 1

        return Score(gold, system, correct, aligned)

    def enhanced_alignment_score(alignment, eulas):
        # count all matching enhanced deprels in gold, system GB
        # gold and system = sum of gold and predicted deps
        # parents are pointers to word object, make sure to compare system parent with aligned word in gold in cases where
        # tokenization introduces mismatches in number of words per sentence.
        gold = 0
        for gold_word in alignment.gold_words:
            gold += len(gold_word.columns[DEPS])

        system = 0
        for system_word in alignment.system_words:
            system += len(system_word.columns[DEPS])

        # NB aligned does not play a role in computing f1 score -- GB
        aligned = len(alignment.matched_words)
        correct = 0
        for words in alignment.matched_words:
            gold_deps = words.gold_word.columns[DEPS]
            system_deps = words.system_word.columns[DEPS]
            for parent, dep in gold_deps:
                eulas_dep = [d.split(':')[0] for d in dep]
                for sparent, sdep in system_deps:
                    eulas_sdep = [d.split(':')[0] for d in sdep]
                    if (dep == sdep or (eulas_dep == eulas_sdep and eulas)) and (
                        parent == alignment.matched_words_map.get(sparent, 'NotAligned')
                        or (parent == 0 and sparent == 0)
                    ):
                        correct += 1

        return Score(gold, system, correct, aligned)

    def beyond_end(words, i, multiword_span_end):
        if i >= len(words):
            return True

        if words[i].is_multiword:
            return words[i].span.start >= multiword_span_end

        return words[i].span.end > multiword_span_end

    def extend_end(word, multiword_span_end):
        if word.is_multiword and word.span.end > multiword_span_end:
            return word.span.end

        return multiword_span_end

    def find_multiword_span(gold_words, system_words, gi, si):
        # We know gold_words[gi].is_multiword or system_words[si].is_multiword.
        # Find the start of the multiword span (gs, ss), so the multiword span is minimal.
        # Initialize multiword_span_end characters index.
        if gold_words[gi].is_multiword:
            multiword_span_end = gold_words[gi].span.end
            if not system_words[si].is_multiword and system_words[si].span.start < gold_words[gi].span.start:
                si += 1
        else:  # if system_words[si].is_multiword
            multiword_span_end = system_words[si].span.end
            if not gold_words[gi].is_multiword and gold_words[gi].span.start < system_words[si].span.start:
                gi += 1
        gs, ss = gi, si

        # Find the end of the multiword span
        # (so both gi and si are pointing to the word following the multiword span end).
        while not beyond_end(gold_words, gi, multiword_span_end) or not beyond_end(
            system_words,
            si,
            multiword_span_end,
        ):
            if gi < len(gold_words) and (
                si >= len(system_words) or gold_words[gi].span.start <= system_words[si].span.start
            ):
                multiword_span_end = extend_end(gold_words[gi], multiword_span_end)
                gi += 1
            else:
                multiword_span_end = extend_end(system_words[si], multiword_span_end)
                si += 1

        return gs, ss, gi, si

    def compute_lcs(gold_words, system_words, gi, si, gs, ss):  # noqa: PLR0913
        lcs = [[0] * (si - ss) for i in range(gi - gs)]
        for g in reversed(range(gi - gs)):
            for s in reversed(range(si - ss)):
                if gold_words[gs + g].columns[FORM].lower() == system_words[ss + s].columns[FORM].lower():
                    lcs[g][s] = 1 + (lcs[g + 1][s + 1] if g + 1 < gi - gs and s + 1 < si - ss else 0)
                lcs[g][s] = max(lcs[g][s], lcs[g + 1][s] if g + 1 < gi - gs else 0)
                lcs[g][s] = max(lcs[g][s], lcs[g][s + 1] if s + 1 < si - ss else 0)
        return lcs

    def align_words(gold_words, system_words):
        alignment = Alignment(gold_words, system_words)
        gi, si = 0, 0
        while gi < len(gold_words) and si < len(system_words):
            if gold_words[gi].is_multiword or system_words[si].is_multiword:
                # A: Multi-word tokens => align via LCS within the whole "multiword span".
                gs, ss, gi, si = find_multiword_span(gold_words, system_words, gi, si)

                if si > ss and gi > gs:
                    lcs = compute_lcs(gold_words, system_words, gi, si, gs, ss)

                    # Store aligned words
                    s, g = 0, 0
                    while g < gi - gs and s < si - ss:
                        if gold_words[gs + g].columns[FORM].lower() == system_words[ss + s].columns[FORM].lower():
                            alignment.append_aligned_words(gold_words[gs + g], system_words[ss + s])
                            g += 1
                            s += 1
                        elif lcs[g][s] == (lcs[g + 1][s] if g + 1 < gi - gs else 0):
                            g += 1
                        else:
                            s += 1
            # B: No multi-word token => align according to spans.
            elif (gold_words[gi].span.start, gold_words[gi].span.end) == (
                system_words[si].span.start,
                system_words[si].span.end,
            ):
                alignment.append_aligned_words(gold_words[gi], system_words[si])
                gi += 1
                si += 1
            elif gold_words[gi].span.start <= system_words[si].span.start:
                gi += 1
            else:
                si += 1

        return alignment

    # Check that the underlying character sequences do match.
    # In order to match tokens of gold file and system file, we consider the text
    # resulting from concatenation of gold tokens and text resulting from
    # concatenation of system tokens. These texts should match -- if they do not,
    # the evaluation fails.
    # If the texts do match, every token is represented as a range in this original
    # text, and tokens are equal only if their range is the same.

    if gold_ud.characters != system_ud.characters:
        index = 0
        while (
            index < len(gold_ud.characters)
            and index < len(system_ud.characters)
            and gold_ud.characters[index] == system_ud.characters[index]
        ):
            index += 1

        raise UDError(
            'The concatenation of tokens in gold file and in system file differ!\n'
            + "First 20 differing characters in gold file: '{}' and system file: '{}'".format(
                ''.join(gold_ud.characters[index : index + 20]),
                ''.join(system_ud.characters[index : index + 20]),
            ),
        )

    # Align words
    alignment = align_words(gold_ud.words, system_ud.words)

    # Compute the F1-scores
    return {
        'Tokens': spans_score(gold_ud.tokens, system_ud.tokens),
        'Sentences': spans_score(gold_ud.sentences, system_ud.sentences),
        'Words': alignment_score(alignment),
        'UPOS': alignment_score(alignment, lambda w, _: w.columns[UPOS]),
        'XPOS': alignment_score(alignment, lambda w, _: w.columns[XPOS]),
        'UFeats': alignment_score(alignment, lambda w, _: w.columns[FEATS]),
        'AllTags': alignment_score(alignment, lambda w, _: (w.columns[UPOS], w.columns[XPOS], w.columns[FEATS])),
        'Lemmas': alignment_score(alignment, lambda w, ga: w.columns[LEMMA] if ga(w).columns[LEMMA] != '_' else '_'),
        'UAS': alignment_score(alignment, lambda w, ga: ga(w.parent))
        if eval_deprels
        else Score(None, None, None, None),
        'LAS': alignment_score(alignment, lambda w, ga: (ga(w.parent), w.columns[DEPREL]))
        if eval_deprels
        else Score(None, None, None, None),
        # include enhanced DEPS score -- GB
        'ELAS': enhanced_alignment_score(alignment, 0) if eval_deprels else Score(None, None, None, None),
        'EULAS': enhanced_alignment_score(alignment, 1) if eval_deprels else Score(None, None, None, None),
        'CLAS': alignment_score(
            alignment,
            lambda w, ga: (ga(w.parent), w.columns[DEPREL]),
            filter_fn=lambda w: w.is_content_deprel,
        )
        if eval_deprels
        else Score(None, None, None, None),
        'MLAS': alignment_score(
            alignment,
            lambda w, ga: (
                ga(w.parent),
                w.columns[DEPREL],
                w.columns[UPOS],
                w.columns[FEATS],
                [(ga(c), c.columns[DEPREL], c.columns[UPOS], c.columns[FEATS]) for c in w.functional_children],
            ),
            filter_fn=lambda w: w.is_content_deprel,
        )
        if eval_deprels
        else Score(None, None, None, None),
        'BLEX': alignment_score(
            alignment,
            lambda w, ga: (ga(w.parent), w.columns[DEPREL], w.columns[LEMMA] if ga(w).columns[LEMMA] != '_' else '_'),
            filter_fn=lambda w: w.is_content_deprel,
        )
        if eval_deprels
        else Score(None, None, None, None),
    }


def load_conllu_file(path, treebank_type, eval_deprels):
    """Load a CoNLL-U file indicated by its path (path) and returns a UDRepresentation object."""
    with open(path, encoding='utf-8') as _file:
        return load_conllu(_file, treebank_type, eval_deprels)


def evaluate_ud_files(gold_path, system_path, tb_type, eval_deprels=True):
    """Evaluate a 'system' CoNLL-U file against a 'gold' file indicated by their paths (gold_path, system_path).

    tb_type allows specific enhancements to be switched off:
        0=evaluate all enhancement types,
        1=no gapping,
        2=no coord shared parents,
        3=no coord shared dependents,
        4=no xsubj (control verbs),
        5=no relative clauses,
        6=no case info in deprels. Values can be combined, e.g. 12=both 1 and 2.
    eval_deprels indicates whether dependency relations (both universal and ennhanced) should be evaluated:
    True=Yes (default), False=No.
    Returns a dictionary with following metrics, each having three fields: precision, recall, and f1:
        - Tokens: how well do the gold tokens match system tokens
        - Sentences: how well do the gold sentences match system sentences
        - Words: how well can the gold words be aligned to system words
        - UPOS: using aligned words, how well does UPOS match
        - XPOS: using aligned words, how well does XPOS match
        - UFeats: using aligned words, how well does universal FEATS match
        - AllTags: using aligned words, how well does UPOS+XPOS+FEATS match
        - Lemmas: using aligned words, how well does LEMMA match
    If eval_deprels=True the following metrics are also included:
        - UAS: using aligned words, how well does HEAD match
        - LAS: using aligned words, how well does HEAD+DEPREL(ignoring subtypes) match
        - CLAS: using aligned words with content DEPREL, how well does HEAD+DEPREL(ignoring subtypes) match
        - MLAS: using aligned words with content DEPREL, how well does
            HEAD+DEPREL(ignoring subtypes)+UPOS+UFEATS+FunctionalChildren(DEPREL+UPOS+UFEATS) match
        - BLEX: using aligned words with content DEPREL, how well does HEAD+DEPREL(ignoring subtypes)+LEMMAS match.
    """
    treebank_type = {}
    enhancements = list(tb_type)
    treebank_type['no_gapping'] = 1 if '1' in enhancements else 0
    treebank_type['no_shared_parents_in_coordination'] = 1 if '2' in enhancements else 0
    treebank_type['no_shared_dependents_in_coordination'] = 1 if '3' in enhancements else 0
    treebank_type['no_control'] = 1 if '4' in enhancements else 0
    treebank_type['no_external_arguments_of_relative_clauses'] = 1 if '5' in enhancements else 0
    treebank_type['no_case_info'] = 1 if '6' in enhancements else 0

    # Load CoNLL-U files
    gold_ud = load_conllu_file(gold_path, treebank_type, eval_deprels)
    system_ud = load_conllu_file(system_path, treebank_type, eval_deprels)

    return evaluate(gold_ud, system_ud, eval_deprels)
