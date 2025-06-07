import json
from unittest import mock

import pytest

from utilities.brat2conllu import (
    brat_to_conllu,
    conll2lists,
    conllu,
    fix_annotations,
    get_best_fit_morpho,
    get_sentence_text,
    join_annotations,
    load_reference_corpus,
    parse_id,
    parse_key_value,
    remap_attrib_idrefs,
    remap_key_values,
    remap_relation_idrefs,
)


def test_parse_id_valid():
    assert parse_id('T12\tNOUN 0 4\tpuer') == ('T12', 'T', '12')
    assert parse_id('R2\tdep Arg1:T1 Arg2:T2') == ('R2', 'R', '2')
    assert parse_id('#1\tAnnotatorNotes T1\tSome note') == ('#1', '#', '1')


def test_parse_id_invalid():
    with pytest.raises(AssertionError):
        parse_id('invalid_line')


def test_parse_key_value_valid():
    assert parse_key_value('Arg1:T1') == ('Arg1', 'T1')
    assert parse_key_value('Arg2:T2') == ('Arg2', 'T2')


def test_parse_key_value_invalid():
    with pytest.raises(AssertionError):
        parse_key_value('Arg1-T1')


def test_remap_key_values():
    kvs = ['Arg1:T1', 'Arg2:T2']
    idmap = {'T1': 'T10', 'T2': 'T20'}
    result = remap_key_values(kvs, idmap)
    assert result == ['Arg1:T10', 'Arg2:T20']


def test_remap_relation_idrefs():
    line = 'R1\tdep Arg1:T1 Arg2:T2'
    idmap = {'T1': 'T10', 'T2': 'T20'}
    result = remap_relation_idrefs(line, idmap)
    assert result == 'R1\tdep Arg1:T10 Arg2:T20'


def test_remap_attrib_idrefs():
    line = 'A1\tNegation T1'
    idmap = {'T1': 'T10'}
    result = remap_attrib_idrefs(line, idmap)
    assert result == 'A1\tNegation T10'


def test_fix_annotations_basic():
    annotations = [
        'T2\tNOUN 5 10\tpuella',
        'T1\tVERB 0 4\tamat',
        'R1\tdep Arg1:T1 Arg2:T2',
        '#1\tAnnotatorNotes T1\tSome note',
    ]
    fixed = fix_annotations(annotations)
    # Should sort textbound by offset, renumber T2->T1, T1->T2, and update relation
    assert any('T1\tVERB 0 4\tamat' in line for line in fixed)
    assert any('T2\tNOUN 5 10\tpuella' in line for line in fixed)
    assert any('R1\tdep Arg1:T1 Arg2:T2' in line for line in fixed)
    assert any('#1\tAnnotatorNotes T1\tSome note' in line for line in fixed)


def test_get_sentence_text():
    conll_list = [
        [1, 'Puella', '_', '_', '_', '_', 2, 'nsubj', '_', '_'],
        [2, 'amat', '_', '_', '_', '_', 0, 'root', '_', '_'],
        [3, '.', '_', '_', '_', '_', 2, 'punct', '_', '_'],
    ]
    assert get_sentence_text(conll_list) == 'Puella amat.'


def test_get_best_fit_morpho_found():
    # Mock reference_corpus[0].filter to return tokens with xpos and feats
    mock_token = {'xpos': 'NOUN', 'feats': {'Case': 'Nom'}}

    class MockSentence:
        def filter(self, **kwargs):  # noqa: ARG002
            return [mock_token]

    reference_corpus = [MockSentence()]
    with (
        mock.patch('utilities.brat2conllu.normalize_xpos') as mock_normalize_xpos,
        mock.patch('utilities.brat2conllu.normalize_features') as mock_normalize_features,
        mock.patch('utilities.brat2conllu.feature_dict_to_string') as mock_feature_dict_to_string,
    ):
        # Mock the normalization functions
        mock_normalize_xpos.return_value = 'NOUN_norm'
        mock_normalize_features.return_value = {'Case': 'Nom'}
        mock_feature_dict_to_string.return_value = 'Case=Nom'

        result = get_best_fit_morpho('puella', 'NOUN', reference_corpus, {})
        assert result == ('NOUN_norm', 'Case=Nom')


def test_get_best_fit_morpho_not_found():
    class MockSentence:
        def filter(self, **kwargs):  # noqa: ARG002
            return []

    reference_corpus = [MockSentence()]
    result = get_best_fit_morpho('puella', 'NOUN', reference_corpus, {})
    assert result == (None, None)


def test_conll2lists(tmp_path):
    # Create a minimal CoNLL-U file
    content = (
        '# sent_id = s1\n'
        '1\tPuella\t_\tNOUN\t_\t_\t2\tnsubj\t_\t_\n'
        '2\tamat\t_\tVERB\t_\t_\t0\troot\t_\t_\n'
        '\n'
        '# sent_id = s2\n'
        '1\tPuer\t_\tNOUN\t_\t_\t2\tnsubj\t_\t_\n'
        '2\tcurrit\t_\tVERB\t_\t_\t0\troot\t_\t_\n'
        '\n'
    )
    file = tmp_path / 'test.conllu'
    file.write_text(content)
    ids, sentences, concordance = conll2lists(str(file))
    assert ids == ['s1', 's2']
    assert len(sentences) == 2  # noqa: PLR2004
    assert 's1' in concordance
    assert 's2' in concordance


def test_load_reference_corpus(monkeypatch, tmp_path):
    # Patch conllu.parse to check call
    called = {}

    def fake_parse(_text):
        called['called'] = True
        return ['parsed']

    monkeypatch.setattr(conllu, 'parse', fake_parse)
    file = tmp_path / 'ref.conllu'
    file.write_text('dummy')
    result = load_reference_corpus(str(file))
    assert called['called']
    assert result == ['parsed']


def test_conll2lists_empty_file(tmp_path):
    file = tmp_path / 'empty.conllu'
    file.write_text('')
    ids, sentences, concordance = conll2lists(str(file))
    assert ids == []
    assert sentences == []
    assert concordance == {}


def test_conll2lists_no_sent_id(tmp_path):
    content = '# some comment\n1\tPuella\t_\tNOUN\t_\t_\t2\tnsubj\t_\t_\n2\tamat\t_\tVERB\t_\t_\t0\troot\t_\t_\n\n'
    file = tmp_path / 'no_sent_id.conllu'
    file.write_text(content)
    ids, sentences, concordance = conll2lists(str(file))
    assert ids == []
    assert sentences == [
        [
            ['1', 'Puella', '_', 'NOUN', '_', '_', '2', 'nsubj', '_', '_'],
            ['2', 'amat', '_', 'VERB', '_', '_', '0', 'root', '_', '_'],
        ],
    ]


def test_parse_key_value_edge_cases():
    # Test with numbers and special characters
    assert parse_key_value('Arg1:T123') == ('Arg1', 'T123')
    assert parse_key_value('Type:value') == ('Type', 'value')


def test_parse_key_value_malformed():
    with pytest.raises(AssertionError, match='Failed to parse key-value pair'):
        parse_key_value('malformed')
    with pytest.raises(AssertionError, match='Failed to parse key-value pair'):
        parse_key_value('key=value')  # wrong separator


def test_fix_annotations_unknown_category():
    annotations = ['X1\tunknown annotation']
    with pytest.raises(ValueError, match='Unknown annotation category X'):
        fix_annotations(annotations)


def test_fix_annotations_complex_scenario():
    annotations = [
        'T5\tNOUN 10 15\tpuella',
        'T1\tVERB 0 4\tamat',
        'T3\tNOUN 6 9\tvia',
        'R2\tdep Arg1:T1 Arg2:T5',
        'R1\tnmod Arg1:T5 Arg2:T3',
        '#1\tNote T3\tSome note',
    ]
    fixed = fix_annotations(annotations)

    # Should sort by offset and renumber: T1(0-4)->T1, T3(6-9)->T2, T5(10-15)->T3
    textbound_lines = [line for line in fixed if line.startswith('T')]
    assert 'T1\tVERB 0 4\tamat' in textbound_lines[0]
    assert 'T2\tNOUN 6 9\tvia' in textbound_lines[1]
    assert 'T3\tNOUN 10 15\tpuella' in textbound_lines[2]

    # Relations should be updated accordingly - check the actual remapping
    relation_lines = [line for line in fixed if line.startswith('R')]
    # R2: T1->T1, T5->T3, so becomes "dep Arg1:T1 Arg2:T3"
    # R1: T5->T3, T3->T2, so becomes "nmod Arg1:T3 Arg2:T2"
    # But they're sorted by original ID, so R1 comes first
    assert 'R1\tnmod Arg1:T3 Arg2:T2' in relation_lines[0]
    assert 'R2\tdep Arg1:T1 Arg2:T3' in relation_lines[1]


def test_join_annotations_comprehensive(tmp_path):
    # Create first annotation file
    ann1 = tmp_path / 'doc1.ann'
    ann1.write_text(
        'T1\tNOUN 0 6\tMarcus\nT2\tVERB 7 11\tamat\nR1\tnsubj Arg1:T2 Arg2:T1\n#1\tNote T1\tProper noun\n',
    )
    txt1 = tmp_path / 'doc1.txt'
    txt1.write_text('Marcus amat.\n')  # 13 characters including newline

    # Create second annotation file
    ann2 = tmp_path / 'doc2.ann'
    ann2.write_text(
        'T1\tNOUN 0 6\tPuella\nT2\tVERB 7 13\tcurrit\nR1\tnsubj Arg1:T2 Arg2:T1\n',
    )
    txt2 = tmp_path / 'doc2.txt'
    txt2.write_text('Puella currit.\n')  # 15 characters including newline

    result = join_annotations([str(ann1), str(ann2)])

    # Check that we have all annotations
    textbound = [ann for ann in result if ann[0].startswith('T')]
    relations = [ann for ann in result if ann[0].startswith('R')]
    comments = [ann for ann in result if ann[0].startswith('#')]

    assert len(textbound) == 4  # 2 from each file  # noqa: PLR2004
    assert len(relations) == 2  # 1 from each file  # noqa: PLR2004
    assert len(comments) == 1  # 1 from first file

    doc2_annotations = [ann for ann in textbound if len(ann) > 2 and ('Puella' in ann[4] or 'currit' in ann[4])]  # noqa: PLR2004
    assert doc2_annotations, f'doc2_annotations: {doc2_annotations}'
    puella_ann = next((ann for ann in doc2_annotations if 'Puella' in ann[4]), None)
    currit_ann = next((ann for ann in doc2_annotations if 'currit' in ann[4]), None)
    assert puella_ann is not None, 'Puella annotation not found'
    assert currit_ann is not None, 'currit annotation not found'
    assert '13 19' in puella_ann[3]
    assert '20 26' in currit_ann[3]


def test_join_annotations_id_collision(tmp_path):
    # Both files have T1, should be renumbered
    ann1 = tmp_path / 'doc1.ann'
    ann1.write_text('T1\tNOUN 0 3\tfoo\n')
    txt1 = tmp_path / 'doc1.txt'
    txt1.write_text('foo\n')

    ann2 = tmp_path / 'doc2.ann'
    ann2.write_text('T1\tVERB 0 3\tbar\n')
    txt2 = tmp_path / 'doc2.txt'
    txt2.write_text('bar\n')

    result = join_annotations([str(ann1), str(ann2)])

    # Should have T1 and T2 (second file's T1 renamed)
    ids = [ann[0] + ann[1] for ann in result if ann[0] == 'T']
    assert 'T1' in ids
    assert 'T2' in ids


def test_join_annotations_discontinuous_spans(tmp_path):
    ann1 = tmp_path / 'doc1.ann'
    ann1.write_text('T1\tNOUN 0 3;5 8\tfoo bar\n')
    txt1 = tmp_path / 'doc1.txt'
    txt1.write_text('foo bar\n')

    result = join_annotations([str(ann1)])

    # Check that discontinuous spans are preserved
    textbound = next(ann for ann in result if ann[0].startswith('T'))
    # The offsets field is now always at index 3
    assert '0 3;5 8' in textbound[3]


def test_brat_to_conllu_basic(tmp_path):
    # Create input directory with annotation files
    input_dir = tmp_path / 'input'
    input_dir.mkdir()

    # Create conllu directory with reference file
    conllu_dir = tmp_path / 'conllu'
    conllu_dir.mkdir()

    # Create basic annotation file
    ann_file = input_dir / 'test_rawdep-doc-001.ann'  # Use proper naming pattern
    ann_file.write_text(
        'T1\tNOUN 0 6\tMarcus\n'
        'T2\tVERB 7 11\tamat\n'
        'T3\tNOUN 12 19\tpuellam\n'
        'T4\tPUNCT 19 20\t.\n'
        'T999\tROOT 21 25\tROOT\n'  # Sentence separator
        'R1\tnsubj Arg1:T2 Arg2:T1\n'
        'R2\tobj Arg1:T2 Arg2:T3\n'
        'R3\tpunct Arg1:T2 Arg2:T4\n',
    )

    # Create corresponding text file
    txt_file = input_dir / 'test_rawdep-doc-001.txt'
    txt_file.write_text('Marcus amat puellam. ROOT')

    # Create reference CoNLL-U file
    conllu_file = conllu_dir / 'test_basic.conllu'
    conllu_file.write_text(
        '# sent_id = s1\n'
        '1\tMarcus\tmarcus\tNOUN\tNoun\tCase=Nom\t2\tnsubj\t2:nsubj\t_\n'
        '2\tamat\tamo\tVERB\tVerb\tNumber=Sing\t0\troot\t0:root\t_\n'
        '3\tpuellam\tpuella\tNOUN\tNoun\tCase=Acc\t2\tobj\t2:obj\t_\n'
        '4\t.\t.\tPUNCT\tPunct\t_\t2\tpunct\t2:punct\t_\n'
        '\n',
    )

    # Create reference corpus file
    ref_corpus = tmp_path / 'reference.conllu'
    ref_corpus.write_text(
        '1\tMarcus\tmarcus\tNOUN\tNoun\tCase=Nom\t2\tnsubj\t2:nsubj\t_\n'
        '2\tamat\tamo\tVERB\tVerb\tNumber=Sing\t0\troot\t0:root\t_\n'
        '\n',
    )

    with mock.patch('utilities.brat2conllu.load_lang_features') as mock_load_features:
        mock_load_features.return_value = {}

        # Run the conversion
        brat_to_conllu(
            str(input_dir),
            str(conllu_dir),
            'la',
            reference_corpus_path=str(ref_corpus),
        )

    # Check output file was created
    output_file = conllu_dir / 'test_fixeddep.conllu'
    assert output_file.exists()

    content = output_file.read_text()
    assert '# sent_id = s1' in content
    assert 'Marcus' in content
    assert 'amat' in content


def test_brat_to_conllu_aux_correction(tmp_path):
    input_dir = tmp_path / 'input'
    input_dir.mkdir()
    conllu_dir = tmp_path / 'conllu'
    conllu_dir.mkdir()

    # Create annotation with aux relation
    ann_file = input_dir / 'test_basic-doc-001.ann'
    ann_file.write_text(
        'T1\tNOUN 0 6\tMarcus\n'
        'T2\tVERB 7 10\test\n'  # Should become AUX
        'T3\tVERB 11 18\tcurrit\n'
        'T4\tPUNCT 19 20\t.\n'
        'T999\tROOT 21 25\tROOT\n'
        'R1\tnsubj Arg1:T3 Arg2:T1\n'
        'R2\taux Arg1:T3 Arg2:T2\n'  # aux relation triggers UPOS change
        'R3\tpunct Arg1:T3 Arg2:T4\n',
    )

    txt_file = input_dir / 'test_basic-doc-001.txt'
    txt_file.write_text('Marcus est currit. ROOT')

    conllu_file = conllu_dir / 'test_basic.conllu'
    conllu_file.write_text(
        '# sent_id = s1\n'
        '1\tMarcus\tmarcus\tNOUN\tNoun\tCase=Nom\t3\tnsubj\t3:nsubj\t_\n'
        '2\test\tsum\tVERB\tVerb\tNumber=Sing\t3\taux\t3:aux\t_\n'
        '3\tcurrit\tcurro\tVERB\tVerb\tNumber=Sing\t0\troot\t0:root\t_\n'
        '4\t.\t.\tPUNCT\tPunct\t_\t3\tpunct\t3:punct\t_\n'
        '\n',
    )

    ref_corpus = tmp_path / 'reference.conllu'
    ref_corpus.write_text('')

    with mock.patch('utilities.brat2conllu.load_lang_features') as mock_load_features:
        mock_load_features.return_value = {}

        brat_to_conllu(
            str(input_dir),
            str(conllu_dir),
            'la',
            reference_corpus_path=str(ref_corpus),
        )

    output_file = conllu_dir / 'test_fixeddep.conllu'
    content = output_file.read_text()

    # Check that 'est' was changed from VERB to AUX
    lines = content.split('\n')
    est_line = next(line for line in lines if line.startswith('2\test'))
    assert '\tAUX\t' in est_line


def test_brat_to_conllu_enhanced_deps(tmp_path):
    input_dir = tmp_path / 'input'
    input_dir.mkdir()
    conllu_dir = tmp_path / 'conllu'
    conllu_dir.mkdir()

    ann_file = input_dir / 'test_rawdep-doc-001.ann'
    ann_file.write_text(
        'T1\tNOUN 0 6\tMarcus\n'
        'T2\tVERB 7 11\tamat\n'
        'T3\tNOUN 12 19\tpuellam\n'
        'T999\tROOT 20 24\tROOT\n'
        'R1\tnsubj Arg1:T2 Arg2:T1\n'
        'R2\tobj Arg1:T2 Arg2:T3\n'
        'R3\tconj Arg1:T1 Arg2:T3\n',  # Additional enhanced dependency
    )

    txt_file = input_dir / 'test_rawdep-doc-001.txt'
    txt_file.write_text('Marcus amat puellam ROOT')

    conllu_file = conllu_dir / 'test_basic.conllu'
    conllu_file.write_text(
        '# sent_id = s1\n'
        '1\tMarcus\tmarcus\tNOUN\tNoun\tCase=Nom\t2\tnsubj\t2:nsubj\t_\n'
        '2\tamat\tamo\tVERB\tVerb\tNumber=Sing\t0\troot\t0:root\t_\n'
        '3\tpuellam\tpuella\tNOUN\tNoun\tCase=Acc\t2\tobj\t2:obj\t_\n'
        '\n',
    )

    ref_corpus = tmp_path / 'reference.conllu'
    ref_corpus.write_text('')

    with mock.patch('utilities.brat2conllu.load_lang_features') as mock_load_features:
        mock_load_features.return_value = {}

        brat_to_conllu(
            str(input_dir),
            str(conllu_dir),
            'la',
            reference_corpus_path=str(ref_corpus),
        )

    output_file = conllu_dir / 'test_fixeddep.conllu'
    content = output_file.read_text()

    # Check enhanced dependencies are included
    lines = content.split('\n')
    puellam_line = next(line for line in lines if line.startswith('3\tpuellam'))
    # Should have both basic dependency and enhanced dependency
    assert '1:conj|2:obj' in puellam_line or '2:obj|1:conj' in puellam_line


def test_brat_to_conllu_concordance_file(tmp_path):
    input_dir = tmp_path / 'input'
    input_dir.mkdir()
    conllu_dir = tmp_path / 'conllu'
    conllu_dir.mkdir()

    ann_file = input_dir / 'test_rawdep-doc-001.ann'
    ann_file.write_text(
        'T1\tNOUN 0 6\tMarcus\nT2\tVERB 7 11\tamat\nT999\tROOT 12 16\tROOT\nR1\tnsubj Arg1:T2 Arg2:T1\n',
    )

    txt_file = input_dir / 'test_rawdep-doc-001.txt'
    txt_file.write_text('Marcus amat ROOT')

    conllu_file = conllu_dir / 'test_basic.conllu'
    conllu_file.write_text(
        '# sent_id = s1\n'
        '1\tMarcus\tmarcus\tNOUN\tNoun\tCase=Nom\t2\tnsubj\t2:nsubj\t_\n'
        '2\tamat\tamo\tVERB\tVerb\tNumber=Sing\t0\troot\t0:root\t_\n'
        '\n',
    )

    ref_corpus = tmp_path / 'reference.conllu'
    ref_corpus.write_text('')

    with mock.patch('utilities.brat2conllu.load_lang_features') as mock_load_features:
        mock_load_features.return_value = {}

        brat_to_conllu(
            str(input_dir),
            str(conllu_dir),
            'la',
            reference_corpus_path=str(ref_corpus),
        )

    # Check concordance file was created
    concordance_file = input_dir / 'brat_conllu_sentence_concordance.json'
    assert concordance_file.exists()

    with open(concordance_file) as f:
        concordance = json.load(f)

    assert 's1' in concordance
    assert 'alt_id' in concordance['s1']
    assert 'order' in concordance['s1']


def test_brat_to_conllu_token_mismatch(tmp_path):
    input_dir = tmp_path / 'input'
    input_dir.mkdir()
    conllu_dir = tmp_path / 'conllu'
    conllu_dir.mkdir()

    ann_file = input_dir / 'test-doc-001.ann'
    ann_file.write_text(
        'T1\tNOUN 0 6\tMarcus\n'  # This doesn't match CoNLL-U
        'T999\tROOT 7 11\tROOT\n',
    )

    txt_file = input_dir / 'test-doc-001.txt'
    txt_file.write_text('Marcus ROOT')

    conllu_file = conllu_dir / 'test.conllu'
    conllu_file.write_text(
        '# sent_id = s1\n'
        '1\tPuella\tpuella\tNOUN\tNoun\tCase=Nom\t0\troot\t0:root\t_\n'  # Different token
        '\n',
    )

    ref_corpus = tmp_path / 'reference.conllu'
    ref_corpus.write_text('')

    with mock.patch('utilities.brat2conllu.load_lang_features') as mock_load_features:
        mock_load_features.return_value = {}

        with pytest.raises(AssertionError, match='token mismatch'):
            brat_to_conllu(
                str(input_dir),
                str(conllu_dir),
                'la',
                reference_corpus_path=str(ref_corpus),
            )
