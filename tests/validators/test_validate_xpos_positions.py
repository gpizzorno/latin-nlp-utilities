"""Test validation for each position."""

from nlp_utilities.validators import validate_xpos


def test_validate_xpos_corrects_pos_to_noun() -> None:
    """Test that NOUN UPOS validates positions but keeps position 1."""
    result = validate_xpos('NOUN', 'v3spia---')
    # Position 1 stays 'v', but invalid positions for noun are cleared
    assert result[0] == 'v'  # Position 1 not changed
    assert result[1] == '-'  # Position 2 cleared (person invalid for noun)
    assert result[2] == 's'  # Position 3 valid (number)
    assert result == 'v-s------'


def test_validate_xpos_corrects_pos_to_verb() -> None:
    """Test that VERB UPOS validates positions but keeps position 1."""
    result = validate_xpos('VERB', 'n-s---mn-')
    # Position 1 stays 'n', all positions valid for nominal
    assert result[0] == 'n'
    assert result == 'n-s---mn-'


def test_validate_xpos_corrects_pos_to_adj() -> None:
    """Test that ADJ UPOS validates positions but keeps position 1."""
    result = validate_xpos('ADJ', 'n-s---mn-')
    # Position 1 stays 'n', positions valid for nominal
    assert result[0] == 'n'
    assert result == 'n-s---mn-'


def test_validate_xpos_corrects_pos_to_adv() -> None:
    """Test that ADV UPOS sets position 1 to 'd'."""
    result = validate_xpos('ADV', 'd--------')
    assert result[0] == 'd'


def test_validate_xpos_corrects_pos_to_pron() -> None:
    """Test that PRON UPOS sets position 1 to 'p'."""
    result = validate_xpos('PRON', 'p1s----d-')
    assert result[0] == 'p'


def test_validate_xpos_position_2_valid_for_verb() -> None:
    """Test that position 2 is valid for verbs."""
    result = validate_xpos('VERB', 'v3spia---')
    assert result[1] == '3'  # Person preserved for verb


def test_validate_xpos_position_2_cleared_for_noun() -> None:
    """Test that position 2 is cleared for nouns."""
    result = validate_xpos('NOUN', 'n3s---mn-')
    assert result[1] == '-'  # Person cleared for noun


def test_validate_xpos_position_2_cleared_for_adj() -> None:
    """Test that position 2 is cleared for adjectives."""
    result = validate_xpos('ADJ', 'a3s---mn-')
    assert result[1] == '-'


def test_validate_xpos_position_2_preserved_dash() -> None:
    """Test that dash in position 2 is preserved."""
    result = validate_xpos('NOUN', 'n-s---mn-')
    assert result[1] == '-'


def test_validate_xpos_position_3_valid_for_noun() -> None:
    """Test that position 3 is valid for nouns."""
    result = validate_xpos('NOUN', 'n-s---mn-')
    assert result[2] == 's'  # Number preserved for noun


def test_validate_xpos_position_3_valid_for_verb() -> None:
    """Test that position 3 is valid for verbs."""
    result = validate_xpos('VERB', 'v3spia---')
    assert result[2] == 's'


def test_validate_xpos_position_3_valid_for_adj() -> None:
    """Test that position 3 is valid for adjectives."""
    result = validate_xpos('ADJ', 'a-s---fn-')
    assert result[2] == 's'


def test_validate_xpos_position_3_cleared_for_adv() -> None:
    """Test that position 3 is cleared for adverbs."""
    result = validate_xpos('ADV', 'd-s------')
    assert result[2] == '-'


def test_validate_xpos_positions_4_5_6_valid_for_verb() -> None:
    """Test that positions 4-6 are valid for verbs."""
    result = validate_xpos('VERB', 'v3spia---')
    assert result[3] == 'p'  # Tense
    assert result[4] == 'i'  # Mood
    assert result[5] == 'a'  # Voice


def test_validate_xpos_positions_4_5_6_cleared_for_noun() -> None:
    """Test that positions 4-6 are cleared for nouns."""
    result = validate_xpos('NOUN', 'n-spia-mn-')
    assert result[3] == '-'
    assert result[4] == '-'
    assert result[5] == '-'


def test_validate_xpos_positions_4_5_6_cleared_for_adj() -> None:
    """Test that positions 4-6 are cleared for adjectives."""
    result = validate_xpos('ADJ', 'a-spia-fnc')
    assert result[3] == '-'
    assert result[4] == '-'
    assert result[5] == '-'


def test_validate_xpos_positions_7_8_valid_for_noun() -> None:
    """Test that positions 7-8 are valid for nouns."""
    result = validate_xpos('NOUN', 'n-s---mn-')
    assert result[6] == 'm'  # Gender
    assert result[7] == 'n'  # Case


def test_validate_xpos_positions_7_8_valid_for_adj() -> None:
    """Test that positions 7-8 are valid for adjectives."""
    result = validate_xpos('ADJ', 'a-s---fnc')
    assert result[6] == 'f'
    assert result[7] == 'n'


def test_validate_xpos_positions_7_8_valid_for_pron() -> None:
    """Test that positions 7-8 are valid for pronouns."""
    result = validate_xpos('PRON', 'p1s---md-')
    assert result[6] == 'm'
    assert result[7] == 'd'


def test_validate_xpos_positions_7_8_cleared_for_verb() -> None:
    """Test that positions 7-8 can be valid for verbs (participles)."""
    result = validate_xpos('VERB', 'v3spiamn-')
    # Positions 7-8 ARE valid for verbs (participles can have gender/case)
    assert result[0] == 'v'
    assert result[6] == 'm'  # Valid
    assert result[7] == 'n'  # Valid


def test_validate_xpos_position_9_valid_for_adj() -> None:
    """Test that position 9 is valid for adjectives."""
    result = validate_xpos('ADJ', 'a-s---fnc')
    assert result[8] == 'c'  # Degree preserved


def test_validate_xpos_position_9_cleared_for_noun() -> None:
    """Test that position 9 is cleared for nouns."""
    result = validate_xpos('NOUN', 'n-s---mnc')
    assert result[8] == '-'


def test_validate_xpos_position_9_cleared_for_verb() -> None:
    """Test that position 9 is cleared for verbs."""
    result = validate_xpos('VERB', 'v3spiac--')
    assert result[8] == '-'
