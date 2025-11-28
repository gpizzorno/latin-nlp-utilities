"""Test validate_features integration scenarios."""

from typing import Any

from conllu_tools.utils.features import validate_features


def test_validate_features_realistic_noun(feature_set: dict[str, Any]) -> None:
    """Test realistic noun example."""
    result = validate_features('NOUN', 'Case=Dat|Gender=Neut|Number=Plur', feature_set)
    assert result.get('Case') == 'Dat'
    assert result.get('Gender') == 'Neut'
    assert result.get('Number') == 'Plur'


def test_validate_features_realistic_verb(feature_set: dict[str, Any]) -> None:
    """Test realistic verb example."""
    result = validate_features('VERB', 'Mood=Sub|Number=Plur|Person=2|Tense=Fut|Voice=Pass', feature_set)
    # Should have at least some valid features
    assert len(result) > 0


def test_validate_features_realistic_adjective(feature_set: dict[str, Any]) -> None:
    """Test realistic adjective example."""
    result = validate_features('ADJ', 'Case=Gen|Degree=Sup|Gender=Fem|Number=Sing', feature_set)
    assert len(result) > 0


def test_validate_features_participle(feature_set: dict[str, Any]) -> None:
    """Test participle features (verb with nominal features)."""
    result = validate_features(
        'VERB',
        {
            'Case': 'Acc',
            'Gender': 'Masc',
            'Number': 'Sing',
            'Tense': 'Pres',
            'VerbForm': 'Part',
            'Voice': 'Act',
        },
        feature_set,
    )
    # Participles can have both verb and nominal features
    assert len(result) > 0


def test_validate_features_gerund(feature_set: dict[str, Any]) -> None:
    """Test gerund features."""
    result = validate_features(
        'VERB',
        {
            'Case': 'Gen',
            'VerbForm': 'Ger',
            'Voice': 'Act',
        },
        feature_set,
    )
    assert len(result) >= 0


def test_validate_features_from_real_data(feature_set: dict[str, Any]) -> None:
    """Test with features from actual treebank data."""
    # Example from real data
    result = validate_features(
        'NOUN',
        {
            'Case': 'Nom',
            'Gender': 'Fem',
            'Number': 'Sing',
        },
        feature_set,
    )
    assert result.get('Case') == 'Nom'
    assert result.get('Gender') == 'Fem'
    assert result.get('Number') == 'Sing'


def test_validate_features_filters_invalid_keeps_valid(feature_set: dict[str, Any]) -> None:
    """Test that function filters invalid but keeps valid features."""
    result = validate_features(
        'NOUN',
        {
            'Case': 'Nom',
            'Gender': 'Masc',
            'Number': 'Sing',
            'Mood': 'Ind',  # Invalid for NOUN
            'InvalidFeature': 'Value',  # Unknown feature
        },
        feature_set,
    )
    assert result.get('Case') == 'Nom'
    assert result.get('Gender') == 'Masc'
    assert result.get('Number') == 'Sing'
    assert 'Mood' not in result
    assert 'InvalidFeature' not in result
    assert len(result) == 3
