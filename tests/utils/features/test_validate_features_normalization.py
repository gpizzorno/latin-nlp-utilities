"""Test feature name and value normalization."""

from typing import Any

from conllu_tools.utils.features import validate_features


def test_validate_features_normalizes_feature_name_case(feature_set: dict[str, Any]) -> None:
    """Test that feature names are case-normalized."""
    # Lowercase feature name
    result = validate_features('NOUN', {'case': 'Nom'}, feature_set)
    assert 'Case' in result
    assert result['Case'] == 'Nom'


def test_validate_features_normalizes_feature_value_case(feature_set: dict[str, Any]) -> None:
    """Test that feature values are case-normalized."""
    # Lowercase value
    result = validate_features('NOUN', {'Case': 'nom'}, feature_set)
    assert result.get('Case') == 'Nom'


def test_validate_features_mixed_case_feature(feature_set: dict[str, Any]) -> None:
    """Test with mixed case feature name."""
    result = validate_features('NOUN', {'cAsE': 'Nom'}, feature_set)
    assert 'Case' in result


def test_validate_features_mixed_case_value(feature_set: dict[str, Any]) -> None:
    """Test with mixed case feature value."""
    result = validate_features('NOUN', {'Case': 'nOM'}, feature_set)
    assert result.get('Case') == 'Nom'


def test_validate_features_all_lowercase(feature_set: dict[str, Any]) -> None:
    """Test with all lowercase input."""
    result = validate_features('NOUN', {'case': 'nom', 'gender': 'masc', 'number': 'sing'}, feature_set)
    assert result.get('Case') == 'Nom'
    assert result.get('Gender') == 'Masc'
    assert result.get('Number') == 'Sing'
