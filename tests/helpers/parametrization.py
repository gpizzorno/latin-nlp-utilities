"""Parametrization helper functions for CoNLL-U validators."""

from __future__ import annotations

import copy

from conllu_tools.constants import UNIVERSAL_DEPRELS, UPOS_TAGS

from tests.test_data.load_data import UPOS_DEPREL_INVALID_PAIRS


def all_upos_tags() -> list[str]:
    """Return list of all valid UPOS tags for parametrized testing."""
    return copy.deepcopy(UPOS_TAGS)


def all_deprels() -> set[str]:
    """Return list of all valid universal DEPREL values (base forms without subtypes)."""
    return copy.deepcopy(UNIVERSAL_DEPRELS)


def invalid_upos_deprel_pairs() -> list[tuple[str, str]]:
    """Return list of known-invalid (UPOS, DEPREL) combinations."""
    return copy.deepcopy(UPOS_DEPREL_INVALID_PAIRS)


def validation_levels() -> list[int]:
    """Return [1, 2, 3, 4, 5] for level parametrization."""
    return [1, 2, 3, 4, 5]
