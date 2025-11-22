"""Test validate_features with invalid features."""

from typing import Any

from nlp_utilities.validators import validate_features


def test_validate_features_unknown_feature_name(feature_set: dict[str, Any]) -> None:
    """Test that unknown feature names are ignored."""
    result = validate_features('NOUN', {'UnknownFeature': 'Value', 'Case': 'Nom'}, feature_set)
    assert 'UnknownFeature' not in result
    assert result.get('Case') == 'Nom'


def test_validate_features_unknown_feature_value(feature_set: dict[str, Any]) -> None:
    """Test that unknown feature values are ignored."""
    result = validate_features('NOUN', {'Case': 'UnknownCase', 'Gender': 'Masc'}, feature_set)
    assert 'Case' not in result
    assert result.get('Gender') == 'Masc'


def test_validate_features_wrong_upos_for_feature(feature_set: dict[str, Any]) -> None:
    """Test features invalid for specific UPOS are filtered."""
    # Tense is not valid for NOUN
    result = validate_features('NOUN', {'Case': 'Nom', 'Tense': 'Pres'}, feature_set)
    assert result.get('Case') == 'Nom'
    assert 'Tense' not in result


def test_validate_features_all_invalid(feature_set: dict[str, Any]) -> None:
    """Test when all features are invalid."""
    result = validate_features('NOUN', {'InvalidFeature1': 'Value1', 'InvalidFeature2': 'Value2'}, feature_set)
    assert result == {}


def test_validate_features_mixed_valid_invalid(feature_set: dict[str, Any]) -> None:
    """Test mixture of valid and invalid features."""
    result = validate_features(
        'NOUN',
        {
            'Case': 'Nom',
            'InvalidFeature': 'Value',
            'Gender': 'Masc',
            'Tense': 'Pres',  # Invalid for NOUN
        },
        feature_set,
    )
    assert result.get('Case') == 'Nom'
    assert result.get('Gender') == 'Masc'
    assert 'InvalidFeature' not in result
    assert 'Tense' not in result
