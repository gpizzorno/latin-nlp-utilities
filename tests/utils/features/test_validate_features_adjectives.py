"""Test validate_features with adjective-specific features."""

from typing import Any

from conllu_tools.utils.features import validate_features


def test_validate_features_adjective_cases(feature_set: dict[str, Any]) -> None:
    """Test adjective cases."""
    result = validate_features('ADJ', {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}, feature_set)
    assert 'Case' in result
    assert 'Gender' in result
    assert 'Number' in result


def test_validate_features_adjective_degrees(feature_set: dict[str, Any]) -> None:
    """Test adjective degrees."""
    degrees = ['Pos', 'Cmp', 'Sup']
    for degree in degrees:
        result = validate_features('ADJ', {'Degree': degree}, feature_set)
        if 'Degree' in result:
            assert result.get('Degree') == degree
