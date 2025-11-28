"""Tests for PROIEL XPOS to Perseus converter functions and integration."""

from conllu_tools.utils.xpos.proiel_converters import proiel_to_perseus


def test_proiel_to_perseus_empty_features() -> None:
    """Test with empty feature string."""
    result = proiel_to_perseus('NOUN', '_')
    assert result == 'n--------'


def test_proiel_to_perseus_basic_noun() -> None:
    """Test conversion of a basic noun."""
    result = proiel_to_perseus('NOUN', 'Case=Nom|Gender=Masc|Number=Sing')
    assert result == 'n-s---mn-'
    assert result[0] == 'n'  # noun
    assert result[1] == '-'  # no person
    assert result[2] == 's'  # singular
    assert result[6] == 'm'  # masculine
    assert result[7] == 'n'  # nominative


def test_proiel_to_perseus_verb_complete() -> None:
    """Test conversion of a verb with all features."""
    result = proiel_to_perseus('VERB', 'Mood=Ind|Number=Sing|Person=1|Tense=Pres|Voice=Act')
    assert result == 'v1spia---'
    assert result[0] == 'v'  # verb
    assert result[1] == '1'  # first person
    assert result[2] == 's'  # singular
    assert result[3] == 'p'  # present
    assert result[4] == 'i'  # indicative
    assert result[5] == 'a'  # active


def test_proiel_to_perseus_verb_passive() -> None:
    """Test conversion of a passive verb."""
    result = proiel_to_perseus('VERB', 'Mood=Ind|Number=Plur|Person=3|Tense=Pres|Voice=Pass')
    assert result == 'v3ppip---'
    assert result[1] == '3'  # third person
    assert result[2] == 'p'  # plural
    assert result[3] == 'p'  # present
    assert result[4] == 'i'  # indicative
    assert result[5] == 'p'  # passive


def test_proiel_to_perseus_verb_perfect() -> None:
    """Test conversion of a perfect tense verb."""
    result = proiel_to_perseus('VERB', 'Mood=Ind|Number=Sing|Person=3|Tense=Past|Voice=Act')
    assert result == 'v3sria---'
    assert result[3] == 'r'  # perfect (Past)


def test_proiel_to_perseus_verb_pluperfect() -> None:
    """Test conversion of a pluperfect tense verb."""
    result = proiel_to_perseus('VERB', 'Mood=Ind|Number=Sing|Person=3|Tense=Pqp|Voice=Act')
    assert result == 'v3slia---'
    assert result[3] == 'l'  # pluperfect


def test_proiel_to_perseus_verb_future() -> None:
    """Test conversion of a future tense verb."""
    result = proiel_to_perseus('VERB', 'Mood=Ind|Number=Sing|Person=1|Tense=Fut|Voice=Act')
    assert result == 'v1sfia---'
    assert result[3] == 'f'  # future


def test_proiel_to_perseus_verb_subjunctive() -> None:
    """Test conversion of a subjunctive verb."""
    result = proiel_to_perseus('VERB', 'Mood=Sub|Number=Plur|Person=2|Tense=Pres|Voice=Act')
    assert result == 'v2ppsa---'
    assert result[4] == 's'  # subjunctive


def test_proiel_to_perseus_verb_imperative() -> None:
    """Test conversion of an imperative verb."""
    result = proiel_to_perseus('VERB', 'Mood=Imp|Number=Sing|Person=2|Tense=Pres|Voice=Act')
    assert result == 'v2spma---'
    assert result[4] == 'm'  # imperative


def test_proiel_to_perseus_adjective_positive() -> None:
    """Test conversion of a positive degree adjective."""
    result = proiel_to_perseus('ADJ', 'Case=Nom|Degree=Pos|Gender=Fem|Number=Sing')
    assert result == 'a-s---fnp'
    assert result[0] == 'a'  # adjective
    assert result[6] == 'f'  # feminine
    assert result[7] == 'n'  # nominative
    assert result[8] == 'p'  # positive


def test_proiel_to_perseus_adjective_comparative() -> None:
    """Test conversion of a comparative adjective."""
    result = proiel_to_perseus('ADJ', 'Case=Acc|Degree=Cmp|Gender=Masc|Number=Sing')
    assert result == 'a-s---mac'
    assert result[7] == 'a'  # accusative
    assert result[8] == 'c'  # comparative


def test_proiel_to_perseus_adjective_superlative() -> None:
    """Test conversion of a superlative adjective."""
    result = proiel_to_perseus('ADJ', 'Case=Gen|Degree=Sup|Gender=Neut|Number=Plur')
    assert result == 'a-p---ngs'
    assert result[2] == 'p'  # plural
    assert result[6] == 'n'  # neuter
    assert result[7] == 'g'  # genitive
    assert result[8] == 's'  # superlative


def test_proiel_to_perseus_pronoun() -> None:
    """Test conversion of a pronoun."""
    result = proiel_to_perseus('PRON', 'Case=Dat|Gender=Masc|Number=Sing')
    assert result == 'p-s---md-'
    assert result[0] == 'p'  # pronoun
    assert result[7] == 'd'  # dative


def test_proiel_to_perseus_missing_person() -> None:
    """Test with Person feature missing."""
    result = proiel_to_perseus('VERB', 'Mood=Ind|Number=Sing|Tense=Pres|Voice=Act')
    assert result == 'v-spia---'
    assert result[1] == '-'  # no person


def test_proiel_to_perseus_missing_number() -> None:
    """Test with Number feature missing."""
    result = proiel_to_perseus('NOUN', 'Case=Nom|Gender=Masc')
    assert result == 'n-----mn-'
    assert result[2] == '-'  # no number


def test_proiel_to_perseus_missing_gender() -> None:
    """Test with Gender feature missing."""
    result = proiel_to_perseus('NOUN', 'Case=Acc|Number=Plur')
    assert result == 'n-p----a-'
    assert result[6] == '-'  # no gender


def test_proiel_to_perseus_missing_case() -> None:
    """Test with Case feature missing."""
    result = proiel_to_perseus('NOUN', 'Gender=Fem|Number=Sing')
    assert result == 'n-s---f--'
    assert result[7] == '-'  # no case


def test_proiel_to_perseus_only_tense() -> None:
    """Test with only Tense feature."""
    result = proiel_to_perseus('VERB', 'Tense=Pres')
    assert result == 'v--p-----'


def test_proiel_to_perseus_only_mood() -> None:
    """Test with only Mood feature."""
    result = proiel_to_perseus('VERB', 'Mood=Sub')
    assert result == 'v---s----'


def test_proiel_to_perseus_only_voice() -> None:
    """Test with only Voice feature."""
    result = proiel_to_perseus('VERB', 'Voice=Pass')
    assert result == 'v----p---'


def test_proiel_to_perseus_all_cases() -> None:
    """Test all case values."""
    assert proiel_to_perseus('NOUN', 'Case=Nom')[7] == 'n'  # nominative
    assert proiel_to_perseus('NOUN', 'Case=Gen')[7] == 'g'  # genitive
    assert proiel_to_perseus('NOUN', 'Case=Dat')[7] == 'd'  # dative
    assert proiel_to_perseus('NOUN', 'Case=Acc')[7] == 'a'  # accusative
    assert proiel_to_perseus('NOUN', 'Case=Voc')[7] == 'v'  # vocative
    assert proiel_to_perseus('NOUN', 'Case=Abl')[7] == 'b'  # ablative


def test_proiel_to_perseus_all_genders() -> None:
    """Test all gender values."""
    assert proiel_to_perseus('NOUN', 'Gender=Masc')[6] == 'm'  # masculine
    assert proiel_to_perseus('NOUN', 'Gender=Fem')[6] == 'f'  # feminine
    assert proiel_to_perseus('NOUN', 'Gender=Neut')[6] == 'n'  # neuter


def test_proiel_to_perseus_unknown_feature_values() -> None:
    """Test with unknown feature values."""
    result = proiel_to_perseus('NOUN', 'Case=Loc|Gender=Com|Number=Dual')
    assert result[2] == '-'  # Dual not supported
    assert result[6] == '-'  # Com not supported
    assert result[7] == '-'  # Loc not supported


def test_proiel_to_perseus_unknown_upos() -> None:
    """Test with unknown UPOS tag."""
    result = proiel_to_perseus('INTJ', 'Case=Nom')
    assert result[0] == '-'  # unknown UPOS


def test_proiel_to_perseus_realistic_examples() -> None:
    """Test with realistic examples from actual treebank data."""
    # "dominus" - nominative singular masculine noun
    result = proiel_to_perseus('NOUN', 'Case=Nom|Gender=Masc|Number=Sing')
    assert result == 'n-s---mn-'

    # "laudatur" - 3rd person singular present indicative passive
    result = proiel_to_perseus('VERB', 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Pass')
    assert result == 'v3spip---'

    # "melior" - comparative adjective nominative masculine singular
    result = proiel_to_perseus('ADJ', 'Case=Nom|Degree=Cmp|Gender=Masc|Number=Sing')
    assert result == 'a-s---mnc'

    # "mihi" - dative singular pronoun
    result = proiel_to_perseus('PRON', 'Case=Dat|Number=Sing|Person=1')
    assert result == 'p1s----d-'


def test_proiel_to_perseus_extra_features() -> None:
    """Test with features that are not used in conversion."""
    # Extra features should be ignored
    result = proiel_to_perseus('NOUN', 'Animacy=Anim|Case=Nom|Gender=Masc|Number=Sing|Foreign=Yes')
    assert result == 'n-s---mn-'


def test_proiel_to_perseus_empty_string_upos() -> None:
    """Test with empty UPOS string."""
    result = proiel_to_perseus('', 'Case=Nom')
    # Empty UPOS should map to '-'
    assert result[0] == '-'


def test_proiel_to_perseus_feature_order_independence() -> None:
    """Test that feature order doesn't matter."""
    result1 = proiel_to_perseus('VERB', 'Mood=Ind|Number=Sing|Person=1|Tense=Pres|Voice=Act')
    result2 = proiel_to_perseus('VERB', 'Voice=Act|Tense=Pres|Person=1|Number=Sing|Mood=Ind')
    result3 = proiel_to_perseus('VERB', 'Person=1|Voice=Act|Mood=Ind|Tense=Pres|Number=Sing')
    assert result1 == result2 == result3 == 'v1spia---'
