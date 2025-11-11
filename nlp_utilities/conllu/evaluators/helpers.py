"""Helper functions for the conllu evaluators."""

from __future__ import annotations

from nlp_utilities.constants import UNIVERSAL_FEATURES

from .base import Alignment, UDWord


def _beyond_end(words: list[UDWord], i: int, multiword_span_end: int) -> bool:
    """Check if word index is beyond the multiword span end.

    Arguments:
        words: List of words
        i: Index to check
        multiword_span_end: End position of multiword span

    Returns:
        True if beyond end

    """
    if i >= len(words):
        return True

    if words[i].is_multiword:
        return words[i].span.start >= multiword_span_end

    return words[i].span.end > multiword_span_end


def _extend_end(word: UDWord, multiword_span_end: int) -> int:
    """Extend multiword span end if word extends beyond it.

    Arguments:
        word: Word to check
        multiword_span_end: Current span end

    Returns:
        New span end

    """
    if word.is_multiword and word.span.end > multiword_span_end:
        return word.span.end

    return multiword_span_end


def _find_multiword_span(
    gold_words: list[UDWord],
    system_words: list[UDWord],
    gi: int,
    si: int,
) -> tuple[int, int, int, int]:
    """Find the multiword span boundaries.

    Arguments:
        gold_words: Gold words
        system_words: System words
        gi: Gold index
        si: System index

    Returns:
        Tuple of (gs, ss, gi, si) - start and end indices

    """
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
    while not _beyond_end(gold_words, gi, multiword_span_end) or not _beyond_end(
        system_words,
        si,
        multiword_span_end,
    ):
        if gi < len(gold_words) and (
            si >= len(system_words) or gold_words[gi].span.start <= system_words[si].span.start
        ):
            multiword_span_end = _extend_end(gold_words[gi], multiword_span_end)
            gi += 1
        else:
            multiword_span_end = _extend_end(system_words[si], multiword_span_end)
            si += 1

    return gs, ss, gi, si


def _compute_lcs(  # noqa: PLR0913
    gold_words: list[UDWord],
    system_words: list[UDWord],
    gi: int,
    si: int,
    gs: int,
    ss: int,
) -> list[list[int]]:
    """Compute longest common subsequence for word alignment.

    Arguments:
        gold_words: Gold words
        system_words: System words
        gi: Gold end index
        si: System end index
        gs: Gold start index
        ss: System start index

    Returns:
        LCS matrix

    """
    lcs = [[0] * (si - ss) for _ in range(gi - gs)]
    for g in reversed(range(gi - gs)):
        for s in reversed(range(si - ss)):
            if gold_words[gs + g].token['form'].lower() == system_words[ss + s].token['form'].lower():
                lcs[g][s] = 1 + (lcs[g + 1][s + 1] if g + 1 < gi - gs and s + 1 < si - ss else 0)
            lcs[g][s] = max(lcs[g][s], lcs[g + 1][s] if g + 1 < gi - gs else 0)
            lcs[g][s] = max(lcs[g][s], lcs[g][s + 1] if s + 1 < si - ss else 0)
    return lcs


def align_words(gold_words: list[UDWord], system_words: list[UDWord]) -> Alignment:
    """Align gold and system words using span matching and LCS for multi-word tokens.

    Arguments:
        gold_words: Gold words
        system_words: System words

    Returns:
        Alignment object

    """
    alignment = Alignment(gold_words, system_words)
    gi, si = 0, 0

    while gi < len(gold_words) and si < len(system_words):
        if gold_words[gi].is_multiword or system_words[si].is_multiword:
            # Multi-word tokens => align via LCS within the whole "multiword span"
            gs, ss, gi, si = _find_multiword_span(gold_words, system_words, gi, si)

            if si > ss and gi > gs:
                lcs = _compute_lcs(gold_words, system_words, gi, si, gs, ss)

                # Store aligned words
                s, g = 0, 0
                while g < gi - gs and s < si - ss:
                    if gold_words[gs + g].token['form'].lower() == system_words[ss + s].token['form'].lower():
                        alignment.append_aligned_words(gold_words[gs + g], system_words[ss + s])
                        g += 1
                        s += 1
                    elif lcs[g][s] == (lcs[g + 1][s] if g + 1 < gi - gs else 0):
                        g += 1
                    else:
                        s += 1
        # No multi-word token => align according to spans
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


def process_enhanced_deps(deps: list[tuple[str, int]] | None) -> list[tuple[int, list[str]]]:
    """Parse enhanced dependencies from conllu parsed format into structured format.

    Arguments:
        deps: Parsed DEPS field from conllu library (list of (deprel, head) tuples)

    Returns:
        List of (head_id, dependency_path) tuples where dependency_path is a list of relation labels

    """
    edeps: list[tuple[int, list[str]]] = []
    if not deps:
        return edeps

    for deprel, head in deps:
        # Split deprel on '>' to get enhancement steps (e.g., "nmod>case" -> ["nmod", "case"])
        steps = deprel.split('>') if '>' in deprel else [deprel]
        edeps.append((head, steps))

    return edeps


def remove_deprel_subtype(deprel: str) -> str:
    """Normalize a deprel by removing subtypes (everything after ':').

    Arguments:
        deprel: Full deprel string (e.g., "nmod:tmod")

    Returns:
        Base deprel without subtypes (e.g., "nmod")

    """
    return deprel.split(':')[0]


def filter_universal_features(feats: dict[str, str] | None) -> dict[str, str]:
    """Filter features dict to only universal features.

    Arguments:
        feats: FEATS dictionary from conllu token

    Returns:
        Dict containing only universal features

    """
    if not feats:
        return {}
    return {k: v for k, v in feats.items() if k in UNIVERSAL_FEATURES}
