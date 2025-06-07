import pytest

from utilities.conllubio2brat import conllubio_to_brat


def test_basic_conversion(conllu_file, tmp_path):
    outdir = tmp_path / 'brat'
    outdir.mkdir()
    conllubio_to_brat(str(conllu_file), str(outdir))
    txt_file = outdir / 'test.conllu-doc-001.txt'
    ann_file = outdir / 'test.conllu-doc-001.ann'
    assert txt_file.exists()
    assert ann_file.exists()
    txt = txt_file.read_text(encoding='utf-8')
    ann = ann_file.read_text(encoding='utf-8')
    # Check text reconstruction
    assert 'Marcus Tullius Cicero in Roma.' in txt
    # Check annotation format
    assert 'T1\tPER 0 21\tMarcus Tullius Cicero' in ann
    assert 'T2\tLOC 25 29\tRoma' in ann


def test_multiple_sentences(tmp_path):
    content = (
        'Lucius NNP B-PER\n'
        'Annaeus NNP I-PER\n'
        'Seneca NNP I-PER\n'
        '. . O\n'
        '\n'
        'Gallia NNP B-LOC\n'
        'est VBZ O\n'
        'provincia NNP O\n'
        '. . O\n'
        '\n'
    )
    file_path = tmp_path / 'multi.conllu'
    file_path.write_text(content, encoding='utf-8')
    outdir = tmp_path / 'brat2'
    outdir.mkdir()
    conllubio_to_brat(str(file_path), str(outdir))
    txt_file = outdir / 'multi.conllu-doc-001.txt'
    ann_file = outdir / 'multi.conllu-doc-001.ann'
    txt = txt_file.read_text(encoding='utf-8')
    ann = ann_file.read_text(encoding='utf-8')
    assert 'Lucius Annaeus Seneca.' in txt
    assert 'Gallia est provincia.' in txt
    assert 'T1\tPER 0 21\tLucius Annaeus Seneca' in ann
    assert 'T2\tLOC 23 29\tGallia' in ann


def test_document_split(tmp_path):
    content = 'Aulus NNP B-PER\nGellius NNP I-PER\n. . O\n\n=== O\nRoma NNP B-LOC\n. . O\n\n'
    file_path = tmp_path / 'split.conllu'
    file_path.write_text(content, encoding='utf-8')
    outdir = tmp_path / 'brat3'
    outdir.mkdir()
    conllubio_to_brat(str(file_path), str(outdir))
    txt1 = (outdir / 'split.conllu-doc-001.txt').read_text(encoding='utf-8')
    txt2 = (outdir / 'split.conllu-doc-002.txt').read_text(encoding='utf-8')
    ann1 = (outdir / 'split.conllu-doc-001.ann').read_text(encoding='utf-8')
    ann2 = (outdir / 'split.conllu-doc-002.ann').read_text(encoding='utf-8')
    assert 'Aulus Gellius.' in txt1
    assert 'Roma.' in txt2
    assert 'PER' in ann1
    assert 'LOC' in ann2


def test_no_entities(tmp_path):
    content = 'Salve UH O\namicus NN O\n. . O\n\n'
    file_path = tmp_path / 'noent.conllu'
    file_path.write_text(content, encoding='utf-8')
    outdir = tmp_path / 'brat4'
    outdir.mkdir()
    conllubio_to_brat(str(file_path), str(outdir))
    txt = (outdir / 'noent.conllu-doc-001.txt').read_text(encoding='utf-8')
    ann = (outdir / 'noent.conllu-doc-001.ann').read_text(encoding='utf-8')
    assert 'Salve amicus.' in txt
    assert ann.strip() == ''


def test_invalid_format(tmp_path):
    content = 'ThisIsWrongFormat\n'
    file_path = tmp_path / 'bad.conllu'
    file_path.write_text(content, encoding='utf-8')
    outdir = tmp_path / 'brat5'
    outdir.mkdir()
    with pytest.raises(AssertionError):
        conllubio_to_brat(str(file_path), str(outdir))
