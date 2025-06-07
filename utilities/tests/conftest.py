"""Configure pytest fixtures."""

import io

import pytest


@pytest.fixture
def conllu_file(tmp_path):
    content = 'Marcus NNP B-PER\nTullius NNP I-PER\nCicero NNP I-PER\nin IN O\nRoma NNP B-LOC\n. . O\n\n'
    file_path = tmp_path / 'test.conllu'
    file_path.write_text(content, encoding='utf-8')
    return file_path


@pytest.fixture
def conllu_sentence():
    return (
        '# sent_id = 2\n'
        '# text = nec ab alio:\n'
        '1\tnec\tnec\tCCONJ\tO4\t_\t3\tcc\t3:cc\t_\n'
        '2\tab\tab\tADP\tS4|vgr2\tAdpType=Prep\t3\tcase\t3:case\t_\n'
        '3\talio\talius\tNOUN\tF1|grn1|casF|gen3\tCase=Abl|Gender=Neut|Number=Sing\t0\troot\t_\tSpaceAfter=No\n'
        '4\t:\t:\tPUNCT\tPunc\t_\t3\tpunct\t2:punct\t_\n'
        '\n'
    )


@pytest.fixture
def conllu_stream(conllu_sentence):
    return io.StringIO(conllu_sentence)


# Mock for upos_to_tag
@pytest.fixture(autouse=True)
def patch_upos_to_tag(monkeypatch):
    monkeypatch.setattr('utilities.converters.upos_to_perseus', lambda upos: upos.lower())


@pytest.fixture
def treebank_type():
    return {
        'no_gapping': 0,
        'no_shared_parents_in_coordination': 0,
        'no_shared_dependents_in_coordination': 0,
        'no_control': 0,
        'no_external_arguments_of_relative_clauses': 0,
        'no_case_info': 0,
    }
