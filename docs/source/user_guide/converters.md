# Converters

This guide covers converting between different tagsets and annotation schemes for Latin treebanks.

## Overview

The converters module provides utilities for standardizing annotations from various Latin treebanks
to a common format. This includes:

- **UPOS conversion**: Language-specific POS tags → Universal POS tags
- **Feature conversion**: Various morphological annotation schemes → Universal Features
- **XPOS conversion**: Normalizing language-specific POS tags across treebanks

These converters are useful for:

- Harmonizing annotations across different Latin treebanks
- Creating cross-treebank training datasets
- Adapting legacy annotations to Universal Dependencies standards

## Quick Start

Converting from PROIEL UPOS AND FEATS to Perseus XPOS:

```python
from nlp_utilities.converters.xpos import proiel_to_perseus

proiel_upos = 'NOUN'
proiel_feats = 'Case=Acc|Gender=Neut|Number=Sing'
new_xpos = proiel_to_perseus(proiel_upos, proiel_feats) # PROIEL XPOS = 'Nb'
print(new_xpos)  # "n-s---na-"
```

Converting from ITTB UPOS and XPOS to Perseus XPOS:

```python
from nlp_utilities.converters.xpos import ittb_to_perseus

ittb_upos = 'ADJ'
ittb_xpos = 'C1|grn1|casB|gen1'
new_xpos = ittb_to_perseus(ittb_upos, ittb_xpos)
print(new_xpos)  # "a-s---mgp"
```

## XPOS Converters

The XPOS converters normalize language-specific POS tags from different treebanks to a
common Perseus-style format.

### Supported Treebanks

- **PROIEL**: e.g., `Pp`
- **ITTB**: e.g., `J3|modJ|tem3|gen6`
- **LLCT**: e.g., `v|v|1|s|r|i|a|-|-|-`
- **Perseus**: Target format (e.g., `v3spia---`)

### PROIEL to Perseus

The PROIEL converter takes UPOS and FEATS:

```python
from nlp_utilities.converters.xpos import proiel_to_perseus

print(proiel_to_perseus('NOUN', 'Case=Nom|Gender=Masc|Number=Sing'))
# Returns 'n-s---mn-'

print(proiel_to_perseus('VERB', 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Pass'))
# Returns 'v3spip---'

print(proiel_to_perseus('PRON', 'Case=Dat|Number=Sing|Person=1'))
# Returns 'p1s----d-'
```

### ITTB to Perseus

The ITTB converter takes UPOS and XPOS:

```python
from nlp_utilities.converters.xpos import ittb_to_perseus

print(ittb_to_perseus('ADJ', 'gen2|casB|grp3'))
# Returns 'a-s---fgs'

print(ittb_to_perseus('ADJ', 'gen1|casA|grn2'))
# Returns 'a-s---mnc'

print(ittb_to_perseus('NOUN', 'gen1|casA'))
# Returns 'n-s---mn-'
```

### LLCT to Perseus

LLCT uses a pipe-separated format that combines UPOS, XPOS, and FEATS information. The converter needs all three columns to generate standard XPOS:

```python
from nlp_utilities.converters.xpos import llct_to_perseus

# LLCT format: requires UPOS, XPOS (10-part pipe-separated), and FEATS
upos = 'VERB'
xpos = 'v|v|3|s|p|i|a|-|-|-'  # POS|POS_repeat|person|number|tense|mood|voice|gender|case|degree
feats = 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act'

new_xpos = llct_to_perseus(upos, xpos, feats)
print(new_xpos)  # "v3spia---"
```

## UPOS Converters

Convert language-specific POS tags to Universal POS tags.

### DALME to UPOS

Convert DALME project tags to Universal POS:

```python
from nlp_utilities.converters.upos import dalme_to_upos

dalme_tag = 'coordinating conjunction'
upos_tag = dalme_to_upos(dalme_tag)
print(upos_tag)  # 'CCONJ'
```

### UPOS to Perseus

Convert a UPOS tag to a Perseus XPOS tag:

```python
from nlp_utilities.converters.upos import upos_to_perseus

upos = "NOUN"
perseus_tag = upos_to_perseus(upos)
print(perseus_tag)  # 'n'
```

## Feature Converters

Convert morphological feature representations between formats.

### Feature Dictionary ↔ String

Convert between dictionary and CoNLL-U string format:

```python
from nlp_utilities.converters.features import feature_dict_to_string, feature_string_to_dict

# Dict to string
features = {
    'Case': 'Nom',
    'Gender': 'Masc',
    'Number': 'Sing'
}
feat_string = feature_dict_to_string(features)
print(feat_string)  # 'Case=Nom|Gender=Masc|Number=Sing'

# String to dict
feat_string = 'Case=Gen|Number=Plur'
features = feature_string_to_dict(feat_string)
print(features)  # {'Case': 'Gen', 'Number': 'Plur'}
```

**Automatic sorting**: Output is alphabetically sorted by feature name.

## Format Conversion

Auto-detect and convert XPOS formats to Perseus standard.

### `format_xpos`

The `format_xpos` function automatically detects the input XPOS format and converts it to Perseus:

```python
from nlp_utilities.converters.xpos import format_xpos

# LLCT format (pipe-separated, 10 parts)
xpos = format_xpos(
    upos='VERB',
    xpos='v|v|3|s|p|i|a|-|-|-',
    feats='Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act'
)
print(xpos)  # 'v3spia---'

# ITTB format (pipe-separated features like 'gen4|tem1|mod1')
xpos = format_xpos(
    upos='VERB',
    xpos='gen4|tem1|mod1',
    feats='Mood=Ind|Tense=Pres|Voice=Pass'
)
print(xpos)  # 'v--pip---'

# PROIEL format (minimal codes, relies on FEATS)
xpos = format_xpos(
    upos='NOUN',
    xpos='Nb',
    feats='Case=Acc|Gender=Neut|Number=Sing'
)
print(xpos)  # 'n-s---na-'

# Perseus format (already correct, just validates UPOS)
xpos = format_xpos(
    upos='NOUN',
    xpos='a-s---fn-',  # Wrong first character
    feats='Case=Nom|Gender=Fem|Number=Sing'
)
print(xpos)  # 'n-s---fn-' (UPOS character corrected)

# Unknown/None - generates default
xpos = format_xpos(
    upos='ADJ',
    xpos=None,
    feats='Case=Nom|Gender=Masc|Number=Sing'
)
print(xpos)  # 'a--------' (default for ADJ)
```

**Format Detection:**

The function uses regex patterns to detect input format:

- **PERSEUS_XPOS_MATCHER**: `[nvapmdcrileugt-]{9}` - 9-character Perseus format
- **LLCT_XPOS_MATCHER**: Pipe-separated 10-part format
- **ITTB_XPOS_MATCHER**: Pipe-separated with feature codes (e.g., `gen4|tem1`)
- **PROIEL_XPOS_MATCHER**: Single or double character codes

**Use cases:**

- Harmonizing annotations from different treebanks
- Converting legacy annotations to standard format
- Processing mixed-format corpora
- Component of `normalize_morphology` function

**Example: Processing Mixed Formats**

```python
from nlp_utilities.converters.xpos import format_xpos

# Process tokens from different source treebanks
tokens = [
    {'upos': 'VERB', 'xpos': 'v|v|3|s|p|i|a|-|-|-', 'feats': 'Mood=Ind|...', 'source': 'LLCT'},
    {'upos': 'NOUN', 'xpos': 'gen2|casA', 'feats': 'Case=Nom|...', 'source': 'ITTB'},
    {'upos': 'ADJ', 'xpos': 'Nb', 'feats': 'Case=Acc|...', 'source': 'PROIEL'},
]

for token in tokens:
    token['xpos_normalized'] = format_xpos(
        token['upos'],
        token['xpos'],
        token['feats']
    )
    print(f"{token['source']}: {token['xpos']} → {token['xpos_normalized']}")

# Output:
# LLCT: v|v|3|s|p|i|a|-|-|- → v3spia---
# ITTB: gen2|casA → n-s---fn-
# PROIEL: Nb → n-s---na-
```

## Feature-to-XPOS Conversion

Generate Perseus XPOS tags from morphological features.

### `features_to_xpos`

The `features_to_xpos` function creates Perseus XPOS positions from feature dictionaries:

```python
from nlp_utilities.converters.features import features_to_xpos

# Generate XPOS from features
xpos = features_to_xpos('Case=Nom|Gender=Masc|Number=Sing')
print(xpos)  # '-----mn-' (positions 7,8 filled)

xpos = features_to_xpos('Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act')
print(xpos)  # '-3spia---' (verb positions filled)

# Works with dictionaries too
xpos = features_to_xpos({'Case': 'Acc', 'Gender': 'Fem', 'Number': 'Plur'})
print(xpos)  # '-p---fa-' (positions 3,7,8 filled)

xpos = features_to_xpos({'Degree': 'Sup'})
print(xpos)  # '--------s' (position 9 filled - superlative adjective)
```

**Feature-to-Position Mapping:**

The function uses the `FEATS_TO_XPOS` mapping constant:

```python
# Example mappings (feature, value) → (position, character)
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
```

**Use cases:**

- Generating XPOS when only morphological features are available
- Filling missing XPOS positions from features
- Creating initial tags for new annotations
- Component of `normalize_morphology` function

**Example: Complete Workflow**

```python
from nlp_utilities.converters.features import features_to_xpos, feature_string_to_dict
from nlp_utilities.validators import validate_xpos

# Start with features only
feats_str = 'Case=Gen|Gender=Fem|Number=Plur'
feats_dict = feature_string_to_dict(feats_str)

# Generate XPOS from features
xpos = features_to_xpos(feats_dict)
print(f"Generated XPOS: {xpos}")  # '-p---fg-'

# Validate for specific UPOS
validated_xpos = validate_xpos('NOUN', xpos)
print(f"Validated XPOS: {validated_xpos}")  # 'n-p---fg-'
```

**Example: Filling Partial XPOS**

```python
from nlp_utilities.converters.features import features_to_xpos

# You have partial XPOS and want to fill gaps from features
provided_xpos = 'v--pi----'  # Tense and Mood known
features = 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act'

# Generate from features
xpos_from_feats = features_to_xpos(features)
print(xpos_from_feats)  # '-3spia---'

# Reconcile: provided positions take precedence, fill gaps
final_xpos = list(provided_xpos)
for i, char in enumerate(xpos_from_feats):
    if final_xpos[i] == '-' and char != '-':
        final_xpos[i] = char

print(''.join(final_xpos))  # 'v3spia---' (combined)
```

## See Also

- [Normalization](normalization.md) - How format_xpos and features_to_xpos integrate with normalize_morphology
- [Validation](validation.md) - Validating converted files
- {ref}`api_reference` - Detailed converter API
