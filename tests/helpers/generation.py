"""Helper functions for evaluator tests."""

from __future__ import annotations

from typing import Any

import conllu

from conllu_tools.evaluation.base import Alignment, UDSpan, UDWord


def create_test_udword(
    form: str,
    upos: str,
    head: int,
    deprel: str,
    *,
    word_id: int = 1,
    lemma: str | None = None,
    xpos: str = '_',
    feats: dict[str, str] | None = None,
    start: int = 0,
    end: int | None = None,
    is_multiword: bool = False,
) -> UDWord:
    """Create a UDWord for testing.

    Args:
        form: Word form
        upos: Universal POS tag
        head: HEAD value
        deprel: Dependency relation
        word_id: Token ID
        lemma: Lemma (defaults to form)
        xpos: Language-specific POS tag
        feats: Morphological features dict
        start: Start position in character array
        end: End position (defaults to start + len(form))
        is_multiword: Whether this is part of a multi-word token

    Returns:
        UDWord instance

    """
    if lemma is None:
        lemma = form
    if end is None:
        end = start + len(form)

    token = conllu.Token(
        [
            ('id', word_id),
            ('form', form),
            ('lemma', lemma),
            ('upos', upos),
            ('xpos', xpos),
            ('feats', feats),
            ('head', head),
            ('deprel', deprel),
            ('deps', None),
            ('misc', None),
        ],
    )

    span = UDSpan(start=start, end=end)
    return UDWord(span=span, token=token, is_multiword=is_multiword)


def create_test_alignment(
    gold_words: list[UDWord],
    system_words: list[UDWord],
    *,
    aligned_pairs: list[tuple[int, int]] | None = None,
) -> Alignment:
    """Create an Alignment for testing.

    Args:
        gold_words: List of gold UDWord objects
        system_words: List of system UDWord objects
        aligned_pairs: Optional list of (gold_idx, system_idx) tuples to align

    Returns:
        Alignment instance

    """
    alignment = Alignment(gold_words=gold_words, system_words=system_words)

    if aligned_pairs:
        for gold_idx, system_idx in aligned_pairs:
            alignment.append_aligned_words(gold_words[gold_idx], system_words[system_idx])

    return alignment


def create_simple_conllu_sentence(
    tokens: list[dict[str, Any]],
    *,
    sent_id: str = 'test',
    text: str | None = None,
) -> conllu.TokenList:
    """Create a conllu.TokenList from token dictionaries.

    Args:
        tokens: List of token dictionaries with keys: id, form, lemma, upos, head, deprel, etc.
        sent_id: Sentence ID
        text: Text content (reconstructed from tokens if None)

    Returns:
        conllu.TokenList instance

    """
    if text is None:
        text = ' '.join(t['form'] for t in tokens if not isinstance(t.get('id'), tuple))

    lines = [
        f'# sent_id = {sent_id}',
        f'# text = {text}',
    ]

    for token in tokens:
        line_parts = [
            str(token.get('id', 1)),
            token.get('form', '_'),
            token.get('lemma', '_'),
            token.get('upos', '_'),
            token.get('xpos', '_'),
            token.get('feats', '_') if isinstance(token.get('feats'), str) else '_',
            str(token.get('head', 0)),
            token.get('deprel', '_'),
            token.get('deps', '_'),
            token.get('misc', '_'),
        ]
        lines.append('\t'.join(line_parts))

    lines.append('')  # Blank line at end
    conllu_text = '\n'.join(lines)
    return conllu.parse(conllu_text)[0]
