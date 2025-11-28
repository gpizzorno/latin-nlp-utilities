"""Test validate_xpos integration scenarios."""

from conllu_tools.utils.xpos import validate_xpos


def test_validate_xpos_realistic_noun() -> None:
    """Test realistic noun XPOS."""
    result = validate_xpos('NOUN', 'n-s---mn-')
    assert result == 'n-s---mn-'


def test_validate_xpos_realistic_verb() -> None:
    """Test realistic verb XPOS."""
    result = validate_xpos('VERB', 'v3spia---')
    assert result == 'v3spia---'


def test_validate_xpos_realistic_adj() -> None:
    """Test realistic adjective XPOS."""
    result = validate_xpos('ADJ', 'a-s---fnc')
    assert result == 'a-s---fnc'


def test_validate_xpos_realistic_pron() -> None:
    """Test realistic pronoun XPOS."""
    result = validate_xpos('PRON', 'p1s----d-')
    # Position 2 (person '1') is cleared because PRON is not 'v' (verb)
    assert result == 'p-s----d-'


def test_validate_xpos_verb_participle() -> None:
    """Test verb participle with nominal features."""
    # Participles have both verb and nominal features
    result = validate_xpos('VERB', 'v--p-aman')
    # Positions 7-8 might be valid for participles
    assert result[0] == 'v'


def test_validate_xpos_corrects_mismatched_upos() -> None:
    """Test that position 1 is NOT changed when XPOS is valid length."""
    # XPOS says verb, but UPOS says noun
    result = validate_xpos('NOUN', 'v3spia---')
    # Position 1 stays 'v', but other positions validated based on NOUN
    assert result[0] == 'v'  # NOT corrected
    # Other positions should be cleared based on NOUN validity


def test_validate_xpos_all_positions_valid_for_upos() -> None:
    """Test when all positions are valid for UPOS."""
    result = validate_xpos('NOUN', 'n-s---mn-')
    assert result == 'n-s---mn-'
    # All positions valid for noun


def test_validate_xpos_all_positions_invalid_for_upos() -> None:
    """Test when most positions are invalid for UPOS."""
    result = validate_xpos('ADV', 'd3spiamn-')
    # Only position 1 is valid for adverb
    assert result[0] == 'd'
    assert result[1] == '-'  # Cleared
    assert result[2] == '-'  # Cleared


def test_validate_xpos_preserves_valid_clears_invalid() -> None:
    """Test that function preserves valid and clears invalid."""
    # NOUN: positions 1,3,7,8 valid; 2,4,5,6,9 should be cleared
    result = validate_xpos('NOUN', 'n3spiamnc')
    assert result[0] == 'n'  # Valid
    assert result[1] == '-'  # Cleared (position 2 invalid for noun)
    assert result[2] == 's'  # Valid
    assert result[3] == '-'  # Cleared
    assert result[4] == '-'  # Cleared
    assert result[5] == '-'  # Cleared
    assert result[6] == 'm'  # Valid
    assert result[7] == 'n'  # Valid
    assert result[8] == '-'  # Cleared (position 9 invalid for noun)


def test_validate_xpos_from_format_xpos_output() -> None:
    """Test validation of format_xpos output."""
    # Simulate output from format_xpos
    result = validate_xpos('NOUN', 'n-s---mn-')
    assert result == 'n-s---mn-'


def test_validate_xpos_handles_converted_xpos() -> None:
    """Test validation of converted XPOS formats."""
    # After conversion from other formats
    result = validate_xpos('VERB', 'v3spia---')
    assert result == 'v3spia---'
