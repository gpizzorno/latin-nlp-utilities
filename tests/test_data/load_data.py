"""Data loading functions for tests."""

from __future__ import annotations

import json
from pathlib import Path

base_path = Path(__file__).parent

with (base_path / 'en_sentence.json').open(encoding='utf-8') as file:
    EN_SENTENCE = json.load(file)

with (base_path / 'la_sentence.json').open(encoding='utf-8') as file:
    LA_SENTENCE = json.load(file)

with (base_path / 'upos_deprel_invalid_pairs.json').open(encoding='utf-8') as file:
    UPOS_DEPREL_INVALID_PAIRS = json.load(file)

with (base_path / 'upos_deprel_valid_pairs.json').open(encoding='utf-8') as file:
    UPOS_DEPREL_VALID_PAIRS = json.load(file)

with (base_path / 'brat' / 'simple.ann').open(encoding='utf-8') as file:
    SIMPLE_ANN = file.read()

with (base_path / 'brat' / 'simple_with_root.ann').open(encoding='utf-8') as file:
    SIMPLE_ANN_WITH_ROOT = file.read()

with (base_path / 'brat' / 'simple.txt').open(encoding='utf-8') as file:
    SIMPLE_TXT = file.read()

with (base_path / 'brat' / 'simple_with_root.txt').open(encoding='utf-8') as file:
    SIMPLE_TXT_WITH_ROOT = file.read()

with (base_path / 'brat' / 'simple.conllu').open(encoding='utf-8') as file:
    SIMPLE_CONLLU = file.read()

with (base_path / 'brat' / 'multi.conllu').open(encoding='utf-8') as file:
    MULTI_CONLLU = file.read()

with (base_path / 'brat' / 'metadata.json').open(encoding='utf-8') as file:
    BRAT_METADATA = json.load(file)
