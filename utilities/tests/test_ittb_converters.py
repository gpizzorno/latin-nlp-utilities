import pytest

from utilities.converters.ittb_to_perseus import (
    cas_to_case,
    cas_to_number,
    gen_to_gender,
    gen_to_number,
    gen_to_person,
    grnp_to_degree,
    mod_to_mood,
    mod_to_voice,
    tem_to_tense,
)


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('4', '1'),
        ('7', '1'),
        ('5', '2'),
        ('8', '2'),
        ('6', '3'),
        ('9', '3'),
        ('0', '-'),
        ('x', '-'),
    ],
)
def test_gen_to_person(value, expected):
    assert gen_to_person(value) == expected


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('4', 's'),
        ('5', 's'),
        ('6', 's'),
        ('7', 'p'),
        ('8', 'p'),
        ('9', 'p'),
        ('0', '-'),
        ('x', '-'),
    ],
)
def test_gen_to_number(value, expected):
    assert gen_to_number(value) == expected


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('A', 's'),
        ('B', 's'),
        ('C', 's'),
        ('D', 's'),
        ('E', 's'),
        ('F', 's'),
        ('J', 'p'),
        ('K', 'p'),
        ('L', 'p'),
        ('M', 'p'),
        ('N', 'p'),
        ('O', 'p'),
        ('Z', '-'),
        ('', '-'),
    ],
)
def test_cas_to_number(value, expected):
    assert cas_to_number(value) == expected


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('1', 'p'),
        ('2', 'i'),
        ('3', 'f'),
        ('4', 'r'),
        ('5', 'l'),
        ('6', 't'),
        ('0', '-'),
        ('x', '-'),
    ],
)
def test_tem_to_tense(value, expected):
    assert tem_to_tense(value) == expected


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('A', 'i'),
        ('J', 'i'),
        ('B', 's'),
        ('K', 's'),
        ('H', 'n'),
        ('Q', 'n'),
        ('C', 'm'),
        ('L', 'm'),
        ('D', 'p'),
        ('M', 'p'),
        ('E', 'd'),
        ('N', 'd'),
        ('O', 'g'),
        ('G', 'u'),
        ('P', 'u'),
        ('X', '-'),
        ('', '-'),
    ],
)
def test_mod_to_mood(value, expected):
    assert mod_to_mood(value) == expected


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('A', 'a'),
        ('B', 'a'),
        ('C', 'a'),
        ('D', 'a'),
        ('E', 'a'),
        ('G', 'a'),
        ('H', 'a'),
        ('J', 'p'),
        ('K', 'p'),
        ('L', 'p'),
        ('M', 'p'),
        ('N', 'p'),
        ('O', 'p'),
        ('P', 'p'),
        ('Q', 'p'),
        ('X', '-'),
        ('', '-'),
    ],
)
def test_mod_to_voice(value, expected):
    assert mod_to_voice(value) == expected


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('1', 'm'),
        ('2', 'f'),
        ('3', 'n'),
        ('0', '-'),
        ('x', '-'),
    ],
)
def test_gen_to_gender(value, expected):
    assert gen_to_gender(value) == expected


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('A', 'n'),
        ('J', 'n'),
        ('B', 'g'),
        ('K', 'g'),
        ('C', 'd'),
        ('L', 'd'),
        ('D', 'a'),
        ('M', 'a'),
        ('E', 'v'),
        ('N', 'v'),
        ('F', 'b'),
        ('O', 'b'),
        ('Z', '-'),
        ('', '-'),
    ],
)
def test_cas_to_case(value, expected):
    assert cas_to_case(value) == expected


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('1', 'p'),
        ('2', 'c'),
        ('3', 's'),
        ('0', '-'),
        ('x', '-'),
    ],
)
def test_grnp_to_degree(value, expected):
    assert grnp_to_degree(value) == expected
