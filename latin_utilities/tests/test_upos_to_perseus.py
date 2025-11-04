import pytest

from latin_utilities.converters.upos_to_perseus import upos_to_perseus


@pytest.mark.parametrize(
    ('upos_tag', 'expected'),
    [
        ('ADJ', 'a'),
        ('ADP', 'r'),
        ('ADV', 'd'),
        ('AUX', 'v'),
        ('CCONJ', 'c'),
        ('DET', 'p'),
        ('NOUN', 'n'),
        ('NUM', 'm'),
        ('PART', 't'),
        ('PRON', 'p'),
        ('PROPN', 'n'),
        ('PUNCT', 'u'),
        ('SCONJ', 'c'),
        ('VERB', 'v'),
        ('X', '-'),
    ],
)
def test_upos_to_perseus_known_tags(upos_tag, expected):
    assert upos_to_perseus(upos_tag) == expected


def test_upos_to_perseus_unknown_tag():
    assert upos_to_perseus('FOO') == '-'
    assert upos_to_perseus('') == '-'
    assert upos_to_perseus(None) == '-'


def test_upos_to_perseus_case_sensitivity():
    # Should be case-sensitive: "adj" is not "ADJ"
    assert upos_to_perseus('adj') == '-'
