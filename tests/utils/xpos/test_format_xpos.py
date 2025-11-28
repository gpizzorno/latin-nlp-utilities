"""Tests for format_xpos function."""

import pytest

from conllu_tools.utils.xpos import format_xpos


def test_format_xpos_requires_upos() -> None:
    """Test that UPOS is required."""
    with pytest.raises(ValueError, match='UPOS must be provided to format XPOS'):
        format_xpos(None, 'n-s---mn-', {'Case': 'Nom'})  # type: ignore [arg-type]


def test_format_xpos_accepts_empty_feats_dict() -> None:
    """Test that empty FEATS dict is accepted."""
    result = format_xpos('NOUN', 'n-s---mn-', {})
    assert result == 'n-s---mn-'


def test_format_xpos_accepts_empty_feats_string() -> None:
    """Test that empty FEATS string is accepted."""
    result = format_xpos('NOUN', 'n-s---mn-', '')
    assert result == 'n-s---mn-'  # Perseus XPOS is preserved


def test_format_xpos_accepts_underscore_feats() -> None:
    """Test that underscore FEATS is accepted."""
    result = format_xpos('NOUN', 'n-s---mn-', '_')
    assert result == 'n-s---mn-'  # Perseus XPOS is preserved


def test_format_xpos_perseus_noun() -> None:
    """Test Perseus format noun."""
    result = format_xpos('NOUN', 'n-s---mn-', {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'})
    assert result == 'n-s---mn-'


def test_format_xpos_perseus_verb() -> None:
    """Test Perseus format verb."""
    result = format_xpos(
        'VERB',
        'v3spia---',
        {'Mood': 'Ind', 'Number': 'Sing', 'Person': '3', 'Tense': 'Pres', 'Voice': 'Act'},
    )
    assert result == 'v3spia---'


def test_format_xpos_perseus_adjective() -> None:
    """Test Perseus format adjective."""
    result = format_xpos('ADJ', 'a-s---fn-', {'Case': 'Nom', 'Gender': 'Fem', 'Number': 'Sing'})
    assert result == 'a-s---fn-'


def test_format_xpos_perseus_corrects_upos() -> None:
    """Test that UPOS overrides Perseus PoS character."""
    # XPOS has 'v' but UPOS is NOUN, should correct to 'n'
    result = format_xpos('NOUN', 'v3spia---', {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'})
    assert result == 'n3spia---'


def test_format_xpos_perseus_preserves_positions_2_to_9() -> None:
    """Test that positions 2-9 are preserved from Perseus XPOS."""
    result = format_xpos('VERB', 'v2pfspmac', {'Mood': 'Sub', 'Number': 'Plur', 'Person': '2', 'Tense': 'Fut'})
    assert result == 'v2pfspmac'


def test_format_xpos_perseus_with_all_dashes() -> None:
    """Test Perseus format with all dashes."""
    result = format_xpos('NOUN', 'n--------', {})
    assert result == 'n--------'


def test_format_xpos_perseus_lowercase_required() -> None:
    """Test that Perseus pattern requires lowercase."""
    # Perseus pattern: ^[123espitrlfndgumabvc-]{9}$
    result = format_xpos('NOUN', 'n-s---mn-', {'Case': 'Nom'})
    assert result == 'n-s---mn-'


def test_format_xpos_perseus_invalid_chars_fallback() -> None:
    """Test that invalid Perseus chars cause fallback."""
    # 'X' is not in Perseus pattern [123espitrlfndgumabvc-]
    result = format_xpos('NOUN', 'nXs---mn-', {'Case': 'Nom'})
    assert result == 'n--------'


def test_format_xpos_perseus_wrong_length_fallback() -> None:
    """Test that wrong length causes fallback."""
    result = format_xpos('NOUN', 'n-s---mn', {'Case': 'Nom'})  # 8 chars, should be 9
    assert result == 'n--------'


def test_format_xpos_llct_noun() -> None:
    """Test LLCT format noun."""
    result = format_xpos('NOUN', 'n|n|-|s|-|-|-|m|n|-', {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'})
    assert result == 'n-s---mn-'


def test_format_xpos_llct_verb() -> None:
    """Test LLCT format verb."""
    result = format_xpos(
        'VERB',
        'v|v|1|s|p|i|-|-|-|-',
        {'Mood': 'Ind', 'Number': 'Sing', 'Person': '1', 'Tense': 'Pres', 'Voice': 'Act'},
    )
    assert result == 'v1spia---'


def test_format_xpos_llct_adjective() -> None:
    """Test LLCT format adjective."""
    result = format_xpos('ADJ', 'a|a|-|s|-|-|-|f|n|p', {'Case': 'Nom', 'Gender': 'Fem', 'Number': 'Sing'})
    assert result == 'a-s---fn-'


def test_format_xpos_llct_propn() -> None:
    """Test LLCT format proper noun."""
    result = format_xpos('PROPN', 'Propn|n|-|s|-|-|-|m|g|-', {'Case': 'Gen', 'Gender': 'Masc', 'Number': 'Sing'})
    assert result == 'n-s---mg-'


def test_format_xpos_llct_with_all_dashes() -> None:
    """Test LLCT format with all dashes."""
    result = format_xpos('NOUN', 'n|n|-|-|-|-|-|-|-|-', {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'})
    assert result == 'n-s---mn-'


def test_format_xpos_ittb_noun() -> None:
    """Test ITTB format noun."""
    # ITTB format: N1|gen<code>|cas<code> (casC=dative singular)
    result = format_xpos('NOUN', 'N1|gen3|casC', {'Case': 'Dat', 'Gender': 'Neut', 'Number': 'Sing'})
    assert result == 'n-s---nd-'


def test_format_xpos_ittb_verb() -> None:
    """Test ITTB format verb."""
    # ITTB format: V1|gen<code>|tem<code>|mod<code> (e.g., gen6=3rd sing, tem1=present, modA=ind active)
    result = format_xpos(
        'VERB',
        'V1|gen6|tem1|modA',
        {'Mood': 'Ind', 'Number': 'Sing', 'Person': '3', 'Tense': 'Pres'},
    )
    assert result == 'v3spia---'


def test_format_xpos_ittb_adjective() -> None:
    """Test ITTB format adjective."""
    # ITTB format: A1|gen<code>|cas<code> (casC=dative)
    result = format_xpos('ADJ', 'A1|gen3|casC', {'Case': 'Dat', 'Gender': 'Neut', 'Number': 'Sing'})
    assert result == 'a-s---nd-'


def test_format_xpos_ittb_minimal() -> None:
    """Test ITTB format with minimal tags."""
    result = format_xpos('NOUN', 'N1', {})
    assert result == 'n--------'


def test_format_xpos_ittb_number_only() -> None:
    """Test ITTB format with number only (no letter prefix)."""
    result = format_xpos('VERB', '11', {})
    assert result == 'v--------'


def test_format_xpos_proiel_noun() -> None:
    """Test PROIEL format noun."""
    # PROIEL format: Nb (2 chars, uppercase then lowercase)
    result = format_xpos('NOUN', 'Nb', {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'})
    assert result == 'n-s---mn-'


def test_format_xpos_proiel_verb() -> None:
    """Test PROIEL format verb."""
    result = format_xpos(
        'VERB',
        'V-',
        {'Mood': 'Ind', 'Number': 'Sing', 'Person': '3', 'Tense': 'Pres', 'Voice': 'Act'},
    )
    assert result == 'v3spia---'


def test_format_xpos_proiel_adjective() -> None:
    """Test PROIEL format adjective."""
    result = format_xpos('ADJ', 'A-', {'Case': 'Nom', 'Gender': 'Fem', 'Number': 'Sing'})
    assert result == 'a-s---fn-'


def test_format_xpos_proiel_with_dash() -> None:
    """Test PROIEL format with dash in second position."""
    result = format_xpos('PRON', 'P-', {'Case': 'Dat', 'Number': 'Sing', 'Person': '1'})
    assert result == 'p1s----d-'


def test_format_xpos_none_xpos_noun() -> None:
    """Test with None XPOS for noun."""
    result = format_xpos('NOUN', None, {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'})
    assert result == 'n--------'


def test_format_xpos_none_xpos_verb() -> None:
    """Test with None XPOS for verb."""
    result = format_xpos('VERB', None, {'Mood': 'Ind', 'Person': '3', 'Tense': 'Pres'})
    assert result == 'v--------'


def test_format_xpos_none_xpos_unknown_upos() -> None:
    """Test with None XPOS and unknown UPOS."""
    result = format_xpos('INTJ', None, {})
    assert result == '---------'


def test_format_xpos_invalid_format() -> None:
    """Test with XPOS that doesn't match any pattern."""
    result = format_xpos('NOUN', 'invalid', {'Case': 'Nom'})
    assert result == 'n--------'


def test_format_xpos_empty_string() -> None:
    """Test with empty XPOS string."""
    result = format_xpos('NOUN', '', {'Case': 'Nom'})
    assert result == 'n--------'


def test_format_xpos_random_chars() -> None:
    """Test with random characters that don't match patterns."""
    result = format_xpos('VERB', 'xyz123abc', {'Mood': 'Ind'})
    assert result == 'v--------'


def test_format_xpos_feats_string_noun() -> None:
    """Test with FEATS as string for noun."""
    result = format_xpos('NOUN', 'n-s---mn-', 'Case=Nom|Gender=Masc|Number=Sing')
    assert result == 'n-s---mn-'


def test_format_xpos_feats_string_verb() -> None:
    """Test with FEATS as string for verb."""
    result = format_xpos('VERB', 'v3spia---', 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act')
    assert result == 'v3spia---'


def test_format_xpos_feats_string_llct() -> None:
    """Test with FEATS string and LLCT XPOS."""
    result = format_xpos('NOUN', 'n|n|-|s|-|-|-|m|n|-', 'Case=Nom|Gender=Masc|Number=Sing')
    assert result == 'n-s---mn-'


def test_format_xpos_feats_string_empty() -> None:
    """Test with empty FEATS string."""
    result = format_xpos('NOUN', None, '')
    assert result == 'n--------'


def test_format_xpos_feats_string_underscore() -> None:
    """Test with underscore FEATS string."""
    result = format_xpos('VERB', None, '_')
    assert result == 'v--------'


def test_format_xpos_upos_noun() -> None:
    """Test NOUN UPOS maps to 'n'."""
    result = format_xpos('NOUN', None, {})
    assert result[0] == 'n'


def test_format_xpos_upos_verb() -> None:
    """Test VERB UPOS maps to 'v'."""
    result = format_xpos('VERB', None, {})
    assert result[0] == 'v'


def test_format_xpos_upos_adj() -> None:
    """Test ADJ UPOS maps to 'a'."""
    result = format_xpos('ADJ', None, {})
    assert result[0] == 'a'


def test_format_xpos_upos_adv() -> None:
    """Test ADV UPOS maps to 'd'."""
    result = format_xpos('ADV', None, {})
    assert result[0] == 'd'


def test_format_xpos_upos_pron() -> None:
    """Test PRON UPOS maps to 'p'."""
    result = format_xpos('PRON', None, {})
    assert result[0] == 'p'


def test_format_xpos_upos_num() -> None:
    """Test NUM UPOS maps to 'm'."""
    result = format_xpos('NUM', None, {})
    assert result[0] == 'm'


def test_format_xpos_upos_adp() -> None:
    """Test ADP UPOS maps to 'r'."""
    result = format_xpos('ADP', None, {})
    assert result[0] == 'r'


def test_format_xpos_upos_conj() -> None:
    """Test CCONJ UPOS maps to 'c'."""
    result = format_xpos('CCONJ', None, {})
    assert result[0] == 'c'


def test_format_xpos_upos_sconj() -> None:
    """Test SCONJ UPOS maps to 'c'."""
    result = format_xpos('SCONJ', None, {})
    assert result[0] == 'c'


def test_format_xpos_upos_intj() -> None:
    """Test INTJ UPOS maps to '-'."""
    result = format_xpos('INTJ', None, {})
    assert result[0] == '-'


def test_format_xpos_upos_x() -> None:
    """Test X UPOS maps to '-'."""
    result = format_xpos('X', None, {})
    assert result[0] == '-'


def test_format_xpos_upos_punct() -> None:
    """Test PUNCT UPOS maps to 'u'."""
    result = format_xpos('PUNCT', None, {})
    assert result[0] == 'u'


def test_format_xpos_upos_propn() -> None:
    """Test PROPN UPOS maps to 'n'."""
    result = format_xpos('PROPN', None, {})
    assert result[0] == 'n'


def test_format_xpos_upos_unknown() -> None:
    """Test unknown UPOS maps to '-'."""
    result = format_xpos('UNKNOWN', None, {})
    assert result[0] == '-'


def test_format_xpos_perseus_overrides_position_0_only() -> None:
    """Test that Perseus XPOS only has position 0 overridden by UPOS."""
    # Input has wrong PoS but correct other positions
    result = format_xpos('NOUN', 'v3spia---', {})
    assert result == 'n3spia---'  # Only position 0 changed


def test_format_xpos_llct_converts_all_positions() -> None:
    """Test that LLCT conversion processes all positions."""
    result = format_xpos('VERB', 'v|v|2|p|f|s|p|m|a|c', 'Mood=Sub|Number=Plur|Person=2|Tense=Fut|Voice=Pass')
    # LLCT converter should handle all positions
    assert len(result) == 9


def test_format_xpos_mixed_case_upos() -> None:
    """Test that UPOS is case-sensitive."""
    # lowercase 'noun' should not match UPOS_TO_PERSEUS
    result = format_xpos('noun', None, {})
    assert result[0] == '-'  # Unknown UPOS


def test_format_xpos_perseus_pattern_strict() -> None:
    """Test that Perseus pattern is strictly enforced."""
    # Uppercase not allowed in Perseus pattern
    result = format_xpos('NOUN', 'N-S---MN-', {})
    assert result == 'n--------'  # Falls back due to uppercase


def test_format_xpos_llct_pattern_allows_propn() -> None:
    """Test that LLCT pattern allows 'Propn' prefix."""
    result = format_xpos('PROPN', 'Propn|n|-|s|-|-|-|m|n|-', {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'})
    assert result == 'n-s---mn-'


def test_format_xpos_ittb_pattern_optional_letter() -> None:
    """Test that ITTB pattern allows optional letter prefix."""
    # With letter
    result1 = format_xpos('NOUN', 'N1', {})
    assert result1 == 'n--------'

    # Without letter
    result2 = format_xpos('VERB', '11', {})
    assert result2 == 'v--------'


def test_format_xpos_proiel_requires_exact_2_chars() -> None:
    """Test that PROIEL pattern requires exactly 2 characters."""
    # Valid 2-char
    result1 = format_xpos('NOUN', 'Nb', {})
    assert len(result1) == 9

    # Invalid 1-char should fallback
    result2 = format_xpos('NOUN', 'N', {})
    assert result2 == 'n--------'

    # Invalid 3-char should fallback
    result3 = format_xpos('NOUN', 'Nbc', {})
    assert result3 == 'n--------'


def test_format_xpos_returns_9_chars_always() -> None:
    """Test that result is always 9 characters."""
    test_cases: list[tuple[str, str | None, dict[str, str]]] = [
        ('NOUN', None, {}),
        ('VERB', 'v3spia---', {}),
        ('ADJ', 'a|a|-|s|-|-|-|f|n|p', {}),
        ('PRON', 'P1', {}),
        ('NUM', 'Mb', {}),
        ('INTJ', 'invalid', {}),
    ]
    for upos, xpos, feats in test_cases:
        result = format_xpos(upos, xpos, feats)
        assert len(result) == 9, f'Expected 9 chars for {upos}/{xpos}, got {len(result)}'


def test_format_xpos_integration_llct_to_perseus() -> None:
    """Test full integration from LLCT to Perseus format."""
    result = format_xpos(
        'VERB',
        'v|v|3|p|p|i|p|-|-|-',
        'Mood=Ind|Number=Plur|Person=3|Tense=Pres|Voice=Pass',
    )
    assert result == 'v3ppip---'
    assert result[0] == 'v'  # UPOS
    assert result[1] == '3'  # Person
    assert result[2] == 'p'  # Number
    assert result[3] == 'p'  # Tense
    assert result[4] == 'i'  # Mood
    assert result[5] == 'p'  # Voice


def test_format_xpos_integration_ittb_to_perseus() -> None:
    """Test full integration from ITTB to Perseus format."""
    # ITTB format: N1|gen<code>|cas<code> (gen2=fem, casD=accusative singular)
    result = format_xpos('NOUN', 'N1|gen2|casD', 'Case=Acc|Gender=Fem|Number=Sing')
    assert result == 'n-s---fa-'


def test_format_xpos_integration_proiel_to_perseus() -> None:
    """Test full integration from PROIEL to Perseus format."""
    result = format_xpos('VERB', 'V-', 'Mood=Ind|Number=Sing|Person=1|Tense=Pres|Voice=Act')
    assert result == 'v1spia---'


def test_format_xpos_priority_order() -> None:
    """Test that format matching happens in correct priority order."""
    # Perseus format should match first (if valid)
    perseus_result = format_xpos('NOUN', 'n-s---mn-', {})
    assert perseus_result == 'n-s---mn-'

    # If not Perseus, check LLCT
    llct_result = format_xpos('NOUN', 'n|n|-|s|-|-|-|m|n|-', {})
    assert llct_result == 'n-s---mn-'

    # If not LLCT, check ITTB
    ittb_result = format_xpos('NOUN', 'N1|gen1|casA', {})
    assert ittb_result == 'n-s---mn-'

    # If not ITTB, check PROIEL
    proiel_result = format_xpos('NOUN', 'Nb', 'Case=Nom|Gender=Masc|Number=Sing')
    assert proiel_result == 'n-s---mn-'

    # If none match, fallback
    fallback_result = format_xpos('NOUN', 'unknown', {})
    assert fallback_result == 'n--------'
