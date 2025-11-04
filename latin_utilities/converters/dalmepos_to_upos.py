"""Converter from DALME POS tags to Universal POS tags."""

TAGS = {
    'adjective': 'ADJ',
    'adposition': 'ADP',
    'adverb': 'ADV',
    'coordinating conjunction': 'CCONJ',
    'gerund': 'VERB',
    'noun': 'NOUN',
    'numeral': 'NUM',
    'particle': 'PART',
    'pronoun': 'PRON',
    'proper noun': 'PROPN',
    'verb': 'VERB',
}


def dalmepos_to_upos(dalmepos_tag):
    """Convert a DALME POS tag to a Universal POS tag."""
    return TAGS.get(dalmepos_tag, 'X')  # Return 'X' for unknown tags
