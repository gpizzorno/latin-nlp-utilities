"""Test that dashes are always preserved."""

from nlp_utilities.validators import validate_xpos


def test_validate_xpos_preserves_all_dashes() -> None:
    """Test that all dashes are preserved."""
    result = validate_xpos('NOUN', 'n--------')
    assert result == 'n--------'


def test_validate_xpos_preserves_mixed_dashes() -> None:
    """Test that dashes in some positions are preserved."""
    result = validate_xpos('NOUN', 'n-s---m--')
    assert result == 'n-s---m--'


def test_validate_xpos_dash_never_cleared() -> None:
    """Test that dash is never changed to another character."""
    result = validate_xpos('VERB', 'v-s------')
    assert result[1] == '-'  # Dash stays dash
