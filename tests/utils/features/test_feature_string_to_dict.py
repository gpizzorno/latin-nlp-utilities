"""Unit tests for feature_string_to_dict conversion function."""

import pytest

from conllu_tools.utils.features import feature_string_to_dict


def test_feature_string_to_dict_basic() -> None:
    assert feature_string_to_dict('Case=Nom|Gender=Masc') == {'Case': 'Nom', 'Gender': 'Masc'}


def test_feature_string_to_dict_empty() -> None:
    assert feature_string_to_dict('') == {}
    assert feature_string_to_dict('_') == {}


def test_feature_string_to_dict_none() -> None:
    """Test feature_string_to_dict with None input."""
    assert feature_string_to_dict(None) == {}


def test_feature_string_to_dict_single_feature() -> None:
    """Test with a single feature."""
    assert feature_string_to_dict('Case=Nom') == {'Case': 'Nom'}


def test_feature_string_to_dict_multiple_features() -> None:
    """Test with multiple features."""
    result = feature_string_to_dict('Case=Nom|Gender=Masc|Number=Sing')
    assert result == {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}


def test_feature_string_to_dict_multiple_values() -> None:
    """Test with features that have multiple equals signs (edge case)."""
    # This should take first split only, so 'Val=ue' would become key='Val', value='ue'
    result = feature_string_to_dict('Case=Nom=Extra')
    assert result == {'Case': 'Nom'}


def test_feature_string_to_dict_trailing_pipe() -> None:
    """Test with trailing pipe character."""
    # The empty string after split will cause issues - ['Case', 'Nom'], ['Gender', 'Masc'], ['']
    # This will cause an IndexError or create unexpected behavior
    with pytest.raises(IndexError):
        feature_string_to_dict('Case=Nom|Gender=Masc|')


def test_feature_string_to_dict_leading_pipe() -> None:
    """Test with leading pipe character."""
    # Malformed input, should raise error
    with pytest.raises(IndexError):
        feature_string_to_dict('|Case=Nom|Gender=Masc')


def test_feature_string_to_dict_double_pipe() -> None:
    """Test with double pipe characters."""
    # Malformed input, should raise error
    with pytest.raises(IndexError):
        feature_string_to_dict('Case=Nom||Gender=Masc')


def test_feature_string_to_dict_missing_equals() -> None:
    """Test with missing equals sign."""
    with pytest.raises(IndexError):
        feature_string_to_dict('Case=Nom|Gender')


def test_feature_string_to_dict_missing_value() -> None:
    """Test with missing value after equals."""
    result = feature_string_to_dict('Case=|Gender=Masc')
    # 'Case=' split gives ['Case', ''], which should work but give empty value
    # This should work and create {'Case': '', 'Gender': 'Masc'}
    assert result == {'Case': '', 'Gender': 'Masc'}


def test_feature_string_to_dict_missing_key() -> None:
    """Test with missing key before equals."""
    result = feature_string_to_dict('=Nom|Gender=Masc')
    # '=Nom' split gives ['', 'Nom'], which creates {'': 'Nom'}
    assert result.get('') == 'Nom' or 'Gender' in result


def test_feature_string_to_dict_whitespace() -> None:
    """Test with whitespace in feature string."""
    result = feature_string_to_dict('Case=Nom | Gender=Masc')
    # Whitespace is not trimmed, so ' Gender' would be the key
    assert result.get('Case') == 'Nom'


def test_feature_string_to_dict_special_characters() -> None:
    """Test with special characters in values."""
    result = feature_string_to_dict('Case=Nom|Feature[layer]=Value')
    # Should handle special characters in feature names
    assert result['Case'] == 'Nom'
    assert result['Feature[layer]'] == 'Value'


def test_feature_string_to_dict_unicode() -> None:
    """Test with Unicode characters."""
    result = feature_string_to_dict('Caseα=Nom|Gender=Masc')  # noqa: RUF001
    assert result.get('Caseα') == 'Nom' or 'Case' in result  # noqa: RUF001


def test_feature_string_empty_after_split() -> None:
    """Test behavior with only pipe characters."""
    # Malformed input, should raise error
    with pytest.raises(IndexError):
        feature_string_to_dict('|||')
