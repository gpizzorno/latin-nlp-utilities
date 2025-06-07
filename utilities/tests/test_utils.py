import hashlib

import pytest

from utilities import utils


def test_feature_string_to_dict_basic():
    assert utils.feature_string_to_dict('Case=Nom|Gender=Masc') == {'Case': 'Nom', 'Gender': 'Masc'}


def test_feature_string_to_dict_empty():
    assert utils.feature_string_to_dict('') == {}
    assert utils.feature_string_to_dict('_') == {}


def test_feature_dict_to_string_basic():
    d = {'Gender': 'Masc', 'Case': 'Nom'}
    # Should be sorted alphabetically by key (case-insensitive)
    assert utils.feature_dict_to_string(d) == 'Case=Nom|Gender=Masc'


def test_feature_dict_to_string_empty():
    assert utils.feature_dict_to_string({}) == '_'


def test_normalize_features_valid():
    featset = {
        'Case': {
            'byupos': {
                'noun': {'Nom': 1, 'Acc': 1},
                'verb': {'Nom': 0},
            },
        },
        'Gender': {
            'byupos': {
                'noun': {'Masc': 1, 'Fem': 1},
            },
        },
    }
    features = {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}
    result = utils.normalize_features('noun', features, featset)
    assert result == {'Case': 'Nom', 'Gender': 'Masc'}


def test_normalize_features_string_input():
    featset = {
        'Case': {
            'byupos': {
                'noun': {'Nom': 1},
            },
        },
    }
    features = 'Case=Nom|Number=Sing'
    result = utils.normalize_features('noun', features, featset)
    assert result == {'Case': 'Nom'}


def test_normalize_features_missing_upos_or_featset():
    with pytest.raises(ValueError):  # noqa: PT011
        utils.normalize_features(None, {}, {})
    with pytest.raises(ValueError):  # noqa: PT011
        utils.normalize_features('NOUN', {}, None)


def test_normalize_features_none_features():
    featset = {'Case': {'byupos': {'noun': {'Nom': 1}}}}
    assert utils.normalize_features('noun', None, featset) is None


def test_normalize_xpos_valid():
    upos = 'NOUN'
    xpos = 'Nabcde'
    result = utils.normalize_xpos(upos, xpos)
    # Based on the actual output, it appears only first char of upos_tag is used
    assert result == 'n-b---'


def test_normalize_xpos_missing_args():
    with pytest.raises(ValueError):  # noqa: PT011
        utils.normalize_xpos(None, 'Xabc')
    with pytest.raises(ValueError):  # noqa: PT011
        utils.normalize_xpos('NOUN', '')


def test_get_md5(tmp_path):
    # Create a temp file
    file_path = tmp_path / 'test.txt'
    content = b'hello world'
    file_path.write_bytes(content)
    expected = hashlib.md5(content).hexdigest()
    assert utils.get_md5(str(file_path)) == expected
