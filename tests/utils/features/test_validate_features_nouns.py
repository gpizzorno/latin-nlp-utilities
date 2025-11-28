"""Test validate_features with noun-specific features."""

from typing import Any

from conllu_tools.utils.features import validate_features


def test_validate_features_noun_all_cases(feature_set: dict[str, Any]) -> None:
    """Test all valid noun cases."""
    cases = ['Nom', 'Gen', 'Dat', 'Acc', 'Voc', 'Abl', 'Loc']
    for case in cases:
        result = validate_features('NOUN', {'Case': case}, feature_set)
        assert result.get('Case') == case, f'Case {case} should be valid for NOUN'


def test_validate_features_noun_all_genders(feature_set: dict[str, Any]) -> None:
    """Test all valid noun genders."""
    genders = ['Masc', 'Fem', 'Neut']
    for gender in genders:
        result = validate_features('NOUN', {'Gender': gender}, feature_set)
        assert result.get('Gender') == gender, f'Gender {gender} should be valid for NOUN'


def test_validate_features_noun_numbers(feature_set: dict[str, Any]) -> None:
    """Test noun numbers."""
    result_sing = validate_features('NOUN', {'Number': 'Sing'}, feature_set)
    assert result_sing == {'Number': 'Sing'}

    result_plur = validate_features('NOUN', {'Number': 'Plur'}, feature_set)
    assert result_plur == {'Number': 'Plur'}


def test_validate_features_noun_rejects_verb_features(feature_set: dict[str, Any]) -> None:
    """Test that noun rejects verb-specific features."""
    result = validate_features('NOUN', {'Case': 'Nom', 'Tense': 'Pres', 'Mood': 'Ind'}, feature_set)
    assert result == {'Case': 'Nom'}
    assert 'Tense' not in result
    assert 'Mood' not in result
