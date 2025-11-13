"""Shared fixtures for BRAT module tests."""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

from nlp_utilities.loaders import load_language_data
from tests.test_data.load_data import (
    BRAT_METADATA,
    MULTI_CONLLU,
    SIMPLE_ANN,
    SIMPLE_ANN_WITH_ROOT,
    SIMPLE_CONLLU,
    SIMPLE_TXT,
    SIMPLE_TXT_WITH_ROOT,
    base_path,
)


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_entity_annotation() -> dict[str, Any]:
    """Sample entity annotation dictionary."""
    return {
        'type': 'T',
        'id': 1,
        'upos': 'NOUN',
        'start': 0,
        'end': 5,
        'form': 'Word',
    }


@pytest.fixture
def sample_relation_annotation() -> dict[str, Any]:
    """Sample relation annotation dictionary."""
    return {
        'type': 'R',
        'id': 1,
        'deprel': 'nsubj',
        'head': 2,
        'dep': 1,
    }


@pytest.fixture
def sample_annotations() -> list[dict[str, Any]]:
    """Sample list of mixed annotations."""
    return [
        {'type': 'T', 'id': 1, 'upos': 'NOUN', 'start': 0, 'end': 5, 'form': 'Word'},
        {'type': 'T', 'id': 2, 'upos': 'VERB', 'start': 6, 'end': 10, 'form': 'test'},
        {'type': 'R', 'id': 1, 'deprel': 'nsubj', 'head': 2, 'dep': 1},
    ]


@pytest.fixture
def simple_ann_file(temp_dir: Path) -> Path:
    """Create a simple .ann file with test data."""
    ann_path = temp_dir / 'test.ann'
    ann_path.write_text(SIMPLE_ANN, encoding='utf-8')
    return ann_path


@pytest.fixture
def simple_txt_file(temp_dir: Path) -> Path:
    """Create a simple .txt file with test data."""
    txt_path = temp_dir / 'test.txt'
    txt_path.write_text(SIMPLE_TXT, encoding='utf-8')
    return txt_path


@pytest.fixture
def metadata_dict() -> dict[str, Any]:
    """Sample metadata dictionary."""
    return BRAT_METADATA  # type: ignore [no-any-return]


@pytest.fixture
def simple_conllu_content() -> str:
    """Return simple CoNLL-U formatted content for testing."""
    return SIMPLE_CONLLU


@pytest.fixture
def feature_set() -> dict[str, Any]:
    """Minimal feature set for testing."""
    return load_language_data('feats', language='la')


@pytest.fixture
def reference_conllu_file() -> Path:
    """Provide a reference CoNLL-U file for testing."""
    return base_path / 'brat' / 'simple.conllu'


@pytest.fixture
def brat_input_dir(temp_dir: Path) -> Path:
    """Create a directory with sample BRAT files."""
    brat_dir = temp_dir / 'brat_input'
    brat_dir.mkdir()
    (brat_dir / 'test.ann').write_text(SIMPLE_ANN_WITH_ROOT, encoding='utf-8')
    (brat_dir / 'test.txt').write_text(SIMPLE_TXT_WITH_ROOT, encoding='utf-8')
    return brat_dir


@pytest.fixture
def multi_sentence_conllu(temp_dir: Path) -> Path:
    """Create a multi-sentence CoNLL-U file."""
    conllu_path = temp_dir / 'multi.conllu'
    conllu_path.write_text(MULTI_CONLLU, encoding='utf-8')
    return conllu_path
