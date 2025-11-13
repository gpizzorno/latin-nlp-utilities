"""Shared fixtures for BRAT module tests."""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

from nlp_utilities.loaders import load_language_data


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
    content = """T1\tNOUN 0 5\tWord
T2\tVERB 6 10\ttest
R1\tnsubj Arg1:T2 Arg2:T1
"""
    ann_path.write_text(content, encoding='utf-8')
    return ann_path


@pytest.fixture
def simple_txt_file(temp_dir: Path) -> Path:
    """Create a simple .txt file with test data."""
    txt_path = temp_dir / 'test.txt'
    content = 'Word test'
    txt_path.write_text(content, encoding='utf-8')
    return txt_path


@pytest.fixture
def metadata_dict() -> dict[str, Any]:
    """Sample metadata dictionary."""
    return {
        'conllu_filename': '/path/to/file.conllu',
        'sents_per_doc': 10,
        'output_root': True,
    }


@pytest.fixture
def simple_conllu_content() -> str:
    """Return simple CoNLL-U formatted content for testing."""
    return """# sent_id = 1
# text = Word test
1	Word	word	NOUN	n-s---mn-	Case=Nom|Gender=Masc|Number=Sing	2	nsubj	_	_
2	test	test	VERB	v3spia---	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act	0	root	_	_

"""


@pytest.fixture
def feature_set() -> dict[str, Any]:
    """Minimal feature set for testing."""
    return load_language_data('feats', language='la')


@pytest.fixture
def brat_input_dir(temp_dir: Path) -> Path:
    """Create a directory with sample BRAT files for testing brat_to_conllu."""
    brat_dir = temp_dir / 'brat_input'
    brat_dir.mkdir()

    # Create a simple annotation file with ROOT marker
    ann_content = """T0\tROOT 0 0\tROOT
T1\tNOUN 0 4\tWord
T2\tVERB 5 9\ttest
R1\tnsubj Arg1:T2 Arg2:T1
"""
    (brat_dir / 'test.ann').write_text(ann_content, encoding='utf-8')
    (brat_dir / 'test.txt').write_text('Word test', encoding='utf-8')

    return brat_dir


@pytest.fixture
def reference_conllu_file(temp_dir: Path) -> Path:
    """Create a reference CoNLL-U file for testing brat_to_conllu."""
    conllu_path = temp_dir / 'reference.conllu'
    content = """# sent_id = 1
# text = Word test
1	Word	word	NOUN	n-s---mn-	Case=Nom|Gender=Masc|Number=Sing	0	root	_	_
2	test	test	VERB	v3spia---	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act	0	root	_	_

"""
    conllu_path.write_text(content, encoding='utf-8')
    return conllu_path


@pytest.fixture
def brat_with_root(temp_dir: Path) -> Path:
    """Create BRAT directory with ROOT annotations."""
    brat_dir = temp_dir / 'brat_with_root'
    brat_dir.mkdir()

    # Create annotation with ROOT
    ann_content = """T0\tROOT 0 0\tROOT
T1\tNOUN 0 4\tWord
T2\tVERB 5 9\ttest
R1\tnsubj Arg1:T2 Arg2:T1
R2\troot Arg1:T0 Arg2:T2
"""
    (brat_dir / 'test.ann').write_text(ann_content, encoding='utf-8')
    (brat_dir / 'test.txt').write_text('Word test', encoding='utf-8')

    return brat_dir


@pytest.fixture
def multi_sentence_conllu(temp_dir: Path) -> Path:
    """Create a multi-sentence CoNLL-U file."""
    conllu_path = temp_dir / 'multi.conllu'
    content = """# sent_id = 1
# text = Word test
1	Word	word	NOUN	n-s---mn-	_	2	nsubj	_	_
2	test	test	VERB	v3spia---	_	0	root	_	_

# sent_id = 2
# text = Another sentence
1	Another	another	DET	d--------	_	2	det	_	_
2	sentence	sentence	NOUN	n-s---fn-	_	0	root	_	_

"""
    conllu_path.write_text(content, encoding='utf-8')
    return conllu_path
