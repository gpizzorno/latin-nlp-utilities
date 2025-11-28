"""Constants for CoNLL-U Tools."""

from __future__ import annotations

from importlib.resources import files

import regex as re

# Default data file paths
DEFAULT_FEATURES = files('conllu_tools.data').joinpath('feats.json')
DEFAULT_DEPRELS = files('conllu_tools.data').joinpath('deprels.json')
DEFAULT_AUX = files('conllu_tools.data').joinpath('auxiliaries.json')
BRAT_ANNOTATION_CONF = files('conllu_tools.data').joinpath('annotation.conf')
BRAT_TOOLS_CONF = files('conllu_tools.data').joinpath('tools.conf')
BRAT_VISUAL_CONF = files('conllu_tools.data').joinpath('visual.conf')

# Additional data file paths
DALME_FEATURES = files('conllu_tools.data').joinpath('dalme_features.json')

# Universal PoS tags
UPOS_TAGS = [
    'ADJ',
    'ADP',
    'ADV',
    'AUX',
    'CCONJ',
    'DET',
    'INTJ',
    'NOUN',
    'NUM',
    'PART',
    'PRON',
    'PROPN',
    'PUNCT',
    'SCONJ',
    'SYM',
    'VERB',
    'X',
]

# List of universal dependency relations
UNIVERSAL_DEPRELS = {
    'acl',
    'advcl',
    'advmod',
    'amod',
    'appos',
    'aux',
    'case',
    'cc',
    'ccomp',
    'clf',
    'compound',
    'conj',
    'cop',
    'csubj',
    'dep',
    'det',
    'discourse',
    'dislocated',
    'expl',
    'fixed',
    'flat',
    'goeswith',
    'iobj',
    'list',
    'mark',
    'nmod',
    'nsubj',
    'nummod',
    'obj',
    'obl',
    'orphan',
    'parataxis',
    'punct',
    'reparandum',
    'root',
    'vocative',
    'xcomp',
}

# Known attributes for MISC column
MISC_ATTRIBUTES = {
    'SpaceAfter',
    'Lang',
    'Translit',
    'LTranslit',
    'Gloss',
    'LId',
    'LDeriv',
}

# Allowed children of functional relations
FUNCTIONAL_RELATION_CHILDREN = {
    'mark': {'advmod', 'obl', 'goeswith', 'fixed', 'reparandum', 'conj', 'cc', 'punct'},
    'case': {'advmod', 'obl', 'goeswith', 'fixed', 'reparandum', 'conj', 'cc', 'punct'},
    'aux': {'goeswith', 'fixed', 'reparandum', 'conj', 'cc', 'punct'},
    'cop': {'goeswith', 'fixed', 'reparandum', 'conj', 'cc', 'punct'},
    'det': {'goeswith', 'fixed', 'reparandum', 'conj', 'cc', 'punct'},  # Added det
    'cc': {'goeswith', 'fixed', 'reparandum', 'conj', 'punct'},
    'fixed': {'goeswith', 'reparandum', 'conj', 'punct'},
    'goeswith': set(),  # No children allowed
    'punct': {'punct'},  # Only punct children allowed
}

# Certain UD relations must always go left-to-right
LEFT_TO_RIGHT_RELATIONS = {'conj', 'fixed', 'flat', 'goeswith', 'appos'}

# Allowed relations for parents of orphan tokens
ORPHAN_ALLOWED_PARENTS = {
    'conj',
    'parataxis',
    'root',
    'csubj',
    'ccomp',
    'advcl',
    'acl',
    'reparandum',
}

# Content relations
CONTENT_DEPRELS = {
    'nsubj',
    'obj',
    'iobj',
    'csubj',
    'ccomp',
    'xcomp',
    'obl',
    'vocative',
    'expl',
    'dislocated',
    'advcl',
    'advmod',
    'discourse',
    'nmod',
    'appos',
    'nummod',
    'acl',
    'amod',
    'conj',
    'fixed',
    'flat',
    'compound',
    'list',
    'parataxis',
    'orphan',
    'goeswith',
    'reparandum',
    'root',
    'dep',
}

# Functional relations
FUNCTIONAL_DEPRELS = {
    'aux',
    'cop',
    'mark',
    'det',
    'clf',
    'case',
    'cc',
}

# Functional relations for leaf validation
FUNCTIONAL_LEAVES_RELATIONS = {*FUNCTIONAL_DEPRELS, 'fixed', 'goeswith', 'punct'}

# Case relations for enhanced dependency processing
CASE_DEPRELS = {'obl', 'nmod', 'conj', 'advcl'}

# Universal dependency relation extensions
UNIVERSAL_DEPREL_EXTENSIONS = {'pass', 'relcl', 'xsubj'}

# Universal features (from UD guidelines)
UNIVERSAL_FEATURES = {
    'PronType',
    'NumType',
    'Poss',
    'Reflex',
    'Foreign',
    'Abbr',
    'Gender',
    'Animacy',
    'Number',
    'Case',
    'Definite',
    'Degree',
    'VerbForm',
    'Mood',
    'Tense',
    'Aspect',
    'Voice',
    'Evident',
    'Polarity',
    'Person',
    'Polite',
}

# Validity codes by POS for XPOS normalization
VALIDITY_BY_POS = {
    2: 'v',
    3: 'nvapm',
    4: 'v',
    5: 'v',
    6: 'v',
    7: 'nvapm',
    8: 'nvapm',
    9: 'a',
}

# Conllu token keys
TOKEN_KEYS = {
    'id': 'int',
    'form': 'str',
    'lemma': 'str',
    'upos': 'str',
    'xpos': 'str',
    'feats': 'dict',
    'head': 'int',
    'deprel': 'str',
    'deps': 'list',
    'misc': 'dict',
}

NESTABLE_KEYS = [k for k, v in TOKEN_KEYS.items() if v in ['dict', 'list']]

# RegEx patterns
MULTIWORD_TOKEN = r'^([1-9][0-9]*)(-)([1-9][0-9]*)$'
EMPTY_NODE = r'^[0-9]+\.[1-9][0-9]*$'
EMPTY_NODE_ID = r'^([0-9]+)\.([0-9]+)$'
BASIC_HEAD_MATCHER = r'^(0|[1-9][0-9]*)$'
ENHANCED_HEAD_MATCHER = r'^(0|[1-9][0-9]*)(\.[1-9][0-9]*)?$'
ENHANCED_DEPREL_PART = r'[\p{Ll}\p{Lm}\p{Lo}\p{M}]+(_[\p{Ll}\p{Lm}\p{Lo}\p{M}]+)*'
ENHANCED_DEPREL_MATCHER = rf'^[a-z]+(:[a-z]+)?(:{ENHANCED_DEPREL_PART})?(:[a-z]+)?$'
INVALID_DEPREL_MATCHER = r'^[a-z]+(:[a-z]+)?$'
# Feature format validation
# Feature name can have optional layered brackets: Feature[layer]
FEATURE_NAME_MATCHER = r'^[A-Z][A-Za-z0-9]*(?:\[[a-z0-9]+\])?$'
FEATURE_VALUE_MATCHER = r'^[A-Z0-9][A-Za-z0-9]*$'
# DEPREL-UPOS compatibility lists
DET_UPOS = r'^(DET|PRON)$'
NUMMOD_UPOS = r'^(NUM|NOUN|SYM)$'
ADVMOD_UPOS = r'^(ADV|ADJ|CCONJ|DET|PART|SYM)$'
EXPL_UPOS = r'^(PRON|DET|PART)$'
COP_UPOS = r'^(AUX|PRON|DET|SYM)$'
CASE_UPOS = r'^(PROPN|ADJ|PRON|DET|NUM|AUX)$'
MARK_UPOS = r'^(NOUN|PROPN|ADJ|PRON|DET|NUM|VERB|AUX|INTJ)$'
CC_UPOS = r'^(NOUN|PROPN|ADJ|PRON|DET|NUM|VERB|AUX|INTJ)$'
# UPOS-DEPREL compatibility lists
PUNCT_DEPREL = r'^(punct|root)$'
# XPOS Matchers
LLCT_XPOS_MATCHER = r'^(\w|Propn)(\|(\w|-)){9}$'
ITTB_XPOS_MATCHER = r'^[A-Z]?\d{1,2}(\|\w{4})*$'
PERSEUS_XPOS_MATCHER = r'^[123espitrlfndgumabvc-]{9}$'
PROIEL_XPOS_MATCHER = r'^[A-Z][a-z-]$'
# Condition matching patterns
NESTED_CONDITION_MATCHER = rf'({"|".join(TOKEN_KEYS)})=(any)?\((.+)\)'
CONDITION_COUNTER_MATCHER = rf'(?:(?:{"|".join(UPOS_TAGS)}|\*)\|?)+(\{{(\d+)(?:,(\d+))?\}})'

# Character mapping for CoNLL-X types to brat-compatible types
TYPE_TO_BRAT_TYPE = {
    '<': '_lt_',
    '>': '_gt_',
    '+': '_plus_',
    '?': '_question_',
    '&': '_amp_',
    ':': '_colon_',
    '.': '_period_',
    '!': '_exclamation_',
}

# Reverse mapping for brat-compatible types back to CoNLL-X types
BRAT_TYPE_TO_TYPE = {v: k for k, v in TYPE_TO_BRAT_TYPE.items()}

DEFAULT_WHITESPACE_EXCEPTIONS = [
    re.compile(r'[0-9 ]+', re.UNICODE),
    re.compile(r'[0-9 ]+[,.][0-9]+', re.UNICODE),
]

# Data for converters
DALME_TAGS = {
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

# Mapping from UPOS tags to Perseus DL tagset codes
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

# Mappings for ITTB to Perseus XPOS conversions
# https://github.com/PerseusDL/treebank_data/blob/master/v2.1/Latin/TAGSET.txt
# https://itreebank.marginalia.it/doc/Tagset_Perseus.pdf
# https://itreebank.marginalia.it/doc/Tagset_IT.pdf
# https://itreebank.marginalia.it/doc/Tagset_IT_README.txt
ITTB_CONCORDANCES = {
    'gen_to_person': [
        (['4', '7'], '1'),  # First person
        (['5', '8'], '2'),  # Second person
        (['6', '9'], '3'),  # Third person
    ],
    'gen_to_number': [
        (['4', '5', '6'], 's'),  # Singular
        (['7', '8', '9'], 'p'),  # Plural
    ],
    'cas_to_number': [
        (['A', 'B', 'C', 'D', 'E', 'F'], 's'),  # Singular
        (['J', 'K', 'L', 'M', 'N', 'O'], 'p'),  # Plural
    ],
    'tem_to_tense': {
        '1': 'p',  # Present
        '2': 'i',  # Imperfect
        '3': 'f',  # Future
        '4': 'r',  # Perfect
        '5': 'l',  # Pluperfect
        '6': 't',  # Future Perfect
    },
    'mod_to_mood': [
        (['A', 'J'], 'i'),  # Indicative
        (['B', 'K'], 's'),  # Subjunctive
        (['H', 'Q'], 'n'),  # Infinitive
        (['C', 'L'], 'm'),  # Imperative
        (['D', 'M'], 'p'),  # Participle
        (['E', 'N'], 'd'),  # Gerund
        (['O'], 'g'),  # Gerundive
        (['G', 'P'], 'u'),  # Uncertain
    ],
    'mod_to_voice': [
        (['A', 'B', 'C', 'D', 'E', 'G', 'H'], 'a'),  # Active
        (['J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q'], 'p'),  # Passive
    ],
    'gen_to_gender': {
        '1': 'm',  # Masculine
        '2': 'f',  # Feminine
        '3': 'n',  # Neuter
    },
    'cas_to_case': [
        (['A', 'J'], 'n'),  # Nominative
        (['B', 'K'], 'g'),  # Genitive
        (['C', 'L'], 'd'),  # Dative
        (['D', 'M'], 'a'),  # Accusative
        (['E', 'N'], 'v'),  # Vocative
        (['F', 'O'], 'b'),  # Ablative
    ],
    'grnp_to_degree': {
        '1': 'p',  # Positive
        '2': 'c',  # Comparative
        '3': 's',  # Superlative
    },
}

# Mappings for PROIEL to Perseus XPOS conversions
# https://dev.syntacticus.org/development-guide/#part-of-speech-tags
# https://github.com/PerseusDL/treebank_data/blob/master/v2.1/Latin/TAGSET.txt
# https://itreebank.marginalia.it/doc/Tagset_Perseus.pdf
PROIEL_CONCORDANCES = {
    'number': {
        'Sing': 's',  # Singular
        'Plur': 'p',  # Plural
    },
    'tense': {
        'Pres': 'p',  # Present
        'Past': 'r',  # Perfect
        'Pqp': 'l',  # Pluperfect
        'Fut': 'f',  # Future
    },
    'mood': {
        'Ind': 'i',  # Indicative
        'Sub': 's',  # Subjunctive
        'Imp': 'm',  # Imperative
    },
    'voice': {
        'Act': 'a',  # Active
        'Pass': 'p',  # Passive
    },
    'gender': {
        'Fem': 'f',  # Feminine
        'Masc': 'm',  # Masculine
        'Neut': 'n',  # Neuter
    },
    'case': {
        'Abl': 'b',  # Ablative
        'Acc': 'a',  # Accusative
        'Dat': 'd',  # Dative
        'Gen': 'g',  # Genitive
        'Nom': 'n',  # Nominative
        'Voc': 'v',  # Vocative
    },
    'degree': {
        'Cmp': 'c',  # Comparative
        'Pos': 'p',  # Positive
        'Sup': 's',  # Superlative
    },
}

# Mappings for LLCT to Perseus XPOS conversions
# https://universaldependencies.org/treebanks/la_llct/index.html
LLCT_CONCORDANCES = {
    'number': {
        'Sing': 's',  # Singular
        'Plur': 'p',  # Plural
    },
    'tense': {
        'Pres': 'p',  # Present
        'Past': 'r',  # Perfect
        'Pqp': 'l',  # Pluperfect
        'Fut': 'f',  # Future
    },
    'mood': {
        'Ind': 'i',  # Indicative
        'Sub': 's',  # Subjunctive
        'Imp': 'm',  # Imperative
    },
    'voice': {
        'Act': 'a',  # Active
        'Pass': 'p',  # Passive
    },
    'gender': {
        'Fem': 'f',  # Feminine
        'Masc': 'm',  # Masculine
        'Neut': 'n',  # Neuter
    },
    'case': {
        'Abl': 'b',  # Ablative
        'Acc': 'a',  # Accusative
        'Dat': 'd',  # Dative
        'Gen': 'g',  # Genitive
        'Nom': 'n',  # Nominative
        'Voc': 'v',  # Vocative
        'Loc': 'l',  # Locative
    },
    'degree': {
        'Abs': 'x',  # Abs?
        'Cmp': 'c',  # Comparative
        'Dim': 'x',  # Dim?
    },
}

# Universal Latin Mappings
FEATS_TO_XPOS = {
    ('Person', '1'): (2, '1'),  # First person
    ('Person', '2'): (2, '2'),  # Second person
    ('Person', '3'): (2, '3'),  # Third person
    ('Number', 'Sing'): (3, 's'),  # Singular
    ('Number', 'Plur'): (3, 'p'),  # Plural
    ('Aspect', 'Imp'): (4, 'i'),  # Imperfect
    ('Aspect', 'Perf'): (4, 't'),  # Future Perfect
    ('Tense', 'Pres'): (4, 'p'),  # Present
    ('Tense', 'Past'): (4, 'r'),  # Perfect
    ('Tense', 'Pqp'): (4, 'l'),  # Pluperfect
    ('Tense', 'Fut'): (4, 'f'),  # Future
    ('VerbForm', 'Inf'): (5, 'n'),  # Infinitive
    ('VerbForm', 'Part'): (5, 'p'),  # Participle
    ('VerbForm', 'Ger'): (5, 'd'),  # Gerund
    ('VerbForm', 'Gdv'): (5, 'g'),  # Gerundive
    ('VerbForm', 'Sup'): (5, 'u'),  # Supine
    ('Mood', 'Ind'): (5, 'i'),  # Indicative
    ('Mood', 'Sub'): (5, 's'),  # Subjunctive
    ('Mood', 'Imp'): (5, 'm'),  # Imperative
    ('Voice', 'Act'): (6, 'a'),  # Active
    ('Voice', 'Pass'): (6, 'p'),  # Passive
    ('VerbType', 'Deponent'): (6, 'd'),  # Deponent
    ('Gender', 'Fem'): (7, 'f'),  # Feminine
    ('Gender', 'Masc'): (7, 'm'),  # Masculine
    ('Gender', 'Neut'): (7, 'n'),  # Neuter
    ('Case', 'Abl'): (8, 'b'),  # Ablative
    ('Case', 'Acc'): (8, 'a'),  # Accusative
    ('Case', 'Dat'): (8, 'd'),  # Dative
    ('Case', 'Gen'): (8, 'g'),  # Genitive
    ('Case', 'Nom'): (8, 'n'),  # Nominative
    ('Case', 'Voc'): (8, 'v'),  # Vocative
    ('Case', 'Loc'): (8, 'l'),  # Locative
    ('Case', 'Ins'): (8, 'i'),  # Instrumental
    ('Degree', 'Cmp'): (9, 'c'),  # Comparative
    ('Degree', 'Pos'): (9, 'p'),  # Positive
    ('Degree', 'Sup'): (9, 's'),  # Superlative
    ('Degree', 'Abs'): (9, 'a'),  # Absolute
}

XPOS_TO_FEATS = {v: k for k, v in FEATS_TO_XPOS.items()}
