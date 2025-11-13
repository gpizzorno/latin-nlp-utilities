"""Unit tests for feature string and dictionary conversion functions."""

from nlp_utilities.converters.features import feature_dict_to_string, feature_string_to_dict


def test_feature_dict_to_string_basic() -> None:
    d = {'Gender': 'Masc', 'Case': 'Nom'}
    # Should be sorted alphabetically by key (case-insensitive)
    assert feature_dict_to_string(d) == 'Case=Nom|Gender=Masc'


def test_feature_dict_to_string_empty() -> None:
    assert feature_dict_to_string({}) == '_'


def test_feature_dict_to_string_none() -> None:
    """Test feature_dict_to_string with None input."""
    assert feature_dict_to_string(None) == '_'


def test_feature_dict_to_string_single_feature() -> None:
    """Test with single feature dictionary."""
    result = feature_dict_to_string({'Case': 'Nom'})
    assert result == 'Case=Nom'


def test_feature_dict_to_string_case_insensitive_sort() -> None:
    """Test that sorting is case-insensitive."""
    d = {'case': 'nom', 'Gender': 'Masc', 'ASPECT': 'Perf'}
    result = feature_dict_to_string(d)
    # Should sort by lowercase version: aspect, case, gender
    assert result == 'ASPECT=Perf|case=nom|Gender=Masc'


def test_feature_dict_to_string_numeric_values() -> None:
    """Test with numeric values."""
    d = {'Person': '1', 'Number': 'Sing'}
    result = feature_dict_to_string(d)
    assert 'Person=1' in result
    assert 'Number=Sing' in result


def test_feature_dict_to_string_special_values() -> None:
    """Test with special character values."""
    d = {'Case': 'Nom', 'Misc': 'Val[1]'}
    result = feature_dict_to_string(d)
    assert 'Case=Nom' in result
    assert 'Misc=Val[1]' in result


def test_feature_dict_to_string_empty_value() -> None:
    """Test with empty string as value."""
    d = {'Case': '', 'Gender': 'Masc'}
    result = feature_dict_to_string(d)
    # Should still create Case= part
    assert 'Case=' in result
    assert 'Gender=Masc' in result


def test_feature_dict_to_string_empty_key() -> None:
    """Test with empty string as key."""
    d = {'': 'Value', 'Case': 'Nom'}
    result = feature_dict_to_string(d)
    # Should handle empty key
    assert '=Value' in result or result.startswith('=')


def test_feature_dict_to_string_many_features() -> None:
    """Test with many features to verify sorting."""
    d = {
        'Voice': 'Act',
        'Tense': 'Pres',
        'Person': '1',
        'Number': 'Sing',
        'Mood': 'Ind',
        'Aspect': 'Perf',
    }
    result = feature_dict_to_string(d)
    parts = result.split('|')
    # Should be sorted: Aspect, Mood, Number, Person, Tense, Voice
    assert parts[0].startswith('Aspect=')
    assert parts[1].startswith('Mood=')
    assert parts[2].startswith('Number=')
    assert parts[3].startswith('Person=')
    assert parts[4].startswith('Tense=')
    assert parts[5].startswith('Voice=')


def test_feature_roundtrip() -> None:
    """Test that dict -> string -> dict roundtrip works."""
    original = {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}
    string = feature_dict_to_string(original)
    result = feature_string_to_dict(string)
    assert result == original


def test_feature_roundtrip_with_sorting() -> None:
    """Test roundtrip with unsorted input."""
    # Input dictionary (unsorted)
    original = {'Number': 'Sing', 'Case': 'Nom', 'Gender': 'Masc'}
    # Convert to string (will be sorted)
    string = feature_dict_to_string(original)
    # Convert back to dict
    result = feature_string_to_dict(string)
    # Should have same content
    assert result == {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}
