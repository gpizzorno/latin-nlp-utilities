# Utils

[ADD INTRO]

## Morphology Normalization

Normalizes XPOS and FEATS together, with automatic format detection and validation.

### Quick Start

Normalizing morphological annotations:

```python
from conllu_tools.utils.normalization import normalize_morphology
from conllu_tools.io import load_language_data

# Load feature set for Latin
feature_set = load_language_data('feats', language='la')

# Normalize XPOS and FEATS together
xpos, feats = normalize_morphology(
    upos='VERB',
    xpos='v-s-ga-g-',
    feats='Aspect=Perf|Case=Gen|Degree=Pos|Number=Sing|Voice=Act',
    feature_set=feature_set,
    ref_features='VerbForm=Ger'  # Missing feature added from reference
)

print(xpos)
# Output: 'v-stga-g-'

print(feats)
# Output: {'Aspect': 'Perf', 'Case': 'Gen', 'Degree': 'Pos', 'Number': 'Sing', 'VerbForm': 'Ger', 'Voice': 'Act'}
```

### Basic Usage

```python
from conllu_tools.utils.normalization import normalize_morphology
from conllu_tools.io import load_language_data

feature_set = load_language_data('feats', language='la')

# Basic normalization
xpos, feats = normalize_morphology(
    upos='NOUN',
    xpos='n-s---mn-',
    feats='Case=Nom|Gender=Masc|Number=Sing',
    feature_set=feature_set
)

print(xpos)  # 'n-s---mn-' (validated)
print(feats)  # {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}
```

### With Reference Features

Use `ref_features` to fill in missing features from a reference source:

```python
# Features are incomplete - missing NumForm
xpos, feats = normalize_morphology(
    upos='NUM',
    xpos='m-p---fa-',
    feats='Case=Acc|Gender=Fem|Number=Plur',
    feature_set=feature_set,
    ref_features='NumForm=Word'  # Will be added
)

print(feats)
# Output: {'Case': 'Acc', 'Gender': 'Fem', 'NumForm': 'Word', 'Number': 'Plur'}
```

### What Gets Normalized

The normalizer performs these operations:

1. **Formats XPOS**: Auto-detects and converts LLCT, ITTB, PROIEL formats to Perseus
2. **Validates XPOS**: Checks each position against UPOS-specific validity rules
3. **Reconciles features**: Merges feats with ref_features (feats take precedence)
4. **Validates features**: Filters out features invalid for the given UPOS
5. **Generates XPOS from features**: Creates XPOS positions from validated features
6. **Reconciles XPOS**: Merges provided and generated XPOS (provided takes precedence)
7. **Returns tuple**: (normalized_xpos, validated_features)


## UPOS Utilities

Convert language-specific POS tags to Universal POS tags.

### DALME to UPOS

Convert DALME project tags to Universal POS:

```python
from conllu_tools.utils.upos import dalme_to_upos

dalme_tag = 'coordinating conjunction'
upos_tag = dalme_to_upos(dalme_tag)
print(upos_tag)  # 'CCONJ'
```

### UPOS to Perseus

Convert a UPOS tag to a Perseus XPOS tag:

```python
from conllu_tools.utils.upos import upos_to_perseus

upos = "NOUN"
perseus_tag = upos_to_perseus(upos)
print(perseus_tag)  # 'n'
```

## Feature Utilities


### Convert Features to XPOS

The `features_to_xpos` function creates Perseus XPOS positions from feature dictionaries:

```python
from conllu_tools.utils.features import features_to_xpos

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



### Convert XPOS to Features


[ADD CONTENT]


### Validate Features

Filter features to ensure they are valid for a given UPOS:

```python
from conllu_tools.utils.features import validate_features
from conllu_tools.io import load_language_data

# Load feature set
feature_set = load_language_data('feats', language='la')

# Validate features - invalid ones will be filtered out
validated = validate_features(
    upos='NOUN',
    feats='Case=Nom|Gender=Fem|Number=Sing|Mood=Ind',  # Mood invalid for NOUN
    feature_set=feature_set
)

print(validated)
# Output: {'Case': 'Nom', 'Gender': 'Fem', 'Number': 'Sing'}
# Note: Mood=Ind removed (not valid for NOUN)

# Works with dictionaries too
validated = validate_features(
    upos='VERB',
    feats={'Mood': 'Ind', 'Case': 'Nom', 'Tense': 'Pres'},  # Case invalid for most verbs
    feature_set=feature_set
)

print(validated)
# Output: {'Mood': 'Ind', 'Tense': 'Pres'}
# Note: Case=Nom removed (typically invalid for finite verbs)
```

**What it does:**
- Checks if each feature is valid for the given UPOS
- Removes features marked as invalid (0) in the feature set
- Removes unknown features not in the feature set
- Normalizes feature names (case-insensitive matching)
- Returns only valid features as a dictionary

**Use cases:**
- Pre-validation before file-level validation
- Checking which features are compatible with a UPOS
- Cleaning annotations during conversion
- Component of `normalize_morphology` function

## XPOS Utilities

### Format XPOS

Auto-detect and convert XPOS formats to Perseus standard.

The `format_xpos` function automatically detects the input XPOS format and converts it to Perseus:

```python
from conllu_tools.utils.xpos import format_xpos

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


### Validate XPOS

Ensure XPOS positions are valid for the given UPOS:

```python
from conllu_tools.utils.xpos import validate_xpos

# Correct UPOS mismatch in first position
validated = validate_xpos(upos='NOUN', xpos='a-s---fn-')
print(validated)
# Output: 'n-s---fn-' (first character corrected from 'a' to 'n')

# Remove invalid positions for UPOS
validated = validate_xpos(upos='NOUN', xpos='n1s---mn-')
print(validated)
# Output: 'n-s---mn-' (position 2 cleared - only valid for verbs)

# Validate verb XPOS
validated = validate_xpos(upos='VERB', xpos='v3spia---')
print(validated)
# Output: 'v3spia---' (all positions valid for verbs)

# Handle short or malformed XPOS
validated = validate_xpos(upos='ADJ', xpos='A')
print(validated)
# Output: 'a--------' (padded to 9 characters)
```

**Position validity rules (Perseus format):**
- **Position 1**: Must match UPOS (n=NOUN, v=VERB, a=ADJ, p=PRON, m=NUM, etc.)
- **Position 2**: Only valid for 'v' (verbs)
- **Position 3**: Valid for n, v, a, p, m (nouns, verbs, adjectives, pronouns, numerals)
- **Positions 4-6**: Only valid for 'v' (verbs)
- **Positions 7-8**: Valid for n, v, a, p, m
- **Position 9**: Only valid for 'a' (adjectives)

**What it does:**
- Ensures first character matches UPOS Perseus code
- Validates each position against UPOS-specific rules
- Replaces invalid positions with '-'
- Pads or truncates to exactly 9 characters
- Returns validated Perseus-format XPOS string

**Use cases:**
- Correcting UPOS/XPOS mismatches
- Validating positional tag structure
- Cleaning imported tags
- Component of `normalize_morphology` function


### Low-level Conversion Tools

The XPOS converters normalize language-specific POS tags from different treebanks to a
common Perseus-style format.

These are used by the higher level functions described above.

**Supported Treebanks**

- **PROIEL**: e.g., `Pp`
- **ITTB**: e.g., `J3|modJ|tem3|gen6`
- **LLCT**: e.g., `v|v|1|s|r|i|a|-|-|-`
- **Perseus**: Target format (e.g., `v3spia---`)


**ITTB to Perseus**

The ITTB converter takes UPOS and XPOS:

```python
from conllu_tools.utils.xpos import ittb_to_perseus

print(ittb_to_perseus('ADJ', 'gen2|casB|grp3'))
# Returns 'a-s---fgs'

print(ittb_to_perseus('ADJ', 'gen1|casA|grn2'))
# Returns 'a-s---mnc'

print(ittb_to_perseus('NOUN', 'gen1|casA'))
# Returns 'n-s---mn-'
```

**PROIEL to Perseus**

The PROIEL converter takes UPOS and FEATS:

```python
from conllu_tools.utils.xpos import proiel_to_perseus

print(proiel_to_perseus('NOUN', 'Case=Nom|Gender=Masc|Number=Sing'))
# Returns 'n-s---mn-'

print(proiel_to_perseus('VERB', 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Pass'))
# Returns 'v3spip---'

print(proiel_to_perseus('PRON', 'Case=Dat|Number=Sing|Person=1'))
# Returns 'p1s----d-'
```

**LLCT to Perseus**

LLCT uses a pipe-separated format that combines UPOS, XPOS, and FEATS information. The converter needs all three columns to generate standard XPOS:

```python
from conllu_tools.utils.xpos import llct_to_perseus

# LLCT format: requires UPOS, XPOS (10-part pipe-separated), and FEATS
upos = 'VERB'
xpos = 'v|v|3|s|p|i|a|-|-|-'  # POS|POS_repeat|person|number|tense|mood|voice|gender|case|degree
feats = 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act'

new_xpos = llct_to_perseus(upos, xpos, feats)
print(new_xpos)  # "v3spia---"
```
