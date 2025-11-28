"""Test text reconstruction with complex multiword token scenarios."""

from pathlib import Path

from conllu_tools.validation.validator import ConlluValidator
from tests.factories import ConlluSentenceFactory
from tests.helpers.assertion import assert_error_count, assert_no_errors_of_type


def test_basic_mwt(tmp_path: Path) -> None:
    """Test basic MWT text reconstruction (French 'au' = 'à le')."""
    tokens = [
        {
            'id': '1-2',
            'form': 'au',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 1,
            'form': 'à',
            'lemma': 'à',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'le',
            'lemma': 'le',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': 'Definite=Def|Gender=Masc|Number=Sing|PronType=Art',
            'head': 3,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'restaurant',
            'lemma': 'restaurant',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': 'Gender=Masc|Number=Sing',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(
        lang='fr',
        tmp_path=tmp_path,
        tokens=tokens,
        text='au restaurant',
    )
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    assert_no_errors_of_type(errors, 'text-mismatch')


def test_multiple_mwts(tmp_path: Path) -> None:
    """Test text reconstruction with multiple MWTs in one sentence."""
    tokens = [
        {
            'id': '1-2',
            'form': 'au',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 1,
            'form': 'à',
            'lemma': 'à',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'le',
            'lemma': 'le',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'café',
            'lemma': 'café',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': '4-5',
            'form': 'du',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'de',
            'lemma': 'de',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 6,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 5,
            'form': 'le',
            'lemma': 'le',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 6,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 6,
            'form': 'matin',
            'lemma': 'matin',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'nmod',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(
        lang='fr',
        tmp_path=tmp_path,
        tokens=tokens,
        text='au café du matin',
    )
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    assert_no_errors_of_type(errors, 'text-mismatch')


def test_mwt_with_spaceafter_no(tmp_path: Path) -> None:
    """Test MWT with SpaceAfter=No on the MWT token."""
    tokens = [
        {
            'id': '1-2',
            'form': 'al',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': 'SpaceAfter=No',
        },
        {
            'id': 1,
            'form': 'a',
            'lemma': 'a',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'il',
            'lemma': 'il',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'bar',
            'lemma': 'bar',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': 'SpaceAfter=No',
        },
        {
            'id': 4,
            'form': '.',
            'lemma': '.',
            'upostag': 'PUNCT',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'punct',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(
        lang='it',
        tmp_path=tmp_path,
        tokens=tokens,
        text='albar.',
    )
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    assert_no_errors_of_type(errors, 'text-mismatch')


def test_consecutive_mwts(tmp_path: Path) -> None:
    """Test consecutive MWTs with no space between them."""
    tokens = [
        {
            'id': '1-2',
            'form': 'del',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': 'SpaceAfter=No',
        },
        {
            'id': 1,
            'form': 'de',
            'lemma': 'de',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'el',
            'lemma': 'el',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 4,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': '3-4',
            'form': 'al',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'a',
            'lemma': 'a',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 6,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 4,
            'form': 'el',
            'lemma': 'el',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 6,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 5,
            'form': 'centro',
            'lemma': 'centro',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 6,
            'form': 'ciudad',
            'lemma': 'ciudad',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 5,
            'deprel': 'nmod',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(
        lang='es',
        tmp_path=tmp_path,
        tokens=tokens,
        text='delal centro ciudad',
    )
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    assert_no_errors_of_type(errors, 'text-mismatch')


def test_mwt_with_empty_nodes(tmp_path: Path) -> None:
    """Test MWT combined with empty nodes."""
    tokens = [
        {
            'id': '1-2',
            'form': 'dello',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 1,
            'form': 'di',
            'lemma': 'di',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'lo',
            'lemma': 'lo',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': '2.1',
            'form': '_',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'cop',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'stato',
            'lemma': 'stato',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(
        lang='it',
        tmp_path=tmp_path,
        tokens=tokens,
        text='dello stato',
    )
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    assert_no_errors_of_type(errors, 'text-mismatch')


def test_three_way_mwt(tmp_path: Path) -> None:
    """Test MWT splitting into three tokens."""
    tokens = [
        {
            'id': '1-3',
            'form': 'vámonos',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 1,
            'form': 'vamos',
            'lemma': 'ir',
            'upostag': 'VERB',
            'xpostag': '_',
            'feats': 'Mood=Imp|Number=Plur|Person=1',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'nos',
            'lemma': 'nos',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': 'Number=Plur|Person=1|PronType=Prs',
            'head': 1,
            'deprel': 'expl',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': '_',
            'lemma': '_',
            'upostag': 'PRON',
            'xpostag': '_',
            'feats': 'Number=Plur|Person=1|PronType=Prs',
            'head': 1,
            'deprel': 'obj',
            'deps': '_',
            'misc': '_',
        },
    ]
    test_file = ConlluSentenceFactory.as_file(
        lang='es',
        tmp_path=tmp_path,
        tokens=tokens,
        text='vámonos',
    )
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    assert_no_errors_of_type(errors, 'text-mismatch')


def test_mwt_reconstruction_error(tmp_path: Path) -> None:
    """Test that MWT reconstruction errors are caught."""
    tokens = [
        {
            'id': '1-2',
            'form': 'au',
            'lemma': '_',
            'upostag': '_',
            'xpostag': '_',
            'feats': '_',
            'head': '_',
            'deprel': '_',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 1,
            'form': 'à',
            'lemma': 'à',
            'upostag': 'ADP',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'case',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 2,
            'form': 'le',
            'lemma': 'le',
            'upostag': 'DET',
            'xpostag': '_',
            'feats': '_',
            'head': 3,
            'deprel': 'det',
            'deps': '_',
            'misc': '_',
        },
        {
            'id': 3,
            'form': 'restaurant',
            'lemma': 'restaurant',
            'upostag': 'NOUN',
            'xpostag': '_',
            'feats': '_',
            'head': 0,
            'deprel': 'root',
            'deps': '_',
            'misc': '_',
        },
    ]
    # Wrong text - includes component words instead of MWT
    test_file = ConlluSentenceFactory.as_file(
        lang='fr',
        tmp_path=tmp_path,
        tokens=tokens,
        text='à le restaurant',  # Should be 'au restaurant'
    )
    validator = ConlluValidator(level=2)
    errors = validator.validate_file(test_file)
    assert_error_count(errors, 1, 'text-mismatch')
