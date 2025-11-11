from nlp_utilities.converters.features import feature_dict_to_string, feature_string_to_dict


def test_feature_string_to_dict_basic() -> None:
    assert feature_string_to_dict('Case=Nom|Gender=Masc') == {'Case': 'Nom', 'Gender': 'Masc'}


def test_feature_string_to_dict_empty() -> None:
    assert feature_string_to_dict('') == {}
    assert feature_string_to_dict('_') == {}


def test_feature_dict_to_string_basic() -> None:
    d = {'Gender': 'Masc', 'Case': 'Nom'}
    # Should be sorted alphabetically by key (case-insensitive)
    assert feature_dict_to_string(d) == 'Case=Nom|Gender=Masc'


def test_feature_dict_to_string_empty() -> None:
    assert feature_dict_to_string({}) == '_'
