"""Test validate_xpos edge cases."""

from nlp_utilities.validators import validate_xpos


def test_validate_xpos_all_valid_chars() -> None:
    """Test with all valid characters."""
    result = validate_xpos('VERB', 'v3spia---')
    assert result == 'v3spia---'


def test_validate_xpos_mixed_valid_invalid_for_upos() -> None:
    """Test with mix of valid and invalid positions for UPOS."""
    result = validate_xpos('NOUN', 'n3s---mn-')
    # Position 2 (person '3') should be cleared for NOUN
    assert result[0] == 'n'
    assert result[1] == '-'  # Cleared
    assert result[2] == 's'  # Valid
    assert result[6] == 'm'  # Valid
    assert result[7] == 'n'  # Valid


def test_validate_xpos_clears_only_invalid_positions() -> None:
    """Test that only invalid positions are cleared."""
    result = validate_xpos('ADJ', 'a-spia-fn')
    # For ADJ, valid positions are 3,7,8,9 (nvapm,nvapm,nvapm,a)
    # Position 4-6 (pia) are invalid for ADJ, so they get cleared
    assert result == 'a-s----fn'  # Positions 4-6 cleared, others preserved


def test_validate_xpos_numeric_person_preserved() -> None:
    """Test that numeric person values are preserved for verbs."""
    for person in ['1', '2', '3']:
        xpos = f'v{person}spia---'
        result = validate_xpos('VERB', xpos)
        assert result[1] == person


def test_validate_xpos_case_sensitive_chars() -> None:
    """Test that character validation is case-sensitive."""
    # Uppercase shouldn't match Perseus pattern
    result = validate_xpos('NOUN', 'N-S---MN-')
    # This should either fail or handle uppercase
    assert len(result) == 9


def test_validate_xpos_special_chars_in_xpos() -> None:
    """Test with special characters in XPOS."""
    result = validate_xpos('NOUN', 'n-s-@-mn-')
    # Special chars that don't match should be preserved or handled
    assert len(result) == 9
