"""Tests for features_to_xpos function."""

from conllu_tools.utils.features import features_to_xpos


def test_features_to_xpos_empty_dict() -> None:
    """Test with empty features dictionary."""
    result = features_to_xpos({})
    assert result == '---------'
    assert len(result) == 9


def test_features_to_xpos_empty_string() -> None:
    """Test with empty features string."""
    result = features_to_xpos('')
    assert result == '---------'


def test_features_to_xpos_underscore_string() -> None:
    """Test with underscore features string."""
    result = features_to_xpos('_')
    assert result == '---------'


def test_features_to_xpos_single_feature() -> None:
    """Test with single feature."""
    result = features_to_xpos({'Case': 'Nom'})
    assert result == '-------n-'
    assert result[7] == 'n'  # Position 8 (0-indexed 7) is case


def test_features_to_xpos_returns_9_chars() -> None:
    """Test that result is always 9 characters."""
    test_cases: list[dict[str, str] | str] = [
        {},
        {'Case': 'Nom'},
        {'Person': '1', 'Number': 'Sing', 'Tense': 'Pres'},
        'Case=Nom|Gender=Masc|Number=Sing',
    ]
    for feats in test_cases:
        result = features_to_xpos(feats)
        assert len(result) == 9, f'Expected 9 chars for {feats}, got {len(result)}'


def test_features_to_xpos_person_1() -> None:
    """Test first person."""
    result = features_to_xpos({'Person': '1'})
    assert result == '-1-------'
    assert result[1] == '1'


def test_features_to_xpos_person_2() -> None:
    """Test second person."""
    result = features_to_xpos({'Person': '2'})
    assert result == '-2-------'
    assert result[1] == '2'


def test_features_to_xpos_person_3() -> None:
    """Test third person."""
    result = features_to_xpos({'Person': '3'})
    assert result == '-3-------'
    assert result[1] == '3'


def test_features_to_xpos_person_invalid() -> None:
    """Test invalid person value is ignored."""
    result = features_to_xpos({'Person': '4'})
    assert result == '---------'


def test_features_to_xpos_number_singular() -> None:
    """Test singular number."""
    result = features_to_xpos({'Number': 'Sing'})
    assert result == '--s------'
    assert result[2] == 's'


def test_features_to_xpos_number_plural() -> None:
    """Test plural number."""
    result = features_to_xpos({'Number': 'Plur'})
    assert result == '--p------'
    assert result[2] == 'p'


def test_features_to_xpos_number_invalid() -> None:
    """Test invalid number value is ignored."""
    result = features_to_xpos({'Number': 'Dual'})
    assert result == '---------'


def test_features_to_xpos_tense_present() -> None:
    """Test present tense."""
    result = features_to_xpos({'Tense': 'Pres'})
    assert result == '---p-----'
    assert result[3] == 'p'


def test_features_to_xpos_tense_past() -> None:
    """Test past tense (perfect)."""
    result = features_to_xpos({'Tense': 'Past'})
    assert result == '---r-----'
    assert result[3] == 'r'


def test_features_to_xpos_tense_pluperfect() -> None:
    """Test pluperfect tense."""
    result = features_to_xpos({'Tense': 'Pqp'})
    assert result == '---l-----'
    assert result[3] == 'l'


def test_features_to_xpos_tense_future() -> None:
    """Test future tense."""
    result = features_to_xpos({'Tense': 'Fut'})
    assert result == '---f-----'
    assert result[3] == 'f'


def test_features_to_xpos_aspect_imperfect() -> None:
    """Test imperfect aspect."""
    result = features_to_xpos({'Aspect': 'Imp'})
    assert result == '---i-----'
    assert result[3] == 'i'


def test_features_to_xpos_aspect_perfect() -> None:
    """Test perfect aspect (future perfect)."""
    result = features_to_xpos({'Aspect': 'Perf'})
    assert result == '---t-----'
    assert result[3] == 't'


def test_features_to_xpos_tense_over_aspect() -> None:
    """Test that when both tense and aspect are present, last one wins."""
    # Both map to position 4, so the last one processed wins
    result1 = features_to_xpos({'Tense': 'Pres', 'Aspect': 'Imp'})
    # Dictionary iteration order in Python 3.7+ is insertion order
    # So 'Aspect' would be processed after 'Tense' and overwrite it
    assert result1[3] in ['p', 'i']  # One of them will be present


def test_features_to_xpos_mood_indicative() -> None:
    """Test indicative mood."""
    result = features_to_xpos({'Mood': 'Ind'})
    assert result == '----i----'
    assert result[4] == 'i'


def test_features_to_xpos_mood_subjunctive() -> None:
    """Test subjunctive mood."""
    result = features_to_xpos({'Mood': 'Sub'})
    assert result == '----s----'
    assert result[4] == 's'


def test_features_to_xpos_mood_imperative() -> None:
    """Test imperative mood."""
    result = features_to_xpos({'Mood': 'Imp'})
    assert result == '----m----'
    assert result[4] == 'm'


def test_features_to_xpos_verbform_infinitive() -> None:
    """Test infinitive verb form."""
    result = features_to_xpos({'VerbForm': 'Inf'})
    assert result == '----n----'
    assert result[4] == 'n'


def test_features_to_xpos_verbform_participle() -> None:
    """Test participle verb form."""
    result = features_to_xpos({'VerbForm': 'Part'})
    assert result == '----p----'
    assert result[4] == 'p'


def test_features_to_xpos_verbform_gerund() -> None:
    """Test gerund verb form."""
    result = features_to_xpos({'VerbForm': 'Ger'})
    assert result == '----d----'
    assert result[4] == 'd'


def test_features_to_xpos_verbform_gerundive() -> None:
    """Test gerundive verb form."""
    result = features_to_xpos({'VerbForm': 'Gdv'})
    assert result == '----g----'
    assert result[4] == 'g'


def test_features_to_xpos_verbform_supine() -> None:
    """Test supine verb form."""
    result = features_to_xpos({'VerbForm': 'Sup'})
    assert result == '----u----'
    assert result[4] == 'u'


def test_features_to_xpos_voice_active() -> None:
    """Test active voice."""
    result = features_to_xpos({'Voice': 'Act'})
    assert result == '-----a---'
    assert result[5] == 'a'


def test_features_to_xpos_voice_passive() -> None:
    """Test passive voice."""
    result = features_to_xpos({'Voice': 'Pass'})
    assert result == '-----p---'
    assert result[5] == 'p'


def test_features_to_xpos_verbtype_deponent() -> None:
    """Test deponent verb type."""
    result = features_to_xpos({'VerbType': 'Deponent'})
    assert result == '-----d---'
    assert result[5] == 'd'


def test_features_to_xpos_gender_masculine() -> None:
    """Test masculine gender."""
    result = features_to_xpos({'Gender': 'Masc'})
    assert result == '------m--'
    assert result[6] == 'm'


def test_features_to_xpos_gender_feminine() -> None:
    """Test feminine gender."""
    result = features_to_xpos({'Gender': 'Fem'})
    assert result == '------f--'
    assert result[6] == 'f'


def test_features_to_xpos_gender_neuter() -> None:
    """Test neuter gender."""
    result = features_to_xpos({'Gender': 'Neut'})
    assert result == '------n--'
    assert result[6] == 'n'


def test_features_to_xpos_case_nominative() -> None:
    """Test nominative case."""
    result = features_to_xpos({'Case': 'Nom'})
    assert result == '-------n-'
    assert result[7] == 'n'


def test_features_to_xpos_case_genitive() -> None:
    """Test genitive case."""
    result = features_to_xpos({'Case': 'Gen'})
    assert result == '-------g-'
    assert result[7] == 'g'


def test_features_to_xpos_case_dative() -> None:
    """Test dative case."""
    result = features_to_xpos({'Case': 'Dat'})
    assert result == '-------d-'
    assert result[7] == 'd'


def test_features_to_xpos_case_accusative() -> None:
    """Test accusative case."""
    result = features_to_xpos({'Case': 'Acc'})
    assert result == '-------a-'
    assert result[7] == 'a'


def test_features_to_xpos_case_vocative() -> None:
    """Test vocative case."""
    result = features_to_xpos({'Case': 'Voc'})
    assert result == '-------v-'
    assert result[7] == 'v'


def test_features_to_xpos_case_ablative() -> None:
    """Test ablative case."""
    result = features_to_xpos({'Case': 'Abl'})
    assert result == '-------b-'
    assert result[7] == 'b'


def test_features_to_xpos_case_locative() -> None:
    """Test locative case."""
    result = features_to_xpos({'Case': 'Loc'})
    assert result == '-------l-'
    assert result[7] == 'l'


def test_features_to_xpos_case_instrumental() -> None:
    """Test instrumental case."""
    result = features_to_xpos({'Case': 'Ins'})
    assert result == '-------i-'
    assert result[7] == 'i'


def test_features_to_xpos_degree_positive() -> None:
    """Test positive degree."""
    result = features_to_xpos({'Degree': 'Pos'})
    assert result == '--------p'
    assert result[8] == 'p'


def test_features_to_xpos_degree_comparative() -> None:
    """Test comparative degree."""
    result = features_to_xpos({'Degree': 'Cmp'})
    assert result == '--------c'
    assert result[8] == 'c'


def test_features_to_xpos_degree_superlative() -> None:
    """Test superlative degree."""
    result = features_to_xpos({'Degree': 'Sup'})
    assert result == '--------s'
    assert result[8] == 's'


def test_features_to_xpos_degree_absolute() -> None:
    """Test absolute degree."""
    result = features_to_xpos({'Degree': 'Abs'})
    assert result == '--------a'
    assert result[8] == 'a'


def test_features_to_xpos_noun_features() -> None:
    """Test noun features."""
    result = features_to_xpos({'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'})
    assert result == '--s---mn-'
    assert result[2] == 's'  # Number
    assert result[6] == 'm'  # Gender
    assert result[7] == 'n'  # Case


def test_features_to_xpos_verb_features() -> None:
    """Test verb features."""
    result = features_to_xpos(
        {
            'Mood': 'Ind',
            'Number': 'Sing',
            'Person': '3',
            'Tense': 'Pres',
            'Voice': 'Act',
        },
    )
    assert result == '-3spia---'
    assert result[1] == '3'  # Person
    assert result[2] == 's'  # Number
    assert result[3] == 'p'  # Tense
    assert result[4] == 'i'  # Mood
    assert result[5] == 'a'  # Voice


def test_features_to_xpos_adjective_features() -> None:
    """Test adjective features."""
    result = features_to_xpos(
        {
            'Case': 'Nom',
            'Degree': 'Cmp',
            'Gender': 'Fem',
            'Number': 'Sing',
        },
    )
    assert result == '--s---fnc'
    assert result[2] == 's'  # Number
    assert result[6] == 'f'  # Gender
    assert result[7] == 'n'  # Case
    assert result[8] == 'c'  # Degree


def test_features_to_xpos_participle_features() -> None:
    """Test participle features."""
    result = features_to_xpos(
        {
            'Case': 'Acc',
            'Gender': 'Masc',
            'Number': 'Plur',
            'Tense': 'Pres',
            'VerbForm': 'Part',
            'Voice': 'Act',
        },
    )
    assert result == '--pppama-'
    assert result[2] == 'p'  # Number
    assert result[3] == 'p'  # Tense
    assert result[4] == 'p'  # VerbForm
    assert result[5] == 'a'  # Voice
    assert result[6] == 'm'  # Gender
    assert result[7] == 'a'  # Case


def test_features_to_xpos_all_positions_filled() -> None:
    """Test with features that fill all positions."""
    result = features_to_xpos(
        {
            'Person': '2',
            'Number': 'Plur',
            'Tense': 'Fut',
            'Mood': 'Sub',
            'Voice': 'Pass',
            'Gender': 'Masc',
            'Case': 'Acc',
            'Degree': 'Cmp',
        },
    )
    assert result == '-2pfspmac'
    # Note: Position 1 (UPOS) is always '-' since features_to_xpos doesn't set it
    assert result[1] == '2'  # Person
    assert result[2] == 'p'  # Number
    assert result[3] == 'f'  # Tense
    assert result[4] == 's'  # Mood
    assert result[5] == 'p'  # Voice
    assert result[6] == 'm'  # Gender
    assert result[7] == 'a'  # Case
    assert result[8] == 'c'  # Degree


def test_features_to_xpos_string_single_feature() -> None:
    """Test with single feature string."""
    result = features_to_xpos('Case=Nom')
    assert result == '-------n-'


def test_features_to_xpos_string_multiple_features() -> None:
    """Test with multiple features string."""
    result = features_to_xpos('Case=Nom|Gender=Masc|Number=Sing')
    assert result == '--s---mn-'


def test_features_to_xpos_string_verb_features() -> None:
    """Test with verb features string."""
    result = features_to_xpos('Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act')
    assert result == '-3spia---'


def test_features_to_xpos_string_unordered() -> None:
    """Test that feature order doesn't matter."""
    result1 = features_to_xpos('Case=Nom|Gender=Masc')
    result2 = features_to_xpos('Gender=Masc|Case=Nom')
    assert result1 == result2


def test_features_to_xpos_unknown_feature() -> None:
    """Test that unknown features are ignored."""
    result = features_to_xpos({'UnknownFeature': 'Value', 'Case': 'Nom'})
    assert result == '-------n-'


def test_features_to_xpos_unknown_value() -> None:
    """Test that unknown feature values are ignored."""
    result = features_to_xpos({'Case': 'UnknownCase', 'Gender': 'Masc'})
    assert result == '------m--'


def test_features_to_xpos_case_sensitive_feature() -> None:
    """Test that feature names are case-sensitive."""
    result = features_to_xpos({'case': 'Nom'})  # lowercase 'case'
    assert result == '---------'  # Not recognized


def test_features_to_xpos_case_sensitive_value() -> None:
    """Test that feature values are case-sensitive."""
    result = features_to_xpos({'Case': 'nom'})  # lowercase 'nom'
    assert result == '---------'  # Not recognized


def test_features_to_xpos_partial_match() -> None:
    """Test that partial matches don't work."""
    result = features_to_xpos({'Case': 'Nomin'})  # Not 'Nom'
    assert result == '---------'


def test_features_to_xpos_numeric_person_string() -> None:
    """Test that Person values must be strings."""
    result = features_to_xpos({'Person': '1'})
    assert result == '-1-------'


def test_features_to_xpos_mixed_valid_invalid() -> None:
    """Test mixture of valid and invalid features."""
    result = features_to_xpos(
        {
            'Case': 'Nom',
            'InvalidFeature': 'Value',
            'Gender': 'Masc',
            'Number': 'InvalidValue',
        },
    )
    assert result == '------mn-'  # Only Case and Gender are set


def test_features_to_xpos_duplicate_position_features() -> None:
    """Test when multiple features map to same position."""
    # Both Tense and Aspect map to position 4
    result = features_to_xpos({'Tense': 'Pres', 'Aspect': 'Imp'})
    # Last one in iteration order wins
    assert result[3] in ['p', 'i']


def test_features_to_xpos_all_dashes_positions() -> None:
    """Test that unfilled positions are dashes."""
    result = features_to_xpos({'Case': 'Nom'})
    for i in range(9):
        if i != 7:  # Position 8 (case) should be 'n'
            assert result[i] == '-', f'Position {i} should be dash, got {result[i]}'


def test_features_to_xpos_realistic_noun() -> None:
    """Test realistic noun example."""
    result = features_to_xpos('Case=Dat|Gender=Neut|Number=Plur')
    assert result == '--p---nd-'


def test_features_to_xpos_realistic_verb() -> None:
    """Test realistic verb example."""
    result = features_to_xpos('Mood=Sub|Number=Plur|Person=2|Tense=Fut|Voice=Pass')
    assert result == '-2pfsp---'


def test_features_to_xpos_realistic_adjective() -> None:
    """Test realistic adjective example."""
    result = features_to_xpos('Case=Gen|Degree=Sup|Gender=Fem|Number=Sing')
    assert result == '--s---fgs'


def test_features_to_xpos_position_0_always_dash() -> None:
    """Test that position 0 (UPOS) is always a dash."""
    test_cases = [
        {},
        {'Case': 'Nom'},
        {'Person': '1', 'Number': 'Sing', 'Tense': 'Pres', 'Mood': 'Ind', 'Voice': 'Act'},
    ]
    for feats in test_cases:
        result = features_to_xpos(feats)
        assert result[0] == '-', f'Position 0 should always be dash for {feats}'
