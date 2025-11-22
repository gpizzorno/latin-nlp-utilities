"""Tests for PROIEL XPOS to Perseus converter functions."""

import pytest

from nlp_utilities.converters.xpos.proiel_converters import (
    _to_case,
    _to_degree,
    _to_gender,
    _to_mood,
    _to_number,
    _to_tense,
    _to_voice,
)


@pytest.mark.parametrize(
    ('input_value', 'expected'),
    [
        ('Sing', 's'),
        ('Plur', 'p'),
        ('Dual', '-'),
        ('', '-'),
        (None, '-'),
    ],
)
def test_to_number(input_value: str | None, expected: str) -> None:
    assert _to_number(input_value) == expected


@pytest.mark.parametrize(
    ('input_value', 'expected'),
    [
        ('Pres', 'p'),
        ('Past', 'r'),
        ('Pqp', 'l'),
        ('Fut', 'f'),
        ('Impf', '-'),
        ('', '-'),
        (None, '-'),
    ],
)
def test_to_tense(input_value: str | None, expected: str) -> None:
    assert _to_tense(input_value) == expected


@pytest.mark.parametrize(
    ('input_value', 'expected'),
    [
        ('Ind', 'i'),
        ('Sub', 's'),
        ('Imp', 'm'),
        ('Opt', '-'),
        ('', '-'),
        (None, '-'),
    ],
)
def test_to_mood(input_value: str | None, expected: str) -> None:
    assert _to_mood(input_value) == expected


@pytest.mark.parametrize(
    ('input_value', 'expected'),
    [
        ('Act', 'a'),
        ('Pass', 'p'),
        ('Mid', '-'),
        ('', '-'),
        (None, '-'),
    ],
)
def test_to_voice(input_value: str | None, expected: str) -> None:
    assert _to_voice(input_value) == expected


@pytest.mark.parametrize(
    ('input_value', 'expected'),
    [
        ('Fem', 'f'),
        ('Masc', 'm'),
        ('Neut', 'n'),
        ('Com', '-'),
        ('', '-'),
        (None, '-'),
    ],
)
def test_to_gender(input_value: str | None, expected: str) -> None:
    assert _to_gender(input_value) == expected


@pytest.mark.parametrize(
    ('input_value', 'expected'),
    [
        ('Abl', 'b'),
        ('Acc', 'a'),
        ('Dat', 'd'),
        ('Gen', 'g'),
        ('Nom', 'n'),
        ('Voc', 'v'),
        ('Loc', '-'),
        ('', '-'),
        (None, '-'),
    ],
)
def test_to_case(input_value: str | None, expected: str) -> None:
    assert _to_case(input_value) == expected


@pytest.mark.parametrize(
    ('input_value', 'expected'),
    [
        ('Cmp', 'c'),
        ('Pos', 'p'),
        ('Sup', 's'),
        ('Abs', '-'),
        ('', '-'),
        (None, '-'),
    ],
)
def test_to_degree(input_value: str | None, expected: str) -> None:
    assert _to_degree(input_value) == expected
