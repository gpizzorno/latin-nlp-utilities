"""Tests for normalize_xpos function."""

from __future__ import annotations

import pytest

from nlp_utilities.normalizers import normalize_xpos


def test_normalize_xpos_valid() -> None:
    """Test normalizing XPOS with valid data."""
    upos = 'NOUN'
    xpos = 'Nabcde'
    result = normalize_xpos(upos, xpos)
    assert result == 'n-b---'


def test_normalize_xpos_missing_upos_raises_error() -> None:
    """Test that missing UPOS raises ValueError."""
    with pytest.raises(ValueError, match='Must pass both UPOS and XPOS'):
        normalize_xpos(None, 'Xabc')  # type: ignore [arg-type]


def test_normalize_xpos_empty_upos_raises_error() -> None:
    """Test that empty UPOS raises ValueError."""
    with pytest.raises(ValueError, match='Must pass both UPOS and XPOS'):
        normalize_xpos('', 'Xabc')


def test_normalize_xpos_missing_xpos_raises_error() -> None:
    """Test that missing XPOS raises ValueError."""
    with pytest.raises(ValueError, match='Must pass both UPOS and XPOS'):
        normalize_xpos('NOUN', None)  # type: ignore [arg-type]


def test_normalize_xpos_empty_xpos_raises_error() -> None:
    """Test that empty XPOS raises ValueError."""
    with pytest.raises(ValueError, match='Must pass both UPOS and XPOS'):
        normalize_xpos('NOUN', '')


def test_normalize_xpos_verb() -> None:
    """Test normalizing XPOS for verb."""
    # VERB -> 'v', checking if 'v' is valid at each position
    upos = 'VERB'
    xpos = 'Vabcdefgh'
    result = normalize_xpos(upos, xpos)
    # Position 2: 'v' in 'v' -> keep 'a'
    # Position 3: 'v' in 'nvapm' -> keep 'b'
    # Position 4: 'v' in 'v' -> keep 'c'
    # Position 5: 'v' in 'v' -> keep 'd'
    # Position 6: 'v' in 'v' -> keep 'e'
    # Position 7: 'v' in 'nvapm' -> keep 'f'
    # Position 8: 'v' in 'nvapm' -> keep 'g'
    # Position 9: 'v' not in 'a' -> replace with '-'
    assert result == 'vabcdefg-'


def test_normalize_xpos_adjective() -> None:
    """Test normalizing XPOS for adjective."""
    upos = 'ADJ'
    xpos = 'Aabcdefgh'
    result = normalize_xpos(upos, xpos)
    # ADJ -> 'a', checking if 'a' is valid at each position
    # Position 2: 'a' not in 'v' -> '-'
    # Position 3: 'a' in 'nvapm' -> keep 'b'
    # Position 4: 'a' not in 'v' -> '-'
    # Position 5: 'a' not in 'v' -> '-'
    # Position 6: 'a' not in 'v' -> '-'
    # Position 7: 'a' in 'nvapm' -> keep 'f'
    # Position 8: 'a' in 'nvapm' -> keep 'g'
    # Position 9: 'a' in 'a' -> keep 'h'
    assert result == 'a-b---fgh'


def test_normalize_xpos_pronoun() -> None:
    """Test normalizing XPOS for pronoun."""
    upos = 'PRON'
    xpos = 'Pabcdefgh'
    result = normalize_xpos(upos, xpos)
    # PRON -> 'p', checking if 'p' is valid at each position
    # Position 2: 'p' not in 'v' -> '-'
    # Position 3: 'p' in 'nvapm' -> keep 'b'
    # Position 4: 'p' not in 'v' -> '-'
    # Position 5: 'p' not in 'v' -> '-'
    # Position 6: 'p' not in 'v' -> '-'
    # Position 7: 'p' in 'nvapm' -> keep 'f'
    # Position 8: 'p' in 'nvapm' -> keep 'g'
    # Position 9: 'p' not in 'a' -> '-'
    assert result == 'p-b---fg-'


def test_normalize_xpos_unknown_upos() -> None:
    """Test normalizing XPOS with unknown UPOS."""
    upos = 'INTJ'
    xpos = 'Iabcdefgh'
    result = normalize_xpos(upos, xpos)
    # Unknown UPOS maps to '-', which is never in any validity set
    assert result == '---------'


def test_normalize_xpos_single_char_xpos() -> None:
    """Test with single character XPOS."""
    upos = 'NOUN'
    xpos = 'N'
    result = normalize_xpos(upos, xpos)
    # Only first char, no positions to iterate
    assert result == 'n'


def test_normalize_xpos_two_char_xpos() -> None:
    """Test with two character XPOS."""
    upos = 'NOUN'
    xpos = 'Na'
    result = normalize_xpos(upos, xpos)
    # First char 'n', then position 2 (index 1): 'a' not in 'v'
    assert result == 'n-'


def test_normalize_xpos_all_positions_valid() -> None:
    """Test XPOS where all positions are valid."""
    upos = 'VERB'
    xpos = 'Vvvvvvvvv'
    result = normalize_xpos(upos, xpos)
    # VERB -> 'v', checking if 'v' is valid at each position
    # Position 2: 'v' in 'v' -> keep
    # Position 3: 'v' in 'nvapm' -> keep
    # Position 4-6: 'v' in 'v' -> keep
    # Position 7-8: 'v' in 'nvapm' -> keep
    # Position 9: 'v' not in 'a' -> '-'
    assert result == 'vvvvvvvv-'


def test_normalize_xpos_all_positions_invalid() -> None:
    """Test XPOS where all positions are invalid."""
    upos = 'PUNCT'
    xpos = 'Uxxxxxxxxx'
    result = normalize_xpos(upos, xpos)
    # PUNCT -> 'u', 'u' is not in any validity set
    assert result == 'u---------'


def test_normalize_xpos_mixed_validity() -> None:
    """Test XPOS with mixed valid/invalid positions."""
    upos = 'NOUN'
    xpos = 'Nnavpmavn'
    result = normalize_xpos(upos, xpos)
    # NOUN -> 'n', checking if 'n' is valid at each position
    # Position 2: 'n' not in 'v' -> '-'
    # Position 3: 'n' in 'nvapm' -> keep 'a'
    # Position 4: 'n' not in 'v' -> '-'
    # Position 5: 'n' not in 'v' -> '-'
    # Position 6: 'n' not in 'v' -> '-'
    # Position 7: 'n' in 'nvapm' -> keep 'a'
    # Position 8: 'n' in 'nvapm' -> keep 'v'
    # Position 9: 'n' not in 'a' -> '-'
    assert result == 'n-a---av-'


def test_normalize_xpos_long_xpos() -> None:
    """Test with XPOS longer than expected."""
    upos = 'NOUN'
    xpos = 'Nabcdefghijk'
    result = normalize_xpos(upos, xpos)
    # NOUN -> 'n', checking if 'n' is valid at each position
    # Should process all characters after first
    # Positions 2, 4-6: 'n' not in 'v' -> '-'
    # Positions 3, 7-8: 'n' in 'nvapm' -> keep
    # Position 9: 'n' not in 'a' -> '-'
    # Positions 10-12: no validity rules defined, so 'n' not in '' -> '-'
    assert result == 'n-b---fg----'


def test_normalize_xpos_position_2_verb() -> None:
    """Test position 2 which is only valid for 'v'."""
    upos = 'VERB'
    xpos = 'Vv'
    result = normalize_xpos(upos, xpos)
    assert result == 'vv'


def test_normalize_xpos_position_2_noun() -> None:
    """Test position 2 for noun (should be invalid)."""
    upos = 'NOUN'
    xpos = 'Nn'
    result = normalize_xpos(upos, xpos)
    # Position 2: 'n' in 'v'? -> No
    assert result == 'n-'


def test_normalize_xpos_position_3_noun() -> None:
    """Test position 3 for noun (valid for 'nvapm')."""
    upos = 'NOUN'
    xpos = 'Nxn'
    result = normalize_xpos(upos, xpos)
    # Position 2: 'x' not in 'v' -> '-'
    # Position 3: 'n' in 'nvapm' -> 'n'
    assert result == 'n-n'


def test_normalize_xpos_position_9_adjective() -> None:
    """Test position 9 which is only valid for 'a' (adjectives)."""
    upos = 'ADJ'
    xpos = 'Axxxxxxxxa'
    result = normalize_xpos(upos, xpos)
    # ADJ -> 'a'
    # Position 2: 'a' not in 'v' -> '-'
    # Position 3: 'a' in 'nvapm' -> keep 'x'
    # Positions 4-6: 'a' not in 'v' -> '-'
    # Positions 7-8: 'a' in 'nvapm' -> keep 'x'
    # Position 9: 'a' in 'a' -> keep 'x'
    # Position 10: 'a' not in '' -> '-'
    assert result == 'a-x---xxx-'


def test_normalize_xpos_position_9_noun() -> None:
    """Test position 9 for noun (should be invalid)."""
    upos = 'NOUN'
    xpos = 'Nxxxxxxxxa'
    result = normalize_xpos(upos, xpos)
    # NOUN -> 'n'
    # Position 2: 'n' not in 'v' -> '-'
    # Position 3: 'n' in 'nvapm' -> keep 'x'
    # Positions 4-6: 'n' not in 'v' -> '-'
    # Positions 7-8: 'n' in 'nvapm' -> keep 'x'
    # Position 9: 'n' not in 'a' -> '-'
    # Position 10: 'n' not in '' -> '-'
    assert result == 'n-x---xx--'


def test_normalize_xpos_case_sensitive_upos() -> None:
    """Test that UPOS is case-sensitive."""
    upos = 'noun'  # lowercase
    xpos = 'Nabcde'
    result = normalize_xpos(upos, xpos)
    # lowercase 'noun' doesn't match UPOS tags, maps to '-'
    # '-' is never in any validity set
    assert result == '------'


def test_normalize_xpos_special_characters() -> None:
    """Test XPOS with special characters."""
    upos = 'NOUN'
    xpos = 'N-_+='
    result = normalize_xpos(upos, xpos)
    # NOUN -> 'n'
    # Position 2: 'n' not in 'v' -> '-'
    # Position 3: 'n' in 'nvapm' -> keep '_'
    # Positions 4-5: 'n' not in 'v' -> '-'
    assert result == 'n-_--'


def test_normalize_xpos_numeric_characters() -> None:
    """Test XPOS with numeric characters."""
    upos = 'NOUN'
    xpos = 'N12345'
    result = normalize_xpos(upos, xpos)
    # NOUN -> 'n'
    # Position 2: 'n' not in 'v' -> '-'
    # Position 3: 'n' in 'nvapm' -> keep '2'
    # Positions 4-6: 'n' not in 'v' -> '-'
    assert result == 'n-2---'


def test_normalize_xpos_all_upos_tags() -> None:
    """Test normalize_xpos with various UPOS tags."""
    # Note: The logic checks if the upos_tag character is IN the validity set for each position
    # VALIDITY_BY_POS = {2:'v', 3:'nvapm', 4:'v', 5:'v', 6:'v', 7:'nvapm', 8:'nvapm', 9:'a'}
    test_cases = [
        ('ADJ', 'Aabcde', 'a-b---'),  # 'a' in pos3,7,8,9 only
        ('ADP', 'Rabcde', 'r-----'),  # 'r' not in any validity set
        ('ADV', 'Dabcde', 'd-----'),  # 'd' not in any validity set
        ('AUX', 'Vabcde', 'vabcde'),  # 'v' in pos2,3,4,5,6,7,8
        ('CCONJ', 'Cabcde', 'c-----'),  # 'c' not in any validity set
        ('DET', 'Pabcde', 'p-b---'),  # 'p' in pos3,7,8 only
        ('NOUN', 'Nabcde', 'n-b---'),  # 'n' in pos3,7,8 only
        ('NUM', 'Mabcde', 'm-b---'),  # 'm' in pos3,7,8 only
        ('PART', 'Tabcde', 't-----'),  # 't' not in any validity set
        ('PRON', 'Pabcde', 'p-b---'),  # 'p' in pos3,7,8 only
        ('PROPN', 'Nabcde', 'n-b---'),  # 'n' in pos3,7,8 only
        ('PUNCT', 'Uabcde', 'u-----'),  # 'u' not in any validity set
        ('SCONJ', 'Cabcde', 'c-----'),  # 'c' not in any validity set
        ('VERB', 'Vabcde', 'vabcde'),  # 'v' in pos2,3,4,5,6,7,8
        ('X', 'Xabcde', '------'),  # 'X' -> '-', not in any validity set
    ]
    for upos, xpos, expected in test_cases:
        result = normalize_xpos(upos, xpos)
        # First 6 chars should match expected pattern
        assert result[:6] == expected, f'Failed for {upos}: got {result}, expected {expected}'
