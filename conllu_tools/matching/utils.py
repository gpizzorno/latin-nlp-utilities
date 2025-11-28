"""Pattern matching utilities for linguistic analysis."""

from __future__ import annotations

import conllu
import regex as re

from conllu_tools.constants import (
    CONDITION_COUNTER_MATCHER,
    NESTABLE_KEYS,
    NESTED_CONDITION_MATCHER,
    TOKEN_KEYS,
)

from .condition import Condition
from .result import MatchResult
from .sentence import SentencePattern
from .token import TokenPattern


def _format_value(value: str) -> list[str]:
    """Format a value string into a list of strings or integers."""
    return value.split('|') if '|' in value else [value]


def _get_match_value(value: str) -> tuple[bool, str, list[str]]:
    """Determine the match type and cleaned value for substring keys."""
    negation = value.startswith('!')
    if negation:
        value = value[1:]

    start = value.startswith('<')
    end = value.endswith('>')

    if start and end:
        return negation, 'contains', _format_value(value[1:-1])
    if start:
        return negation, 'startswith', _format_value(value[1:])
    if end:
        return negation, 'endswith', _format_value(value[:-1])
    return negation, 'equals', _format_value(value)


def _parse_conditions(conditions: list[str]) -> list[Condition]:
    """Parse a list of condition strings into Condition instances."""
    output = []
    for cond in conditions:
        if re.match(NESTED_CONDITION_MATCHER, cond):
            key, use_any, nested = re.match(NESTED_CONDITION_MATCHER, cond).groups()
            if key not in NESTABLE_KEYS:
                msg = f'Cannot nest conditions under key "{key}" of type "{TOKEN_KEYS[key]}".'
                raise ValueError(msg)

            nested = nested.split(',') if ',' in nested else [nested]
            output.append(Condition(key=key, values=_parse_conditions(nested), match_any=bool(use_any)))  # type: ignore [arg-type]
        else:
            key, value = cond.split('=', 1)
            neg, match_type, clean_value = _get_match_value(value)
            output.append(Condition(key=key, values=clean_value, match_type=match_type, negate=neg))  # type: ignore [arg-type]
    return output


def build_pattern(pattern_str: str, name: str | None = None) -> SentencePattern:
    """Build a SentencePattern from a pattern string.

    See the documentation for a detailed explanation of the syntax for the pattern string.

    Arguments:
        pattern_str (str): The pattern string to parse.
        name (str | None): Optional name for the pattern.

    Returns:
        SentencePattern: The constructed SentencePattern instance.

    """
    if not pattern_str or not isinstance(pattern_str, str):
        msg = 'Pattern string must be a non-empty string.'
        raise ValueError(msg)

    tokens = pattern_str.split('+')
    token_patterns = []

    for token in tokens:
        conditions = []
        token_params = {}
        # match counter(s)
        counter_match = re.match(CONDITION_COUNTER_MATCHER, token)
        if counter_match:
            min_count = counter_match.group(2)
            max_count = counter_match.group(3)
            min_count = int(min_count) if min_count is not None else None
            max_count = int(max_count) if max_count is not None else None
            if min_count and max_count:
                token_params['min_count'] = min_count
                token_params['max_count'] = max_count
            else:
                token_params['count'] = min_count if min_count is not None else 0
            token = token.replace(counter_match.group(1), '')  # noqa: PLW2901

        parts = token.split(':')
        neg, _, upos = _get_match_value(parts[0])
        token_params['negate'] = neg
        cond_list = parts[1:]

        # parse conditions
        if cond_list:
            conditions.extend(_parse_conditions(cond_list))

        if len(upos) == 1 and upos[0] == '*':
            if len(conditions) == 0:
                token_patterns.append(TokenPattern(**token_params))  # type: ignore [arg-type]
        else:
            conditions.append(Condition(key='upos', values=upos))  # type: ignore [arg-type]

        if len(conditions) > 0:
            token_patterns.append(TokenPattern(conditions=conditions, **token_params))  # type: ignore [arg-type]

    return SentencePattern(token_patterns, name)


def find_in_corpus(corpus: list[conllu.TokenList], patterns: list[SentencePattern]) -> list[MatchResult]:
    """Find all matches of given patterns in the corpus.

    Arguments:
        corpus (list[conllu.TokenList]): The corpus to search.
        patterns (list[SentencePattern]): The patterns to match.

    Returns:
        list[MatchResult]: The list of all match results.

    """
    matches = []
    for sentence in corpus:
        for pattern in patterns:
            matches.extend(pattern.match(sentence))
    return matches
