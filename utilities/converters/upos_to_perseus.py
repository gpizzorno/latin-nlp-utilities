"""Convert UPOS tags to Perseus equivalent part-of-speech tags."""

# References:
# https://github.com/PerseusDL/treebank_data/blob/master/v2.1/Latin/TAGSET.txt
# https://itreebank.marginalia.it/doc/Tagset_Perseus.pdf

UPOS_TO_PERSEUS = {
    'ADJ': 'a',
    'ADP': 'r',
    'ADV': 'd',
    'AUX': 'v',
    'CCONJ': 'c',
    'DET': 'p',
    'NOUN': 'n',
    'NUM': 'm',
    'PART': 't',
    'PRON': 'p',
    'PROPN': 'n',
    'PUNCT': 'u',
    'SCONJ': 'c',
    'VERB': 'v',
    'X': '-',
}


def upos_to_perseus(upos_tag):
    """Convert a UPOS tag to a Perseus tag."""
    return UPOS_TO_PERSEUS.get(upos_tag, '-')  # Return '-' for unknown tags
