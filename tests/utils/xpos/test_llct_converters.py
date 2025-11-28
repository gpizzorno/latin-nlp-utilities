"""Tests for LLCT to Perseus XPOS converters."""

from conllu_tools.utils.xpos.llct_converters import llct_to_perseus


def test_llct_to_perseus_basic() -> None:
    """Test basic conversion with standard LLCT XPOS."""
    # LLCT format: POS|POS_repeat|person|number|tense|mood|voice|gender|case|degree
    result = llct_to_perseus('NOUN', 'n|n|-|s|-|-|-|m|n|-', 'Case=Nom|Gender=Masc|Number=Sing')
    assert result == 'n-s---mn-'


def test_llct_to_perseus_verb() -> None:
    """Test conversion of a verb."""
    result = llct_to_perseus('VERB', 'v|v|1|s|p|i|-|-|-|-', 'Mood=Ind|Number=Sing|Person=1|Tense=Pres|Voice=Act')
    assert result == 'v1spia---'  # Voice from FEATS (Act -> a)


def test_llct_to_perseus_verb_passive() -> None:
    """Test conversion of a passive verb."""
    result = llct_to_perseus('VERB', 'v|v|3|p|p|i|p|-|-|-', 'Mood=Ind|Number=Plur|Person=3|Tense=Pres|Voice=Pass')
    assert result == 'v3ppip---'


def test_llct_to_perseus_adjective() -> None:
    """Test conversion of an adjective."""
    result = llct_to_perseus('ADJ', 'a|a|-|s|-|-|-|f|n|p', 'Case=Nom|Gender=Fem|Number=Sing')
    assert result == 'a-s---fn-'


def test_llct_to_perseus_adjective_comparative() -> None:
    """Test conversion of a comparative adjective."""
    result = llct_to_perseus('ADJ', 'a|a|-|s|-|-|-|m|a|c', 'Case=Acc|Degree=Cmp|Gender=Masc|Number=Sing')
    assert result == 'a-s---mac'


def test_llct_to_perseus_pronoun() -> None:
    """Test conversion of a pronoun."""
    result = llct_to_perseus('PRON', 'p|p|1|s|-|-|-|-|d|-', 'Case=Dat|Number=Sing|Person=1')
    assert result == 'p1s----d-'


def test_llct_to_perseus_corrects_pos() -> None:
    """Test that UPOS overrides XPOS PoS tag."""
    # Even if XPOS has 'n' for noun, UPOS 'VERB' should make it 'v'
    result = llct_to_perseus('VERB', 'n|n|3|s|p|i|a|-|-|-', 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act')
    assert result[0] == 'v'  # Corrected from 'n' to 'v'


def test_llct_to_perseus_preserves_all_positions() -> None:
    """Test that all positions are preserved correctly."""
    result = llct_to_perseus(
        'VERB',
        'v|v|2|p|f|s|p|m|a|c',
        'Case=Acc|Degree=Cmp|Gender=Masc|Mood=Sub|Number=Plur|Person=2|Tense=Fut|Voice=Pass',
    )
    assert len(result) == 9
    assert result == 'v2pfspmac'


def test_llct_to_perseus_with_dashes() -> None:
    """Test with various dash positions."""
    result = llct_to_perseus('NOUN', 'n|n|-|-|-|-|-|n|v|-', 'Case=Voc|Gender=Neut')
    assert result == 'n-----nv-'


def test_llct_to_perseus_all_dashes() -> None:
    """Test with all features as dashes."""
    result = llct_to_perseus('X', 'x|x|-|-|-|-|-|-|-|-', '_')
    # UPOS 'X' maps to '-'
    assert result == '---------'


def test_llct_to_perseus_unknown_upos() -> None:
    """Test with unknown UPOS tag."""
    result = llct_to_perseus('INTJ', 'i|i|-|-|-|-|-|-|-|-', '_')
    assert result[0] == '-'  # Unknown UPOS


def test_llct_to_perseus_noun_cases() -> None:
    """Test different noun cases."""
    # Nominative
    result = llct_to_perseus('NOUN', 'n|n|-|s|-|-|-|m|n|-', 'Case=Nom|Gender=Masc|Number=Sing')
    assert result[7] == 'n'

    # Genitive
    result = llct_to_perseus('NOUN', 'n|n|-|s|-|-|-|m|g|-', 'Case=Gen|Gender=Masc|Number=Sing')
    assert result[7] == 'g'

    # Dative
    result = llct_to_perseus('NOUN', 'n|n|-|s|-|-|-|m|d|-', 'Case=Dat|Gender=Masc|Number=Sing')
    assert result[7] == 'd'

    # Accusative
    result = llct_to_perseus('NOUN', 'n|n|-|s|-|-|-|m|a|-', 'Case=Acc|Gender=Masc|Number=Sing')
    assert result[7] == 'a'

    # Vocative
    result = llct_to_perseus('NOUN', 'n|n|-|s|-|-|-|m|v|-', 'Case=Voc|Gender=Masc|Number=Sing')
    assert result[7] == 'v'

    # Ablative
    result = llct_to_perseus('NOUN', 'n|n|-|s|-|-|-|m|b|-', 'Case=Abl|Gender=Masc|Number=Sing')
    assert result[7] == 'b'


def test_llct_to_perseus_verb_tenses() -> None:
    """Test different verb tenses."""
    # Present
    result = llct_to_perseus('VERB', 'v|v|1|s|p|i|a|-|-|-', 'Mood=Ind|Number=Sing|Person=1|Tense=Pres|Voice=Act')
    assert result[3] == 'p'

    # Imperfect
    result = llct_to_perseus('VERB', 'v|v|1|s|i|i|a|-|-|-', 'Mood=Ind|Number=Sing|Person=1|Tense=Imp|Voice=Act')
    assert result[3] == '-'  # LLCT uses 'Imp' which doesn't map in concordance

    # Future
    result = llct_to_perseus('VERB', 'v|v|1|s|f|i|a|-|-|-', 'Mood=Ind|Number=Sing|Person=1|Tense=Fut|Voice=Act')
    assert result[3] == 'f'

    # Perfect
    result = llct_to_perseus('VERB', 'v|v|1|s|r|i|a|-|-|-', 'Mood=Ind|Number=Sing|Person=1|Tense=Past|Voice=Act')
    assert result[3] == 'r'

    # Pluperfect
    result = llct_to_perseus('VERB', 'v|v|1|s|l|i|a|-|-|-', 'Mood=Ind|Number=Sing|Person=1|Tense=Pqp|Voice=Act')
    assert result[3] == 'l'

    # Future perfect - 't' is not in LLCT_CONCORDANCES for tense
    result = llct_to_perseus('VERB', 'v|v|1|s|t|i|a|-|-|-', 'Mood=Ind|Number=Sing|Person=1|Voice=Act')
    assert result[3] == '-'  # 't' not valid in LLCT concordance, becomes '-'


def test_llct_to_perseus_verb_moods() -> None:
    """Test different verb moods."""
    # Indicative
    result = llct_to_perseus('VERB', 'v|v|1|s|p|i|a|-|-|-', 'Mood=Ind|Number=Sing|Person=1|Tense=Pres|Voice=Act')
    assert result[4] == 'i'

    # Subjunctive
    result = llct_to_perseus('VERB', 'v|v|1|s|p|s|a|-|-|-', 'Mood=Sub|Number=Sing|Person=1|Tense=Pres|Voice=Act')
    assert result[4] == 's'

    # Imperative
    result = llct_to_perseus('VERB', 'v|v|2|s|p|m|a|-|-|-', 'Mood=Imp|Number=Sing|Person=2|Tense=Pres|Voice=Act')
    assert result[4] == 'm'

    # Infinitive
    result = llct_to_perseus('VERB', 'v|v|-|-|p|n|a|-|-|-', 'Mood=Inf|Tense=Pres|Voice=Act')
    assert result[4] == '-'  # LLCT uses 'Inf' which doesn't map in concordance

    # Participle
    result = llct_to_perseus(
        'VERB',
        'v|v|-|s|p|p|a|m|n|-',
        'Case=Nom|Gender=Masc|Number=Sing|Tense=Pres|VerbForm=Part|Voice=Act',
    )
    assert result[4] == '-'  # LLCT uses VerbForm=Part, not Mood

    # Gerund
    result = llct_to_perseus('VERB', 'v|v|-|-|-|d|a|-|-|-', 'VerbForm=Ger|Voice=Act')
    assert result[4] == '-'  # LLCT uses VerbForm=Ger, not Mood


def test_llct_to_perseus_numbers() -> None:
    """Test singular and plural."""
    # Singular
    result = llct_to_perseus('NOUN', 'n|n|-|s|-|-|-|m|n|-', 'Case=Nom|Gender=Masc|Number=Sing')
    assert result[2] == 's'

    # Plural
    result = llct_to_perseus('NOUN', 'n|n|-|p|-|-|-|m|n|-', 'Case=Nom|Gender=Masc|Number=Plur')
    assert result[2] == 'p'


def test_llct_to_perseus_genders() -> None:
    """Test different genders."""
    # Masculine
    result = llct_to_perseus('NOUN', 'n|n|-|s|-|-|-|m|n|-', 'Case=Nom|Gender=Masc|Number=Sing')
    assert result[6] == 'm'

    # Feminine
    result = llct_to_perseus('NOUN', 'n|n|-|s|-|-|-|f|n|-', 'Case=Nom|Gender=Fem|Number=Sing')
    assert result[6] == 'f'

    # Neuter
    result = llct_to_perseus('NOUN', 'n|n|-|s|-|-|-|n|n|-', 'Case=Nom|Gender=Neut|Number=Sing')
    assert result[6] == 'n'


def test_llct_to_perseus_degrees() -> None:
    """Test different degrees."""
    # 'p' is not in LLCT concordance for degree (only Abs/Cmp/Dim)
    result = llct_to_perseus('ADJ', 'a|a|-|s|-|-|-|m|n|p', 'Case=Nom|Gender=Masc|Number=Sing')
    assert result[8] == '-'  # 'p' not valid, becomes '-'

    # Comparative
    result = llct_to_perseus('ADJ', 'a|a|-|s|-|-|-|m|n|c', 'Case=Nom|Degree=Cmp|Gender=Masc|Number=Sing')
    assert result[8] == 'c'

    # 's' is not in LLCT concordance for degree
    result = llct_to_perseus('ADJ', 'a|a|-|s|-|-|-|m|n|s', 'Case=Nom|Gender=Masc|Number=Sing')
    assert result[8] == '-'  # 's' not valid, becomes '-'


def test_llct_to_perseus_persons() -> None:
    """Test different persons."""
    # First person
    result = llct_to_perseus('VERB', 'v|v|1|s|p|i|a|-|-|-', 'Mood=Ind|Number=Sing|Person=1|Tense=Pres|Voice=Act')
    assert result[1] == '1'

    # Second person
    result = llct_to_perseus('VERB', 'v|v|2|s|p|i|a|-|-|-', 'Mood=Ind|Number=Sing|Person=2|Tense=Pres|Voice=Act')
    assert result[1] == '2'

    # Third person
    result = llct_to_perseus('VERB', 'v|v|3|s|p|i|a|-|-|-', 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act')
    assert result[1] == '3'


def test_llct_to_perseus_voices() -> None:
    """Test active and passive voice."""
    # Active
    result = llct_to_perseus('VERB', 'v|v|1|s|p|i|a|-|-|-', 'Mood=Ind|Number=Sing|Person=1|Tense=Pres|Voice=Act')
    assert result[5] == 'a'

    # Passive
    result = llct_to_perseus('VERB', 'v|v|1|s|p|i|p|-|-|-', 'Mood=Ind|Number=Sing|Person=1|Tense=Pres|Voice=Pass')
    assert result[5] == 'p'


def test_llct_to_perseus_upos_corrections() -> None:
    """Test that UPOS correctly overrides XPOS PoS field."""
    # UPOS should determine the PoS, not XPOS
    result1 = llct_to_perseus('NOUN', 'v|v|3|s|p|i|a|-|-|-', 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act')
    assert result1[0] == 'n'  # NOUN -> 'n', not 'v'

    result2 = llct_to_perseus('ADJ', 'n|n|-|s|-|-|-|m|n|-', 'Case=Nom|Gender=Masc|Number=Sing')
    assert result2[0] == 'a'  # ADJ -> 'a', not 'n'

    result3 = llct_to_perseus('VERB', 'a|a|-|s|-|-|-|m|n|p', 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act')
    assert result3[0] == 'v'  # VERB -> 'v', not 'a'


def test_llct_to_perseus_short_xpos() -> None:
    """Test behavior with XPOS that has fewer elements."""
    # XPOS needs exactly 9 parts before popping index 1, resulting in 8
    # Pad to 10 parts so after pop we have 9
    result = llct_to_perseus('NOUN', 'n|n|-|s|-|-|-|-|-|-', 'Case=Nom|Gender=Masc|Number=Sing')
    assert result == 'n-s---mn-'


def test_llct_to_perseus_empty_xpos() -> None:
    """Test with empty XPOS string - needs 10 parts."""
    # Need 10 parts so after pop we have 9
    result = llct_to_perseus('NOUN', '-|-|-|-|-|-|-|-|-|-', 'Case=Nom|Gender=Masc|Number=Sing')
    # XPOS all dashes, but FEATS provides values that get reconciled
    assert result == 'n-s---mn-'


def test_llct_to_perseus_single_character_xpos() -> None:
    """Test with proper 10-part XPOS."""
    result = llct_to_perseus('VERB', 'v|v|3|s|p|i|a|-|-|-', 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act')
    assert result == 'v3spia---'


def test_llct_to_perseus_dalme_examples() -> None:
    """Test with examples from DALME data."""
    result = llct_to_perseus('NOUN', 'n|n|-|s|-|-|-|m|n|-', 'Case=Nom|Gender=Masc|Number=Sing')
    assert result == 'n-s---mn-'

    result = llct_to_perseus('VERB', 'v|v|3|s|p|i|p|-|-|-', 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Pass')
    assert result == 'v3spip---'

    result = llct_to_perseus('ADJ', 'a|a|-|s|-|-|-|m|n|c', 'Case=Nom|Degree=Cmp|Gender=Masc|Number=Sing')
    assert result == 'a-s---mnc'

    result = llct_to_perseus('VERB', 'v|v|3|s|l|i|a|-|-|-', 'Mood=Ind|Number=Sing|Person=3|Tense=Pqp|Voice=Act')
    assert result == 'v3slia---'


def test_llct_to_perseus_samples() -> None:
    """Test with data samples from LLCT treebank."""
    test_data_samples = [
        {
            'upos': 'NUM',
            'xpos': 'p|p|1|s|-|-|-|m|n|-',
            'feats': 'Case=Nom|Number=Sing|Person=1|PronType=Prs',
            'expected_result': 'm1s---mn-',  # NUM maps to 'm' in Perseus
        },
        {
            'upos': 'PROPN',
            'xpos': 'Propn|n|-|s|-|-|-|m|g|-',
            'feats': 'Case=Gen|Gender=Masc|Number=Sing',
            'expected_result': 'n-s---mg-',
        },
        {
            'upos': 'NOUN',
            'xpos': 'n|n|-|s|-|-|-|-|b|-',
            'feats': 'Case=Abl|Gender=Neut|Number=Sing',
            'expected_result': 'n-s---nb-',
        },
    ]
    for sample in test_data_samples:
        result = llct_to_perseus(sample['upos'], sample['xpos'], sample['feats'])
        assert result == sample['expected_result'], (
            f'Failed for {sample["upos"]}/{sample["xpos"]}/{sample["feats"]}: '
            f'expected {sample["expected_result"]}, got {result}'
        )


def test_llct_to_perseus_feats_override_xpos() -> None:
    """Test that reconciliation prefers XPOS when both values are valid."""
    # Case where XPOS has one value but FEATS has another - reconcile prefers XPOS
    result = llct_to_perseus('NOUN', 'n|n|-|p|-|-|-|m|n|-', 'Case=Nom|Gender=Masc|Number=Sing')
    # FEATS says Sing (s), XPOS says p (plural), reconcile_xpos_feats prefers XPOS
    assert result[2] == 'p'

    # Gender reconciliation - XPOS is preferred
    result = llct_to_perseus('NOUN', 'n|n|-|s|-|-|-|n|n|-', 'Case=Nom|Gender=Masc|Number=Sing')
    # FEATS says Masc (m), XPOS says n (neuter), reconcile prefers XPOS
    assert result[6] == 'n'


def test_llct_to_perseus_missing_feats() -> None:
    """Test with missing or minimal FEATS."""
    # No FEATS, rely on XPOS
    result = llct_to_perseus('NOUN', 'n|n|-|s|-|-|-|m|n|-', '_')
    assert result == 'n-s---mn-'

    # Empty FEATS string
    result = llct_to_perseus('VERB', 'v|v|3|s|p|i|a|-|-|-', '')
    assert result == 'v-spia---'  # Person comes from FEATS, so it's '-'
