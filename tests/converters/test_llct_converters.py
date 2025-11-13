"""Tests for LLCT to Perseus XPOS converters."""

from nlp_utilities.converters.xpos.llct_converters import llct_to_perseus


def test_llct_to_perseus_basic() -> None:
    """Test basic conversion with standard LLCT XPOS."""
    # LLCT format: POS|person|number|tense|mood|voice|gender|case|degree
    result = llct_to_perseus('NOUN', 'n|-|s|-|-|-|m|n|-')
    assert result == 'n-s---mn-'


def test_llct_to_perseus_verb() -> None:
    """Test conversion of a verb."""
    result = llct_to_perseus('VERB', 'v|1|s|p|i|-|-|-|-')
    assert result == 'v1spi----'


def test_llct_to_perseus_verb_passive() -> None:
    """Test conversion of a passive verb."""
    result = llct_to_perseus('VERB', 'v|3|p|p|i|p|-|-|-')
    assert result == 'v3ppip---'


def test_llct_to_perseus_adjective() -> None:
    """Test conversion of an adjective."""
    result = llct_to_perseus('ADJ', 'a|-|s|-|-|-|f|n|p')
    assert result == 'a-s---fnp'


def test_llct_to_perseus_adjective_comparative() -> None:
    """Test conversion of a comparative adjective."""
    result = llct_to_perseus('ADJ', 'a|-|s|-|-|-|m|a|c')
    assert result == 'a-s---mac'


def test_llct_to_perseus_pronoun() -> None:
    """Test conversion of a pronoun."""
    result = llct_to_perseus('PRON', 'p|1|s|-|-|-|-|d|-')
    assert result == 'p1s----d-'


def test_llct_to_perseus_corrects_pos() -> None:
    """Test that UPOS overrides XPOS PoS tag."""
    # Even if XPOS has 'n' for noun, UPOS 'VERB' should make it 'v'
    result = llct_to_perseus('VERB', 'n|3|s|p|i|a|-|-|-')
    assert result[0] == 'v'  # Corrected from 'n' to 'v'


def test_llct_to_perseus_preserves_all_positions() -> None:
    """Test that all positions are preserved correctly."""
    result = llct_to_perseus('VERB', 'v|2|p|f|s|p|m|a|c')
    assert len(result) == 9
    assert result == 'v2pfspmac'


def test_llct_to_perseus_with_dashes() -> None:
    """Test with various dash positions."""
    result = llct_to_perseus('NOUN', 'n|-|-|-|-|-|n|v|-')
    assert result == 'n-----nv-'


def test_llct_to_perseus_all_dashes() -> None:
    """Test with all features as dashes."""
    result = llct_to_perseus('X', 'x|-|-|-|-|-|-|-|-')
    # UPOS 'X' maps to '-'
    assert result == '---------'


def test_llct_to_perseus_unknown_upos() -> None:
    """Test with unknown UPOS tag."""
    result = llct_to_perseus('INTJ', 'i|-|-|-|-|-|-|-|-')
    assert result[0] == '-'  # Unknown UPOS


def test_llct_to_perseus_noun_cases() -> None:
    """Test different noun cases."""
    # Nominative
    result = llct_to_perseus('NOUN', 'n|-|s|-|-|-|m|n|-')
    assert result[7] == 'n'

    # Genitive
    result = llct_to_perseus('NOUN', 'n|-|s|-|-|-|m|g|-')
    assert result[7] == 'g'

    # Dative
    result = llct_to_perseus('NOUN', 'n|-|s|-|-|-|m|d|-')
    assert result[7] == 'd'

    # Accusative
    result = llct_to_perseus('NOUN', 'n|-|s|-|-|-|m|a|-')
    assert result[7] == 'a'

    # Vocative
    result = llct_to_perseus('NOUN', 'n|-|s|-|-|-|m|v|-')
    assert result[7] == 'v'

    # Ablative
    result = llct_to_perseus('NOUN', 'n|-|s|-|-|-|m|b|-')
    assert result[7] == 'b'


def test_llct_to_perseus_verb_tenses() -> None:
    """Test different verb tenses."""
    # Present
    result = llct_to_perseus('VERB', 'v|1|s|p|i|a|-|-|-')
    assert result[3] == 'p'

    # Imperfect
    result = llct_to_perseus('VERB', 'v|1|s|i|i|a|-|-|-')
    assert result[3] == 'i'

    # Future
    result = llct_to_perseus('VERB', 'v|1|s|f|i|a|-|-|-')
    assert result[3] == 'f'

    # Perfect
    result = llct_to_perseus('VERB', 'v|1|s|r|i|a|-|-|-')
    assert result[3] == 'r'

    # Pluperfect
    result = llct_to_perseus('VERB', 'v|1|s|l|i|a|-|-|-')
    assert result[3] == 'l'

    # Future perfect
    result = llct_to_perseus('VERB', 'v|1|s|t|i|a|-|-|-')
    assert result[3] == 't'


def test_llct_to_perseus_verb_moods() -> None:
    """Test different verb moods."""
    # Indicative
    result = llct_to_perseus('VERB', 'v|1|s|p|i|a|-|-|-')
    assert result[4] == 'i'

    # Subjunctive
    result = llct_to_perseus('VERB', 'v|1|s|p|s|a|-|-|-')
    assert result[4] == 's'

    # Imperative
    result = llct_to_perseus('VERB', 'v|2|s|p|m|a|-|-|-')
    assert result[4] == 'm'

    # Infinitive
    result = llct_to_perseus('VERB', 'v|-|-|p|n|a|-|-|-')
    assert result[4] == 'n'

    # Participle
    result = llct_to_perseus('VERB', 'v|-|s|p|p|a|m|n|-')
    assert result[4] == 'p'

    # Gerund
    result = llct_to_perseus('VERB', 'v|-|-|-|d|a|-|-|-')
    assert result[4] == 'd'


def test_llct_to_perseus_numbers() -> None:
    """Test singular and plural."""
    # Singular
    result = llct_to_perseus('NOUN', 'n|-|s|-|-|-|m|n|-')
    assert result[2] == 's'

    # Plural
    result = llct_to_perseus('NOUN', 'n|-|p|-|-|-|m|n|-')
    assert result[2] == 'p'


def test_llct_to_perseus_genders() -> None:
    """Test different genders."""
    # Masculine
    result = llct_to_perseus('NOUN', 'n|-|s|-|-|-|m|n|-')
    assert result[6] == 'm'

    # Feminine
    result = llct_to_perseus('NOUN', 'n|-|s|-|-|-|f|n|-')
    assert result[6] == 'f'

    # Neuter
    result = llct_to_perseus('NOUN', 'n|-|s|-|-|-|n|n|-')
    assert result[6] == 'n'


def test_llct_to_perseus_degrees() -> None:
    """Test different degrees."""
    # Positive
    result = llct_to_perseus('ADJ', 'a|-|s|-|-|-|m|n|p')
    assert result[8] == 'p'

    # Comparative
    result = llct_to_perseus('ADJ', 'a|-|s|-|-|-|m|n|c')
    assert result[8] == 'c'

    # Superlative
    result = llct_to_perseus('ADJ', 'a|-|s|-|-|-|m|n|s')
    assert result[8] == 's'


def test_llct_to_perseus_persons() -> None:
    """Test different persons."""
    # First person
    result = llct_to_perseus('VERB', 'v|1|s|p|i|a|-|-|-')
    assert result[1] == '1'

    # Second person
    result = llct_to_perseus('VERB', 'v|2|s|p|i|a|-|-|-')
    assert result[1] == '2'

    # Third person
    result = llct_to_perseus('VERB', 'v|3|s|p|i|a|-|-|-')
    assert result[1] == '3'


def test_llct_to_perseus_voices() -> None:
    """Test active and passive voice."""
    # Active
    result = llct_to_perseus('VERB', 'v|1|s|p|i|a|-|-|-')
    assert result[5] == 'a'

    # Passive
    result = llct_to_perseus('VERB', 'v|1|s|p|i|p|-|-|-')
    assert result[5] == 'p'


def test_llct_to_perseus_realistic_examples() -> None:
    """Test with realistic examples from actual treebank data."""
    # "dominus" - nominative singular masculine noun
    result = llct_to_perseus('NOUN', 'n|-|s|-|-|-|m|n|-')
    assert result == 'n-s---mn-'

    # "laudatur" - 3rd person singular present indicative passive
    result = llct_to_perseus('VERB', 'v|3|s|p|i|p|-|-|-')
    assert result == 'v3spip---'

    # "pulchrior" - comparative adjective nominative masculine singular
    result = llct_to_perseus('ADJ', 'a|-|s|-|-|-|m|n|c')
    assert result == 'a-s---mnc'

    # "amaverat" - 3rd singular pluperfect indicative active
    result = llct_to_perseus('VERB', 'v|3|s|l|i|a|-|-|-')
    assert result == 'v3slia---'


def test_llct_to_perseus_upos_corrections() -> None:
    """Test that UPOS correctly overrides XPOS PoS field."""
    # UPOS should determine the PoS, not XPOS
    result1 = llct_to_perseus('NOUN', 'v|3|s|p|i|a|-|-|-')
    assert result1[0] == 'n'  # NOUN -> 'n', not 'v'

    result2 = llct_to_perseus('ADJ', 'n|-|s|-|-|-|m|n|-')
    assert result2[0] == 'a'  # ADJ -> 'a', not 'n'

    result3 = llct_to_perseus('VERB', 'a|-|s|-|-|-|m|n|p')
    assert result3[0] == 'v'  # VERB -> 'v', not 'a'


def test_llct_to_perseus_short_xpos() -> None:
    """Test behavior with XPOS that has fewer elements."""
    # If XPOS is malformed with fewer pipes, join should still work
    result = llct_to_perseus('NOUN', 'n|-|s')
    assert result == 'n-s'


def test_llct_to_perseus_long_xpos() -> None:
    """Test behavior with XPOS that has more elements."""
    # If XPOS has extra fields, they should be preserved
    result = llct_to_perseus('NOUN', 'n|-|s|-|-|-|m|n|-|extra')
    assert result == 'n-s---mn-extra'


def test_llct_to_perseus_empty_xpos() -> None:
    """Test with empty XPOS string."""
    result = llct_to_perseus('NOUN', '')
    assert result == 'n'


def test_llct_to_perseus_single_character_xpos() -> None:
    """Test with single character XPOS."""
    result = llct_to_perseus('VERB', 'x')
    assert result == 'v'
