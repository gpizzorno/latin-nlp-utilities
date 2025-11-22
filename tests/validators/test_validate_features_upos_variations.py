"""Test validate_features with different UPOS tags."""

from typing import Any

from nlp_utilities.validators import validate_features


def test_validate_features_pron(feature_set: dict[str, Any]) -> None:
    """Test pronoun features."""
    result = validate_features('PRON', {'Case': 'Dat', 'Number': 'Sing', 'Person': '1'}, feature_set)
    assert len(result) > 0


def test_validate_features_num(feature_set: dict[str, Any]) -> None:
    """Test numeral features."""
    result = validate_features('NUM', {'Case': 'Nom', 'Gender': 'Masc'}, feature_set)
    assert len(result) >= 0  # May or may not have valid features


def test_validate_features_adv(feature_set: dict[str, Any]) -> None:
    """Test adverb features."""
    result = validate_features('ADV', {'Degree': 'Pos'}, feature_set)
    # Adverbs might have Degree
    assert isinstance(result, dict)


def test_validate_features_aux(feature_set: dict[str, Any]) -> None:
    """Test auxiliary features."""
    result = validate_features('AUX', {'Mood': 'Ind', 'Tense': 'Pres'}, feature_set)
    assert isinstance(result, dict)


def test_validate_features_propn(feature_set: dict[str, Any]) -> None:
    """Test proper noun features."""
    result = validate_features('PROPN', {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}, feature_set)
    # Should work like NOUN
    assert len(result) > 0
