"""Test UPOS to Perseus position 1 mapping."""

from conllu_tools.utils.xpos import validate_xpos


def test_validate_xpos_noun_maps_to_n() -> None:
    """Test NOUN maps to 'n'."""
    result = validate_xpos('NOUN', None)
    assert result[0] == 'n'


def test_validate_xpos_verb_maps_to_v() -> None:
    """Test VERB maps to 'v'."""
    result = validate_xpos('VERB', None)
    assert result[0] == 'v'


def test_validate_xpos_adj_maps_to_a() -> None:
    """Test ADJ maps to 'a'."""
    result = validate_xpos('ADJ', None)
    assert result[0] == 'a'


def test_validate_xpos_adv_maps_to_d() -> None:
    """Test ADV maps to 'd'."""
    result = validate_xpos('ADV', None)
    assert result[0] == 'd'


def test_validate_xpos_pron_maps_to_p() -> None:
    """Test PRON maps to 'p'."""
    result = validate_xpos('PRON', None)
    assert result[0] == 'p'


def test_validate_xpos_num_maps_to_m() -> None:
    """Test NUM maps to 'm'."""
    result = validate_xpos('NUM', None)
    assert result[0] == 'm'


def test_validate_xpos_adp_maps_to_r() -> None:
    """Test ADP maps to 'r'."""
    result = validate_xpos('ADP', None)
    assert result[0] == 'r'


def test_validate_xpos_cconj_maps_to_c() -> None:
    """Test CCONJ maps to 'c'."""
    result = validate_xpos('CCONJ', None)
    assert result[0] == 'c'


def test_validate_xpos_sconj_maps_to_c() -> None:
    """Test SCONJ maps to 'c'."""
    result = validate_xpos('SCONJ', None)
    assert result[0] == 'c'


def test_validate_xpos_propn_maps_to_n() -> None:
    """Test PROPN maps to 'n'."""
    result = validate_xpos('PROPN', None)
    assert result[0] == 'n'


def test_validate_xpos_punct_maps_to_u() -> None:
    """Test PUNCT maps to 'u'."""
    result = validate_xpos('PUNCT', None)
    assert result[0] == 'u'


def test_validate_xpos_intj_maps_to_dash() -> None:
    """Test INTJ maps to '-'."""
    result = validate_xpos('INTJ', None)
    assert result[0] == '-'


def test_validate_xpos_x_maps_to_dash() -> None:
    """Test X maps to '-'."""
    result = validate_xpos('X', None)
    assert result[0] == '-'


def test_validate_xpos_unknown_upos_maps_to_dash() -> None:
    """Test unknown UPOS maps to '-'."""
    result = validate_xpos('UNKNOWN', None)
    assert result[0] == '-'
