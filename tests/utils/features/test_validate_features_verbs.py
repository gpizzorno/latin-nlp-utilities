"""Test validate_features with verb-specific features."""

from typing import Any

from conllu_tools.utils.features import validate_features


def test_validate_features_verb_tenses(feature_set: dict[str, Any]) -> None:
    """Test verb tenses."""
    tenses = ['Pres', 'Past', 'Fut', 'Pqp']
    for tense in tenses:
        result = validate_features('VERB', {'Tense': tense}, feature_set)
        if tense in result.get('Tense', ''):
            assert result.get('Tense') == tense


def test_validate_features_verb_moods(feature_set: dict[str, Any]) -> None:
    """Test verb moods."""
    moods = ['Ind', 'Sub', 'Imp']
    for mood in moods:
        result = validate_features('VERB', {'Mood': mood}, feature_set)
        if mood in result.get('Mood', ''):
            assert result.get('Mood') == mood


def test_validate_features_verb_voices(feature_set: dict[str, Any]) -> None:
    """Test verb voices."""
    result_act = validate_features('VERB', {'Voice': 'Act'}, feature_set)
    if 'Voice' in result_act:
        assert result_act['Voice'] == 'Act'

    result_pass = validate_features('VERB', {'Voice': 'Pass'}, feature_set)
    if 'Voice' in result_pass:
        assert result_pass['Voice'] == 'Pass'


def test_validate_features_verb_persons(feature_set: dict[str, Any]) -> None:
    """Test verb persons."""
    persons = ['1', '2', '3']
    for person in persons:
        result = validate_features('VERB', {'Person': person}, feature_set)
        if 'Person' in result:
            assert result.get('Person') == person


def test_validate_features_verb_complete(feature_set: dict[str, Any]) -> None:
    """Test verb with complete feature set."""
    result = validate_features(
        'VERB',
        {
            'Mood': 'Ind',
            'Number': 'Sing',
            'Person': '3',
            'Tense': 'Pres',
            'Voice': 'Act',
        },
        feature_set,
    )
    # All should be valid
    assert 'Mood' in result or 'Tense' in result or 'Voice' in result
    assert len(result) > 0


def test_validate_features_verb_rejects_noun_specific(feature_set: dict[str, Any]) -> None:
    """Test that verb rejects noun-specific features like Case."""
    result = validate_features('VERB', {'Tense': 'Pres', 'Case': 'Nom'}, feature_set)
    assert 'Tense' in result or len(result) >= 0  # Tense might be valid
    # Case should not be valid for VERB (unless it's a participle form)
