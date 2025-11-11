import pytest

from nlp_utilities.converters.upos import dalme_to_upos


@pytest.mark.parametrize(
    ('dalme_tag', 'expected_upos'),
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
def test_dalme_to_upos_known_tags(dalme_tag: str, expected_upos: str) -> None:
    assert dalme_to_upos(dalme_tag) == expected_upos


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
def test_dalme_to_upos_unknown_tags(unknown_tag: str | None) -> None:
    assert dalme_to_upos(unknown_tag) == 'X'  # type: ignore [arg-type]
