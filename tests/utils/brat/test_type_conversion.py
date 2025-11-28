"""Tests for BRAT type conversion functions."""

from __future__ import annotations

from conllu_tools.utils.brat import safe_type_to_type, type_to_safe_type


def test_type_to_safe_type_colon() -> None:
    """Test conversion of colon to safe type."""
    assert type_to_safe_type(':') == '_colon_'


def test_type_to_safe_type_period() -> None:
    """Test conversion of period to safe type."""
    assert type_to_safe_type('.') == '_period_'


def test_type_to_safe_type_lt() -> None:
    """Test conversion of less-than to safe type."""
    assert type_to_safe_type('<') == '_lt_'


def test_type_to_safe_type_gt() -> None:
    """Test conversion of greater-than to safe type."""
    assert type_to_safe_type('>') == '_gt_'


def test_type_to_safe_type_plus() -> None:
    """Test conversion of plus to safe type."""
    assert type_to_safe_type('+') == '_plus_'


def test_type_to_safe_type_question() -> None:
    """Test conversion of question mark to safe type."""
    assert type_to_safe_type('?') == '_question_'


def test_type_to_safe_type_amp() -> None:
    """Test conversion of ampersand to safe type."""
    assert type_to_safe_type('&') == '_amp_'


def test_type_to_safe_type_exclamation() -> None:
    """Test conversion of exclamation to safe type."""
    assert type_to_safe_type('!') == '_exclamation_'


def test_type_to_safe_type_multiple_chars() -> None:
    """Test conversion of string with multiple special characters."""
    assert type_to_safe_type('obl:arg') == 'obl_colon_arg'
    assert type_to_safe_type('test.value') == 'test_period_value'


def test_type_to_safe_type_no_special_chars() -> None:
    """Test pass-through of strings with no special characters."""
    assert type_to_safe_type('nsubj') == 'nsubj'
    assert type_to_safe_type('NOUN') == 'NOUN'


def test_type_to_safe_type_empty_string() -> None:
    """Test conversion of empty string."""
    assert type_to_safe_type('') == ''


def test_type_to_safe_type_mixed_chars() -> None:
    """Test conversion of mixed alphanumeric and special characters."""
    assert type_to_safe_type('a:b+c') == 'a_colon_b_plus_c'


def test_safe_type_to_type_colon() -> None:
    """Test reverse conversion of colon from safe type."""
    assert safe_type_to_type('_colon_') == ':'


def test_safe_type_to_type_period() -> None:
    """Test reverse conversion of period from safe type."""
    assert safe_type_to_type('_period_') == '.'


def test_safe_type_to_type_lt() -> None:
    """Test reverse conversion of less-than from safe type."""
    assert safe_type_to_type('_lt_') == '<'


def test_safe_type_to_type_gt() -> None:
    """Test reverse conversion of greater-than from safe type."""
    assert safe_type_to_type('_gt_') == '>'


def test_safe_type_to_type_plus() -> None:
    """Test reverse conversion of plus from safe type."""
    assert safe_type_to_type('_plus_') == '+'


def test_safe_type_to_type_question() -> None:
    """Test reverse conversion of question mark from safe type."""
    assert safe_type_to_type('_question_') == '?'


def test_safe_type_to_type_amp() -> None:
    """Test reverse conversion of ampersand from safe type."""
    assert safe_type_to_type('_amp_') == '&'


def test_safe_type_to_type_exclamation() -> None:
    """Test reverse conversion of exclamation from safe type."""
    assert safe_type_to_type('_exclamation_') == '!'


def test_safe_type_to_type_multiple_markers() -> None:
    """Test reverse conversion of strings with multiple safe type markers."""
    assert safe_type_to_type('obl_colon_arg') == 'obl:arg'
    assert safe_type_to_type('test_period_value') == 'test.value'


def test_safe_type_to_type_no_markers() -> None:
    """Test pass-through of strings with no safe type markers."""
    assert safe_type_to_type('nsubj') == 'nsubj'
    assert safe_type_to_type('NOUN') == 'NOUN'


def test_safe_type_to_type_empty_string() -> None:
    """Test reverse conversion of empty string."""
    assert safe_type_to_type('') == ''


def test_round_trip_conversion() -> None:
    """Test that original → safe → original preserves the value."""
    test_strings = ['obl:arg', 'test.value', 'a+b', 'x<y', 'p>q', 'what?', 'a&b', 'alert!']
    for original in test_strings:
        safe = type_to_safe_type(original)
        restored = safe_type_to_type(safe)
        assert restored == original, f'Round-trip failed for {original}'
