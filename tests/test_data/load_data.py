"""Data loading functions for tests."""

from __future__ import annotations

import json
from pathlib import Path

with Path(__file__).with_name('en_sentence.json').open(encoding='utf-8') as file:
    EN_SENTENCE = json.load(file)

with Path(__file__).with_name('la_sentence.json').open(encoding='utf-8') as file:
    LA_SENTENCE = json.load(file)

with Path(__file__).with_name('upos_deprel_invalid_pairs.json').open(encoding='utf-8') as file:
    UPOS_DEPREL_INVALID_PAIRS = json.load(file)

with Path(__file__).with_name('upos_deprel_valid_pairs.json').open(encoding='utf-8') as file:
    UPOS_DEPREL_VALID_PAIRS = json.load(file)
