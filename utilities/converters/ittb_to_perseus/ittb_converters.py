"""Functions for converting between ITTB and Perseus XPOS tags."""

# References:

# Perseus XPOS tags:
# https://github.com/PerseusDL/treebank_data/blob/master/v2.1/Latin/TAGSET.txt
# https://itreebank.marginalia.it/doc/Tagset_Perseus.pdf

# ITTB XPOS tags:
# https://itreebank.marginalia.it/doc/Tagset_IT.pdf
# https://itreebank.marginalia.it/doc/Tagset_IT_README.txt


def gen_to_person(value):
    """Convert ITTB 'gen' to Perseus 2: 'person'."""
    concordance = [
        (['4', '7'], '1'),  # First person
        (['5', '8'], '2'),  # Second person
        (['6', '9'], '3'),  # Third person
    ]
    for gen_values, person in concordance:
        if value in gen_values:
            return person
    return '-'  # Return '-' if no match found


def gen_to_number(value):
    """Convert ITTB 'gen' to Perseus 3: 'number'."""
    concordance = [
        (['4', '5', '6'], 's'),  # Singular
        (['7', '8', '9'], 'p'),  # Plural
    ]
    for gen_values, number in concordance:
        if value in gen_values:
            return number
    return '-'  # Return '-' if no match found


def cas_to_number(value):
    """Convert ITTB 'cas' to Perseus 3: 'number'."""
    concordance = [
        (['A', 'B', 'C', 'D', 'E', 'F'], 's'),  # Singular
        (['J', 'K', 'L', 'M', 'N', 'O'], 'p'),  # Plural
    ]
    for cas_values, number in concordance:
        if value in cas_values:
            return number
    return '-'  # Return '-' if no match found


def tem_to_tense(value):
    """Convert ITTB 'tem' to Perseus 4: 'tense'."""
    concordance = {
        '1': 'p',  # Present
        '2': 'i',  # Imperfect
        '3': 'f',  # Future
        '4': 'r',  # Perfect
        '5': 'l',  # Pluperfect
        '6': 't',  # Future Perfect
    }
    return concordance.get(value, '-')  # Return '-' if no match found


def mod_to_mood(value):
    """Convert ITTB 'mod' to Perseus 5: 'mood'."""
    concordance = [
        (['A', 'J'], 'i'),  # Indicative
        (['B', 'K'], 's'),  # Subjunctive
        (['H', 'Q'], 'n'),  # Infinitive
        (['C', 'L'], 'm'),  # Imperative
        (['D', 'M'], 'p'),  # Participle
        (['E', 'N'], 'd'),  # Gerund
        (['O'], 'g'),  # Gerundive
        (['G', 'P'], 'u'),  # Uncertain
    ]
    for mod_values, mood in concordance:
        if value in mod_values:
            return mood
    return '-'  # Return '-' if no match found


def mod_to_voice(value):
    """Convert ITTB 'mod' to Perseus 6: 'voice'."""
    concordance = [
        (['A', 'B', 'C', 'D', 'E', 'G', 'H'], 'a'),  # Active
        (['J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q'], 'p'),  # Passive
    ]
    for mod_values, voice in concordance:
        if value in mod_values:
            return voice
    return '-'  # Return '-' if no match found


def gen_to_gender(value):
    """Convert ITTB 'gen' to Perseus 7: 'gender'."""
    concordance = {
        '1': 'm',  # Masculine
        '2': 'f',  # Feminine
        '3': 'n',  # Neuter
    }
    return concordance.get(value, '-')  # Return '-' if no match found


def cas_to_case(value):
    """Convert ITTB 'cas' to Perseus 8: 'case'."""
    concordance = [
        (['A', 'J'], 'n'),  # Nominative
        (['B', 'K'], 'g'),  # Genitive
        (['C', 'L'], 'd'),  # Dative
        (['D', 'M'], 'a'),  # Accusative
        (['E', 'N'], 'v'),  # Vocative
        (['F', 'O'], 'b'),  # Ablative
    ]
    for cas_values, case in concordance:
        if value in cas_values:
            return case
    return '-'  # Return '-' if no match found


def grnp_to_degree(value):
    """Convert ITTB 'grn' or 'grp' to Perseus 9: 'degree'."""
    concordance = {
        '1': 'p',  # Positive
        '2': 'c',  # Comparative
        '3': 's',  # Superlative
    }
    return concordance.get(value, '-')  # Return '-' if no match found
