"""Test validate_xpos with wrong length XPOS strings."""

from conllu_tools.utils.xpos import validate_xpos


def test_validate_xpos_too_short() -> None:
    """Test with XPOS shorter than 9 characters."""
    result = validate_xpos('NOUN', 'n-s--')
    assert result == 'n--------'


def test_validate_xpos_too_long() -> None:
    """Test with XPOS longer than 9 characters."""
    result = validate_xpos('NOUN', 'n-s---mn-extra')
    assert result == 'n--------'


def test_validate_xpos_empty_string() -> None:
    """Test with empty XPOS string."""
    result = validate_xpos('NOUN', '')
    assert result == 'n--------'


def test_validate_xpos_single_char() -> None:
    """Test with single character XPOS."""
    result = validate_xpos('NOUN', 'n')
    assert result == 'n--------'


def test_validate_xpos_eight_chars() -> None:
    """Test with 8 characters (one short)."""
    result = validate_xpos('NOUN', 'n-s---mn')
    assert result == 'n--------'
