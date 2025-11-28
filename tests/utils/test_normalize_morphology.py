"""Tests for normalize_morphology function."""

from __future__ import annotations

from typing import Any

from conllu_tools.utils.normalization import normalize_morphology


def test_normalize_morphology_basic(feature_set: dict[str, Any]) -> None:
    """Test basic normalization with valid data."""
    features = {'Case': 'Nom', 'Gender': 'Masc'}
    xpos, feats = normalize_morphology('NOUN', 'n--------', features, feature_set)
    assert feats == {'Case': 'Nom', 'Gender': 'Masc'}
    # Case=Nom -> position 8 = 'n', Gender=Masc -> position 7 = 'm'
    assert xpos == 'n-----mn-'


def test_normalize_morphology_with_ref_features(feature_set: dict[str, Any]) -> None:
    """Test normalization with reference features."""
    features = {'Case': 'Nom'}
    ref_features = {'Number': 'Sing'}
    _xpos, feats = normalize_morphology('NOUN', 'n--------', features, feature_set, ref_features)
    assert feats == {'Case': 'Nom', 'Number': 'Sing'}


def test_normalize_morphology_ref_features_string(feature_set: dict[str, Any]) -> None:
    """Test normalization with reference features as string."""
    features = {'Case': 'Nom'}
    ref_features = 'Number=Sing'
    result_xpos, result_feats = normalize_morphology('NOUN', 'n--------', features, feature_set, ref_features)
    assert result_feats == {'Case': 'Nom', 'Number': 'Sing'}
    assert result_xpos[0] == 'n'


def test_normalize_morphology_feats_take_precedence(feature_set: dict[str, Any]) -> None:
    """Test that feats take precedence over ref_features."""
    features = {'Case': 'Nom'}
    ref_features = {'Case': 'Gen'}
    result_xpos, result_feats = normalize_morphology('NOUN', 'n--------', features, feature_set, ref_features)
    assert result_feats == {'Case': 'Nom'}
    assert result_xpos[0] == 'n'


def test_normalize_morphology_string_features(feature_set: dict[str, Any]) -> None:
    """Test normalization with string features."""
    features = 'Case=Nom'
    result_xpos, result_feats = normalize_morphology('NOUN', 'n--------', features, feature_set)
    assert result_feats == {'Case': 'Nom'}
    assert result_xpos[0] == 'n'


def test_normalize_morphology_filters_invalid_features(feature_set: dict[str, Any]) -> None:
    """Test that invalid features are filtered out."""
    features = {'Case': 'Acc', 'UnknownAttr': 'Value'}
    result_xpos, result_feats = normalize_morphology('NOUN', 'n--------', features, feature_set)
    assert result_feats == {'Case': 'Acc'}
    assert result_xpos[0] == 'n'


def test_normalize_morphology_xpos_reconciliation(feature_set: dict[str, Any]) -> None:
    """Test that provided XPOS takes precedence but fills missing slots."""
    features = {'Case': 'Nom', 'Gender': 'Masc'}
    # Provided XPOS has some positions filled (must be lowercase to match PERSEUS pattern)
    result_xpos, result_feats = normalize_morphology('NOUN', 'n-a------', features, feature_set)
    # validate_xpos keeps 'a' at position 3 (valid character for that position)
    # Then features fill missing positions: Gender=Masc -> position 7 'm', Case=Nom -> position 8 'n'
    assert result_xpos[2] == 'a'  # kept from input
    assert result_xpos[6] == 'm'  # filled from Gender
    assert result_xpos[7] == 'n'  # filled from Case
    assert result_xpos[0] == 'n'  # UPOS
    assert result_feats == {'Case': 'Nom', 'Gender': 'Masc'}


def test_normalize_morphology_xpos_validation(feature_set: dict[str, Any]) -> None:
    """Test that XPOS is validated against UPOS."""
    features = {'Case': 'Nom'}
    # Invalid first character for NOUN
    result_xpos, result_feats = normalize_morphology('NOUN', 'V--------', features, feature_set)
    # Should normalize to correct UPOS character
    assert result_xpos[0] == 'n'
    assert result_feats == {'Case': 'Nom'}


def test_normalize_morphology_verb(feature_set: dict[str, Any]) -> None:
    """Test normalization for verb."""
    features = {'Tense': 'Pres', 'Mood': 'Ind'}
    xpos, feats = normalize_morphology('VERB', 'v--------', features, feature_set)
    assert xpos[0] == 'v'
    assert feats == {'Tense': 'Pres', 'Mood': 'Ind'}
    assert xpos == 'v--pi----'


def test_normalize_morphology_adjective(feature_set: dict[str, Any]) -> None:
    """Test normalization for adjective."""
    features = {'Case': 'Nom', 'Gender': 'Masc'}
    xpos, feats = normalize_morphology('ADJ', 'A--------', features, feature_set)
    assert xpos[0] == 'a'
    assert feats == {'Case': 'Nom', 'Gender': 'Masc'}


def test_normalize_morphology_empty_features(feature_set: dict[str, Any]) -> None:
    """Test with empty features dict."""
    feature_set = {'Case': {'byupos': {'NOUN': {'Nom': 1}}}}
    result_xpos, result_feats = normalize_morphology('NOUN', 'n--------', {}, feature_set)
    assert result_feats == {}
    assert result_xpos == 'n--------'


def test_normalize_morphology_empty_string_features(feature_set: dict[str, Any]) -> None:
    """Test with empty feature string."""
    feature_set = {'Case': {'byupos': {'NOUN': {'Nom': 1}}}}
    result_xpos, result_feats = normalize_morphology('NOUN', 'n--------', '', feature_set)
    assert result_feats == {}
    assert result_xpos[0] == 'n'


def test_normalize_morphology_underscore_features(feature_set: dict[str, Any]) -> None:
    """Test with underscore feature string (CoNLL-U empty marker)."""
    feature_set = {'Case': {'byupos': {'NOUN': {'Nom': 1}}}}
    result_xpos, result_feats = normalize_morphology('NOUN', 'n--------', '_', feature_set)
    assert result_feats == {}
    assert result_xpos[0] == 'n'


def test_normalize_morphology_complex_features(feature_set: dict[str, Any]) -> None:
    """Test with multiple valid features."""
    features = {'Case': 'Gen', 'Gender': 'Fem', 'Number': 'Plur'}
    result_xpos, result_feats = normalize_morphology('NOUN', 'n--------', features, feature_set)
    assert result_feats == {'Case': 'Gen', 'Gender': 'Fem', 'Number': 'Plur'}
    assert result_xpos[0] == 'n'


def test_normalize_morphology_mixed_valid_invalid(feature_set: dict[str, Any]) -> None:
    """Test with mix of valid and invalid features."""
    features = {'Case': 'Nom', 'SomeFeature': 'Fem'}
    result_xpos, result_feats = normalize_morphology('NOUN', 'n--------', features, feature_set)
    assert result_feats == {'Case': 'Nom'}
    assert result_xpos[0] == 'n'


def test_normalize_morphology_feature_not_for_upos(feature_set: dict[str, Any]) -> None:
    """Test feature that exists but not for the given UPOS."""
    features = {'VerbForm': 'Fin'}
    result_xpos, result_feats = normalize_morphology('NOUN', 'n--------', features, feature_set)
    assert result_feats == {}
    assert result_xpos[0] == 'n'


def test_normalize_morphology_xpos_fills_missing_positions(feature_set: dict[str, Any]) -> None:
    """Test that missing XPOS positions are filled from features."""
    features = {'Case': 'Nom'}
    # XPOS with missing positions (dashes)
    result_xpos, result_feats = normalize_morphology('NOUN', 'n--------', features, feature_set)
    # Features should generate XPOS that fills the gaps
    assert result_xpos[0] == 'n'
    assert result_feats == {'Case': 'Nom'}


def test_normalize_morphology_xpos_precedence(feature_set: dict[str, Any]) -> None:
    """Test that provided XPOS takes precedence over generated XPOS."""
    features = {'Case': 'Nom'}
    # Provided XPOS has non-dash positions
    result_xpos, result_feats = normalize_morphology('NOUN', 'Nxyzabcde', features, feature_set)
    # Non-dash positions from provided XPOS should be preserved after validation
    assert result_xpos[0] == 'n'
    assert result_feats == {'Case': 'Nom'}


def test_normalize_morphology_pron(feature_set: dict[str, Any]) -> None:
    """Test normalization for pronoun."""
    features = {'Case': 'Nom'}
    result_xpos, result_feats = normalize_morphology('PRON', 'P--------', features, feature_set)
    assert result_xpos[0] == 'p'
    assert result_feats == {'Case': 'Nom'}


def test_normalize_morphology_xpos_validation_removes_invalid(feature_set: dict[str, Any]) -> None:
    """Test that invalid XPOS positions are removed."""
    features = {'Case': 'Nom'}
    # XPOS with invalid characters for NOUN positions
    result_xpos, result_feats = normalize_morphology('NOUN', 'Nxxxxxxxxx', features, feature_set)
    # validate_xpos should clean up invalid positions
    assert result_xpos[0] == 'n'
    assert result_feats == {'Case': 'Nom'}


def test_normalize_morphology_ref_features_filled_only_missing(feature_set: dict[str, Any]) -> None:
    """Test that ref_features only fills missing keys."""
    features = {'Case': 'Nom'}
    ref_features = {'Case': 'Gen', 'Number': 'Sing'}
    result_xpos, result_feats = normalize_morphology('NOUN', 'n--------', features, feature_set, ref_features)
    # Case from features should win, Number from ref_features should be added
    assert result_feats == {'Case': 'Nom', 'Number': 'Sing'}
    assert result_xpos[0] == 'n'


def test_normalize_morphology_xpos_short(feature_set: dict[str, Any]) -> None:
    """Test with XPOS shorter than expected."""
    features = {'Case': 'Nom'}
    # Short XPOS will be normalized by validate_xpos
    result_xpos, result_feats = normalize_morphology('NOUN', 'N', features, feature_set)
    # Should be padded to 9 characters
    assert len(result_xpos) == 9
    assert result_xpos[0] == 'n'
    assert result_feats == {'Case': 'Nom'}


def test_normalize_morphology_all_positions_filled(feature_set: dict[str, Any]) -> None:
    """Test with all XPOS positions non-dash."""
    features = {'Case': 'Nom'}
    result_xpos, result_feats = normalize_morphology('VERB', 'Vvvvvvvvv', features, feature_set)
    # Validation will check each position
    assert result_xpos[0] == 'v'
    assert result_feats == {'Case': 'Nom'}


def test_normalize_morphology_integration(feature_set: dict[str, Any]) -> None:
    """Test full integration with format_xpos, validate_xpos, validate_features, and features_to_xpos."""
    features = 'Case=Nom|Gender=Masc|Number=Sing'
    ref_features = 'Case=Gen|Degree=Pos'
    xpos, feats = normalize_morphology('NOUN', 'n-s------', features, feature_set, ref_features)
    # Features should be validated and Case should come from features not ref
    assert feats == {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}
    # XPOS should be normalized
    assert xpos[0] == 'n'
    assert xpos[6] == 'm'
    assert xpos[7] == 'n'
    assert xpos == 'n-s---mn-'


def test_normalize_morphology_noun_positions(feature_set: dict[str, Any]) -> None:
    """Test XPOS position validation for NOUN."""
    features = {'Case': 'Nom'}
    result_xpos, result_feats = normalize_morphology('NOUN', 'nnavpmavn', features, feature_set)
    assert result_xpos == 'n-a---av-'
    assert result_feats == {'Case': 'Nom'}


def test_normalize_morphology_verb_positions(feature_set: dict[str, Any]) -> None:
    """Test XPOS position validation for VERB."""
    features = {'Mood': 'Ind'}
    result_xpos, result_feats = normalize_morphology('VERB', 'vabcdefgh', features, feature_set)
    assert result_xpos[0] == 'v'
    assert result_xpos == 'v---i----'
    assert result_feats == {'Mood': 'Ind'}


def test_normalize_morphology_adj_position_9(feature_set: dict[str, Any]) -> None:
    """Test position 9 for adjective (only valid for 'a')."""
    features = {'Case': 'Nom'}
    result_xpos, result_feats = normalize_morphology('ADJ', 'Axxxxxxxxa', features, feature_set)
    # ADJ -> 'a'
    # After validate_xpos, only positions where 'a' is valid are kept
    assert result_xpos[0] == 'a'
    # Case=Nom fills position 8
    assert result_xpos[7] == 'n'
    assert result_feats == {'Case': 'Nom'}


def test_normalize_morphology_unknown_upos(feature_set: dict[str, Any]) -> None:
    """Test with unknown UPOS."""
    features = {'Case': 'Nom'}
    result_xpos, result_feats = normalize_morphology('INTJ', 'Iabcdefgh', features, feature_set)
    # Unknown UPOS, features won't validate
    assert result_feats == {}
    assert len(result_xpos) == 9


def test_normalize_morphology_case_sensitive_upos(feature_set: dict[str, Any]) -> None:
    """Test that UPOS is case-sensitive in feature validation."""
    features = {'Case': 'Nom'}
    result_xpos, result_feats = normalize_morphology('noun', 'n--------', features, feature_set)  # Lowercase
    assert result_feats == {}
    assert len(result_xpos) == 9


def test_real_world_cases(feature_set: dict[str, Any]) -> None:
    """Test real-world morphology normalization cases."""
    test_cases: list[dict[str, str]] = [
        {
            'upos': 'VERB',
            'xpos': 'v-s-ga-g-',
            'feats': 'Aspect=Perf|Case=Gen|Degree=Pos|Number=Sing|Voice=Act',
            'ref_feats': 'Aspect=Perf|Case=Gen|Degree=Pos|Number=Sing|VerbForm=Ger|Voice=Act',
            'result_xpos': 'v-stga-g-',
            'result_feats': 'Aspect=Perf|Case=Gen|Degree=Pos|Number=Sing|VerbForm=Ger|Voice=Act',
        },
        {
            'upos': 'NUM',
            'xpos': 'm-p---fa-',
            'feats': 'Case=Acc|Gender=Fem|Number=Plur',
            'ref_feats': 'NumForm=Word',
            'result_xpos': 'm-p---fa-',
            'result_feats': 'Case=Acc|Gender=Fem|NumForm=Word|Number=Plur',
        },
        {
            'upos': 'AUX',
            'xpos': 'v2spia---',
            'feats': 'Mood=Ind|Number=Sing|Person=2|Tense=Pres|VerbForm=Fin|Voice=Act',
            'ref_feats': '',
            'result_xpos': 'v2spia---',
            'result_feats': 'Mood=Ind|Number=Sing|Person=2|Tense=Pres|VerbForm=Fin|Voice=Act',
        },
        {
            'upos': 'ADJ',
            'xpos': 'a-s---nbp',
            'feats': 'Case=Abl|Degree=Pos|Gender=Neut|Number=Sing',
            'ref_feats': 'Case=Abl|Gender=Masc|Number=Sing',
            'result_xpos': 'a-s---nbp',
            'result_feats': 'Case=Abl|Degree=Pos|Gender=Neut|Number=Sing',
        },
        {
            'upos': 'NOUN',
            'xpos': 'v2spma---',
            'feats': 'Mood=Imp|Number=Sing|Person=2|Tense=Pres|VerbForm=Fin|Voice=Act',
            'ref_feats': '',
            'result_xpos': 'n-s------',
            'result_feats': 'Number=Sing',
        },
    ]

    for test_case in test_cases:
        feats = test_case['feats']
        ref_feats = test_case['ref_feats']
        if ref_feats is not None:
            result_xpos, result_feats = normalize_morphology(
                test_case['upos'],
                test_case['xpos'],
                feats,
                feature_set,
                ref_feats,
            )
        else:
            result_xpos, result_feats = normalize_morphology(
                test_case['upos'],
                test_case['xpos'],
                feats,
                feature_set,
            )

        # Convert result_feats dict back to string for comparison
        result_feats_str = '|'.join(f'{k}={v}' for k, v in sorted(result_feats.items()))

        assert result_xpos == test_case['result_xpos']
        assert result_feats_str == test_case['result_feats']
