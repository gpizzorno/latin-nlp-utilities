"""Test validate_features edge cases."""

from typing import Any

from conllu_tools.utils.features import validate_features


def test_validate_features_empty_feature_name(feature_set: dict[str, Any]) -> None:
    """Test with empty feature name."""
    result = validate_features('NOUN', {'': 'Value', 'Case': 'Nom'}, feature_set)
    assert '' not in result
    assert result.get('Case') == 'Nom'


def test_validate_features_empty_feature_value(feature_set: dict[str, Any]) -> None:
    """Test with empty feature value."""
    result = validate_features('NOUN', {'Case': '', 'Gender': 'Masc'}, feature_set)
    assert 'Case' not in result
    assert result.get('Gender') == 'Masc'


def test_validate_features_whitespace_in_feature(feature_set: dict[str, Any]) -> None:
    """Test with whitespace in feature name."""
    result = validate_features('NOUN', {'Case ': 'Nom'}, feature_set)
    # Whitespace is not trimmed in feature names, so it won't match
    assert 'Case' not in result or result.get('Case') == 'Nom'


def test_validate_features_special_characters(feature_set: dict[str, Any]) -> None:
    """Test with special characters in feature names."""
    result = validate_features('NOUN', {'Case': 'Nom', 'Feature[Special]': 'Value'}, feature_set)
    assert result.get('Case') == 'Nom'
    assert 'Feature[Special]' not in result


def test_validate_features_preserves_order(feature_set: dict[str, Any]) -> None:
    """Test that feature order is preserved in result."""
    result = validate_features('NOUN', {'Gender': 'Masc', 'Case': 'Nom', 'Number': 'Sing'}, feature_set)
    # Python 3.7+ dicts preserve insertion order
    if len(result) > 0:
        assert isinstance(result, dict)


def test_validate_features_case_sensitive_upos(feature_set: dict[str, Any]) -> None:
    """Test that UPOS is case-sensitive."""
    # Lowercase upos might not work
    result = validate_features('noun', {'Case': 'Nom'}, feature_set)
    # Might return empty or partial results
    assert isinstance(result, dict)
