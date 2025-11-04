"""Functions for converting between PROIEL and Perseus XPOS tags."""

# References:

# Perseus XPOS tags:
# https://github.com/PerseusDL/treebank_data/blob/master/v2.1/Latin/TAGSET.txt
# https://itreebank.marginalia.it/doc/Tagset_Perseus.pdf

# PROIEL XPOS tags:
# https://dev.syntacticus.org/development-guide/#part-of-speech-tags


def to_number(value):
    """Convert PROIEL 'num' to Perseus 3: 'number'."""
    concordance = {
        'Sing': 's',  # Singular
        'Plur': 'p',  # Plural
    }
    return concordance.get(value, '-')  # Return '-' if no match found


def to_tense(value):
    """Convert PROIEL 'tense' to Perseus 4: 'tense'."""
    concordance = {
        'Pres': 'p',  # Present
        'Past': 'r',  # Perfect
        'Pqp': 'l',  # Pluperfect
        'Fut': 'f',  # Future
    }
    return concordance.get(value, '-')  # Return '-' if no match found


def to_mood(value):
    """Convert PROIEL 'mood' to Perseus 5: 'mood'."""
    concordance = {
        'Ind': 'i',  # Indicative
        'Sub': 's',  # Subjunctive
        'Imp': 'm',  # Imperative
    }
    return concordance.get(value, '-')  # Return '-' if no match found


def to_voice(value):
    """Convert PROIEL 'voice' to Perseus 6: 'voice'."""
    concordance = {
        'Act': 'a',  # Active
        'Pass': 'p',  # Passive
    }
    return concordance.get(value, '-')  # Return '-' if no match found


def to_gender(value):
    """Convert PROIEL 'gender' to Perseus 7: 'gender'."""
    concordance = {
        'Fem': 'f',  # Feminine
        'Masc': 'm',  # Masculine
        'Neut': 'n',  # Neuter
    }
    return concordance.get(value, '-')  # Return '-' if no match found


def to_case(value):
    """Convert PROIEL 'case' to Perseus 8: 'case'."""
    concordance = {
        'Abl': 'b',  # Ablative
        'Acc': 'a',  # Accusative
        'Dat': 'd',  # Dative
        'Gen': 'g',  # Genitive
        'Nom': 'n',  # Nominative
        'Voc': 'v',  # Vocative
    }
    return concordance.get(value, '-')  # Return '-' if no match found


def to_degree(value):
    """Convert PROIEL 'degree' to Perseus 9: 'degree'."""
    concordance = {
        'Cmp': 'c',  # Comparative
        'Pos': 'p',  # Positive
        'Sup': 's',  # Superlative
    }
    return concordance.get(value, '-')  # Return '-' if no match found
