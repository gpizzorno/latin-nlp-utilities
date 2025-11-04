import pytest

from latin_utilities.converters.dalmepos_to_upos import dalmepos_to_upos


@pytest.mark.parametrize(
    ('dalmepos_tag', 'expected_upos'),
    [
        ('adjective', 'ADJ'),
        ('adposition', 'ADP'),
        ('adverb', 'ADV'),
        ('coordinating conjunction', 'CCONJ'),
        ('gerund', 'VERB'),
        ('noun', 'NOUN'),
        ('numeral', 'NUM'),
        ('particle', 'PART'),
        ('pronoun', 'PRON'),
        ('proper noun', 'PROPN'),
        ('verb', 'VERB'),
    ],
)
def test_dalmepos_to_upos_known_tags(dalmepos_tag, expected_upos):
    assert dalmepos_to_upos(dalmepos_tag) == expected_upos


@pytest.mark.parametrize(
    'unknown_tag',
    [
        'interjection',
        'conjunction',
        'foo',
        '',
        None,
        123,
    ],
)
def test_dalmepos_to_upos_unknown_tags(unknown_tag):
    assert dalmepos_to_upos(unknown_tag) == 'X'
