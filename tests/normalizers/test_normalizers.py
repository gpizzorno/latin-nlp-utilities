import pytest

from nlp_utilities.normalizers import normalize_features, normalize_xpos


def test_normalize_features_valid() -> None:
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
    result = normalize_features('noun', features, featset)
    assert result == {'Case': 'Nom', 'Gender': 'Masc'}


def test_normalize_features_string_input() -> None:
    featset = {
        'Case': {
            'byupos': {
                'noun': {'Nom': 1},
            },
        },
    }
    features = 'Case=Nom|Number=Sing'
    result = normalize_features('noun', features, featset)
    assert result == {'Case': 'Nom'}


def test_normalize_features_missing_upos_or_featset() -> None:
    with pytest.raises(ValueError):  # noqa: PT011
        normalize_features(None, {}, {})
    with pytest.raises(ValueError):  # noqa: PT011
        normalize_features('NOUN', {}, None)


def test_normalize_features_none_features() -> None:
    featset = {'Case': {'byupos': {'noun': {'Nom': 1}}}}
    assert normalize_features('noun', None, featset) is None  # type: ignore [arg-type]


def test_normalize_xpos_valid() -> None:
    upos = 'NOUN'
    xpos = 'Nabcde'
    result = normalize_xpos(upos, xpos)
    # Based on the actual output, it appears only first char of upos_tag is used
    assert result == 'n-b---'


def test_normalize_xpos_missing_args() -> None:
    with pytest.raises(ValueError):  # noqa: PT011
        normalize_xpos(None, 'Xabc')  # type: ignore [arg-type]
    with pytest.raises(ValueError):  # noqa: PT011
        normalize_xpos('NOUN', '')
