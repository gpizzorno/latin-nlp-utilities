"""Tests for validate_features function."""

from typing import Any

import pytest

from nlp_utilities.validators import validate_features


def test_validate_features_requires_upos(feature_set: dict[str, Any]) -> None:
    """Test that UPOS is required."""
    with pytest.raises(ValueError, match='UPOS and feature set must be provided'):
        validate_features(None, {'Case': 'Nom'}, feature_set)  # type: ignore [arg-type]


def test_validate_features_requires_feature_set() -> None:
    """Test that feature_set is required."""
    with pytest.raises(ValueError, match='UPOS and feature set must be provided'):
        validate_features('NOUN', {'Case': 'Nom'}, None)  # type: ignore [arg-type]


def test_validate_features_none_feats(feature_set: dict[str, Any]) -> None:
    """Test with None feats returns empty dict."""
    result = validate_features('NOUN', None, feature_set)  # type: ignore [arg-type]
    assert result == {}


def test_validate_features_empty_dict(feature_set: dict[str, Any]) -> None:
    """Test with empty features dict."""
    result = validate_features('NOUN', {}, feature_set)
    assert result == {}


def test_validate_features_empty_string(feature_set: dict[str, Any]) -> None:
    """Test with empty features string."""
    result = validate_features('NOUN', '', feature_set)
    assert result == {}


def test_validate_features_underscore_string(feature_set: dict[str, Any]) -> None:
    """Test with underscore features string."""
    result = validate_features('NOUN', '_', feature_set)
    assert result == {}


def test_validate_features_single_valid_feature(feature_set: dict[str, Any]) -> None:
    """Test with single valid feature."""
    result = validate_features('NOUN', {'Case': 'Nom'}, feature_set)
    assert result == {'Case': 'Nom'}


def test_validate_features_multiple_valid_features(feature_set: dict[str, Any]) -> None:
    """Test with multiple valid features."""
    result = validate_features('NOUN', {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}, feature_set)
    assert result == {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}


def test_validate_features_string_single_feature(feature_set: dict[str, Any]) -> None:
    """Test with single feature as string."""
    result = validate_features('NOUN', 'Case=Nom', feature_set)
    assert result == {'Case': 'Nom'}


def test_validate_features_string_multiple_features(feature_set: dict[str, Any]) -> None:
    """Test with multiple features as string."""
    result = validate_features('NOUN', 'Case=Nom|Gender=Masc|Number=Sing', feature_set)
    assert result == {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}


def test_validate_features_string_with_invalid(feature_set: dict[str, Any]) -> None:
    """Test that invalid features in string are filtered."""
    result = validate_features('NOUN', 'Case=Nom|Tense=Pres', feature_set)
    assert result == {'Case': 'Nom'}
    assert 'Tense' not in result
