# Normalization

This guide covers normalizing and standardizing morphological annotations.

## Overview

Normalization utilities ensure consistency in annotation format:

- **Morphology normalization**: Comprehensive normalization of XPOS and FEATS together
- **Format detection**: Automatically detect and convert different XPOS formats
- **Validation**: Filter invalid features and XPOS positions
- **Reconciliation**: Merge provided and reference features/XPOS

These tools are useful for:

- Cleaning imported or converted annotations
- Ensuring Universal Dependencies compliance
- Preparing data for validation and evaluation
- Standardizing annotations across annotators and treebanks

## Quick Start

Normalizing morphological annotations:

```python
from nlp_utilities.normalizers import normalize_morphology
from nlp_utilities.loaders import load_language_data

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

## Morphology Normalization

The primary normalization function handles XPOS and FEATS together, with automatic format detection and validation.

### Basic Usage

```python
from nlp_utilities.normalizers import normalize_morphology
from nlp_utilities.loaders import load_language_data

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

### Examples

**Example 1: VERB with gerund features**

```python
xpos, feats = normalize_morphology(
    upos='VERB',
    xpos='v-s-ga-g-',
    feats='Aspect=Perf|Case=Gen|Degree=Pos|Number=Sing|Voice=Act',
    feature_set=feature_set,
    ref_features='Aspect=Perf|Case=Gen|Degree=Pos|Number=Sing|VerbForm=Ger|Voice=Act'
)

print(xpos)
# Output: 'v-stga-g-' (position 3 filled from features)

print(feats)
# Output: {'Aspect': 'Perf', 'Case': 'Gen', 'Degree': 'Pos', 'Number': 'Sing', 'VerbForm': 'Ger', 'Voice': 'Act'}
```

**Example 2: AUX with finite verb features**

```python
xpos, feats = normalize_morphology(
    upos='AUX',
    xpos='v2spia---',
    feats='Mood=Ind|Number=Sing|Person=2|Tense=Pres|VerbForm=Fin|Voice=Act',
    feature_set=feature_set
)

print(xpos)
# Output: 'v2spia---' (all positions validated)

print(feats)
# Output: {'Mood': 'Ind', 'Number': 'Sing', 'Person': 2', 'Tense': 'Pres', 'VerbForm': 'Fin', 'Voice': 'Act'}
```

**Example 3: ADJ with degree reconciliation**

```python
xpos, feats = normalize_morphology(
    upos='ADJ',
    xpos='a-s---nbp',
    feats='Case=Abl|Degree=Pos|Gender=Neut|Number=Sing',
    feature_set=feature_set,
    ref_features='Case=Abl|Gender=Masc|Number=Sing'  # Gender conflicts - feats wins
)

print(xpos)
# Output: 'a-s---nbp' (validated)

print(feats)
# Output: {'Case': 'Abl', 'Degree': 'Pos', 'Gender': 'Neut', 'Number': 'Sing'}
# Note: Gender=Neut from feats takes precedence over Gender=Masc from ref_features
```

**Example 4: NOUN with XPOS/UPOS mismatch correction**

```python
# XPOS suggests VERB, but UPOS is NOUN
xpos, feats = normalize_morphology(
    upos='NOUN',
    xpos='v2spma---',  # Wrong UPOS character
    feats='Mood=Imp|Number=Sing|Person=2|Tense=Pres|VerbForm=Fin|Voice=Act',
    feature_set=feature_set
)

print(xpos)
# Output: 'n-s------' (corrected to NOUN format, invalid features removed)

print(feats)
# Output: {'Number': 'Sing'} (only Number is valid for NOUN)
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

## Component Functions

While `normalize_morphology` is recommended for most use cases, you can also use its component functions independently.

### `validate_features`

Filter features to only those valid for a given UPOS:

```python
from nlp_utilities.validators import validate_features
from nlp_utilities.loaders import load_language_data

feature_set = load_language_data('feats', language='la')

# Mood is invalid for NOUN - will be filtered out
validated = validate_features(
    upos='NOUN',
    feats={'Case': 'Nom', 'Gender': 'Fem', 'Number': 'Sing', 'Mood': 'Ind'},
    feature_set=feature_set
)

print(validated)
# Output: {'Case': 'Nom', 'Gender': 'Fem', 'Number': 'Sing'}

# Works with strings too
validated = validate_features(
    upos='NOUN',
    feats='Case=Nom|Gender=Fem|Number=Sing|Mood=Ind',
    feature_set=feature_set
)

print(validated)
# Output: {'Case': 'Nom', 'Gender': 'Fem', 'Number': 'Sing'}
```

**Use cases:**
- Validating features before file-level validation
- Checking which features are valid for a UPOS
- Cleaning imported annotations

### `validate_xpos`

Ensure XPOS positions are valid for the given UPOS:

```python
from nlp_utilities.validators import validate_xpos

# First character wrong for NOUN
validated = validate_xpos(upos='NOUN', xpos='a-s---fn-')
print(validated)
# Output: 'n-s---fn-' (first character corrected)

# Position 2 only valid for verbs
validated = validate_xpos(upos='NOUN', xpos='n1s---mn-')
print(validated)
# Output: 'n-s---mn-' (position 2 cleared)

# Verb with valid positions
validated = validate_xpos(upos='VERB', xpos='v3spia---')
print(validated)
# Output: 'v3spia---' (all positions valid)
```

**Position validity rules (Perseus format):**
- Position 1: UPOS-dependent (n, v, a, p, m, d, c, r, l, e, i, u, g, -)
- Position 2: Only valid for 'v' (verbs)
- Position 3: Valid for n, v, a, p, m
- Position 4-6: Only valid for 'v' (verbs)
- Position 7-8: Valid for n, v, a, p, m
- Position 9: Only valid for 'a' (adjectives)

**Use cases:**
- Correcting UPOS/XPOS mismatches
- Validating positional tags
- Cleaning converted annotations

### `format_xpos`

Auto-detect and convert XPOS formats to Perseus:

```python
from nlp_utilities.converters.xpos import format_xpos

# LLCT format (pipe-separated)
xpos = format_xpos(
    upos='VERB',
    xpos='v|v|3|s|p|i|a|-|-|-',
    feats='Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act'
)
print(xpos)  # 'v3spia---'

# ITTB format
xpos = format_xpos(
    upos='VERB',
    xpos='gen4|tem1|mod1',
    feats='Mood=Ind|Tense=Pres|Voice=Pass'
)
print(xpos)  # 'v--pi----'

# PROIEL format (uses FEATS, XPOS is minimal)
xpos = format_xpos(
    upos='NOUN',
    xpos='Nb',
    feats='Case=Acc|Gender=Neut|Number=Sing'
)
print(xpos)  # 'n-s---na-'

# Already Perseus - just ensures UPOS matches
xpos = format_xpos(
    upos='NOUN',
    xpos='a-s---fn-',  # Wrong UPOS char
    feats='Case=Nom|Gender=Fem|Number=Sing'
)
print(xpos)  # 'n-s---fn-' (UPOS char corrected)
```

**Use cases:**
- Converting between treebank formats
- Harmonizing cross-treebank annotations
- Auto-detecting format in mixed data

### `features_to_xpos`

Generate Perseus XPOS from feature dictionary:

```python
from nlp_utilities.converters.features import features_to_xpos

# Generate XPOS from features
xpos = features_to_xpos('Case=Nom|Gender=Masc|Number=Sing')
print(xpos)  # '-----mn-'  (positions 7,8 filled)

xpos = features_to_xpos('Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act')
print(xpos)  # '-3spia---'  (verb positions filled)

# Works with dictionaries too
xpos = features_to_xpos({'Case': 'Acc', 'Gender': 'Fem', 'Number': 'Plur'})
print(xpos)  # '-p---fa-'
```

**Use cases:**
- Generating XPOS when only FEATS are available
- Filling missing XPOS positions
- Creating initial XPOS tags from morphological features

## Feature Set Loading

Load language-specific feature sets for validation.

### Basic Loading

```python
from nlp_utilities.loaders import load_language_data

# Load Latin feature set
feature_set = load_language_data('feats', language='la')

# Use with normalize_features
from nlp_utilities.normalizers import normalize_features

normalized = normalize_features('NOUN', 'Case=Nom|Gender=Masc', feature_set)
```

### Understanding the Feature Set Format

Each feature in the set has a `byupos` dictionary that maps UPOS tags to valid values:

- **Value `1`**: Valid for this UPOS
- **Value `0`**: Invalid/not allowed for this UPOS
- **Missing UPOS**: Feature not applicable to this UPOS

JSON representation:

```json
{
    "Case": {
            "byupos": {
            "NOUN": {"Nom": 1, "Gen": 1, "Dat": 1, "Acc": 1, "Voc": 1, "Abl": 1},
            "ADJ": {"Nom": 1, "Gen": 1, "Dat": 1, "Acc": 1, "Voc": 1, "Abl": 1},
            "VERB": {"Nom": 0, "Gen": 0}
        }
    },
    "Gender": {
        "byupos": {
            "NOUN": {"Masc": 1, "Fem": 1, "Neut": 1},
            "ADJ": {"Masc": 1, "Fem": 1, "Neut": 1}
        }
    }
}
```

Working with feature sets as Python dictionaries:

```python
# Example: Case feature
feature_set['Case']['byupos']['NOUN']
# {'Nom': 1, 'Gen': 1, 'Dat': 1, 'Acc': 1, 'Voc': 1, 'Abl': 1, 'Loc': 1}

# Case not valid for verbs in most contexts
feature_set['Case']['byupos']['VERB']
# {'Nom': 0, 'Gen': 0, ...}  # All marked as invalid

# VerbForm only valid for verbs
feature_set['VerbForm']['byupos']['VERB']
# {'Fin': 1, 'Inf': 1, 'Part': 1, 'Ger': 1, 'Gdv': 1, 'Sup': 1}

feature_set['VerbForm']['byupos'].get('NOUN')
# None or not present - VerbForm doesn't apply to nouns
```

### Custom Feature Sets

Define your own feature set for specialized treebanks or annotation schemes:

```python
# Define a custom feature set
custom_feature_set = {
    'Case': {
        'byupos': {
            'NOUN': {'Nom': 1, 'Gen': 1, 'Acc': 1},  # Only 3 cases
            'ADJ': {'Nom': 1, 'Gen': 1, 'Acc': 1},
        }
    },
    'Gender': {
        'byupos': {
            'NOUN': {'Masc': 1, 'Fem': 1},  # No neuter
            'ADJ': {'Masc': 1, 'Fem': 1},
        }
    },
    'Number': {
        'byupos': {
            'NOUN': {'Sing': 1, 'Plur': 1},
            'ADJ': {'Sing': 1, 'Plur': 1},
            'VERB': {'Sing': 1, 'Plur': 1},
        }
    },
}

# Use custom feature set
from nlp_utilities.normalizers import normalize_features

# This will remove Dat case (not in custom set)
normalized = normalize_features(
    'NOUN',
    'Case=Nom|Case=Dat|Gender=Masc',
    custom_feature_set
)
print(normalized)
# Output: {'Case': 'Nom', 'Gender': 'Masc'}
```

### Loading Other Language Data

```python
from nlp_utilities.loaders import load_language_data

# Load dependency relations
deprels = load_language_data('deprels', language='la')

# Load auxiliary verbs list
auxiliaries = load_language_data('auxiliaries', language='la')

# Load whitespace exceptions
whitespace_exceptions = load_whitespace_exceptions(language='la')
```

## Normalization Workflows

### Normalizing a CoNLL-U File

Process an entire CoNLL-U file to normalize all morphological annotations:

```python
from nlp_utilities.normalizers import normalize_morphology
from nlp_utilities.loaders import load_language_data
from nlp_utilities.converters.features import feature_dict_to_string

# Load feature set
feature_set = load_language_data('feats', language='la')

# Load CoNLL-U file (assuming you have a load function)
sentences = load_conllu('input.conllu')

# Normalize all annotations
for sentence in sentences:
    for token in sentence:
        # Skip multiword tokens and empty nodes
        if '-' in str(token['id']) or '.' in str(token['id']):
            continue
        
        # Normalize morphology
        if token['upos'] != '_' and token['xpos'] != '_':
            xpos, feats = normalize_morphology(
                upos=token['upos'],
                xpos=token['xpos'],
                feats=token['feats'] if token['feats'] != '_' else {},
                feature_set=feature_set
            )
            
            # Update token
            token['xpos'] = xpos
            token['feats'] = feature_dict_to_string(feats) if feats else '_'

```

### Cleaning Imported Annotations

Normalize annotations from external sources with ref_features:

```python
from nlp_utilities.normalizers import normalize_morphology
from nlp_utilities.loaders import load_language_data
from nlp_utilities.converters.features import feature_dict_to_string

feature_set = load_language_data('feats', language='la')

def clean_annotation(token, feature_set, ref_token=None):
    """Clean a single token's annotation."""
    if token['upos'] == '_':
        return token
    
    try:
        # Get reference features if available
        ref_features = None
        if ref_token and ref_token['feats'] != '_':
            ref_features = ref_token['feats']
        
        # Normalize
        xpos, feats = normalize_morphology(
            upos=token['upos'],
            xpos=token['xpos'] if token['xpos'] != '_' else f"{token['upos'][0].lower()}--------",
            feats=token['feats'] if token['feats'] != '_' else {},
            feature_set=feature_set,
            ref_features=ref_features
        )
        
        token['xpos'] = xpos
        token['feats'] = feature_dict_to_string(feats) if feats else '_'
        
    except Exception as e:
        print(f"Warning: Could not normalize token {token['form']}: {e}")
        token['xpos'] = f"{token['upos'][0].lower()}--------"
        token['feats'] = '_'
    
    return token

# Apply to all tokens with reference
for sentence, ref_sentence in zip(imported_sentences, reference_sentences):
    for token, ref_token in zip(sentence, ref_sentence):
        if isinstance(token['id'], int):
            clean_annotation(token, feature_set, ref_token)
```

### Validating After Normalization

Always validate after normalizing to ensure correctness:

```python
from nlp_utilities.normalizers import normalize_morphology
from nlp_utilities.conllu import ConlluValidator
from nlp_utilities.loaders import load_language_data

# Normalize
feature_set = load_language_data('feats', language='la')
# ... normalization code ...

# Validate
validator = ConlluValidator(lang='la', level=2)
reporter = validator.validate_file('output_normalized.conllu')

if reporter.get_error_count() > 0:
    print(f"Found {reporter.get_error_count()} errors after normalization")
    for error in reporter.format_errors():
        print(error)
else:
    print("All annotations normalized successfully!")
```

### Batch Normalization

Normalize multiple files in batch:

```python
from pathlib import Path
from nlp_utilities.normalizers import normalize_morphology
from nlp_utilities.loaders import load_language_data
from nlp_utilities.converters.features import feature_dict_to_string

def normalize_directory(input_dir, output_dir):
    """Normalize all CoNLL-U files in a directory."""
    feature_set = load_language_data('feats', language='la')
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for conllu_file in input_path.glob('*.conllu'):
        print(f"Processing {conllu_file.name}...")
        sentences = load_conllu(str(conllu_file))
        
        # Normalize each sentence
        for sentence in sentences:
            for token in sentence:
                if isinstance(token['id'], int) and token['upos'] != '_':
                    try:
                        xpos, feats = normalize_morphology(
                            upos=token['upos'],
                            xpos=token['xpos'] if token['xpos'] != '_' else f"{token['upos'][0].lower()}--------",
                            feats=token['feats'] if token['feats'] != '_' else {},
                            feature_set=feature_set
                        )
                        token['xpos'] = xpos
                        token['feats'] = feature_dict_to_string(feats) if feats else '_'
                    except Exception as e:
                        print(f"  Error in {token['form']}: {e}")
        
        # Save normalized file
        output_file = output_path / conllu_file.name
        save_conllu(sentences, str(output_file))
        print(f"Saved to {output_file}")

# Process all files
normalize_directory('raw_annotations/', 'normalized_annotations/')
```

## Error Handling

### Handling Normalization Errors

```python
from nlp_utilities.normalizers import normalize_morphology
from nlp_utilities.validators import validate_features, validate_xpos

# Validation errors
try:
    result = validate_xpos(None, 'n-s---mn-')
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: UPOS must be provided to validate XPOS

try:
    result = validate_features(None, 'Case=Nom', feature_set)
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: UPOS and feature set must be provided to validate FEATS

# Format detection errors
try:
    xpos, feats = normalize_morphology('NOUN', None, {}, feature_set)
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: Both UPOS and FEATS must be provided to format XPOS
```

### Safe Normalization with Fallbacks

```python
from nlp_utilities.normalizers import normalize_morphology
from nlp_utilities.converters.features import feature_dict_to_string

def safe_normalize_morphology(upos, xpos, feats, feature_set, ref_features=None):
    """Normalize morphology with fallback."""
    try:
        return normalize_morphology(upos, xpos, feats, feature_set, ref_features)
    except Exception as e:
        print(f"Warning: Could not normalize for UPOS '{upos}': {e}")
        # Return safe defaults
        default_xpos = f"{upos[0].lower()}--------" if upos else '---------'
        return default_xpos, {}

# Use safe version in production
for token in sentence:
    if token['upos'] != '_':
        xpos, feats = safe_normalize_morphology(
            token['upos'],
            token['xpos'],
            token['feats'],
            feature_set
        )
        token['xpos'] = xpos
        token['feats'] = feature_dict_to_string(feats) if feats else '_'
```

## See Also

- [Validation](validation.md) - Validating normalized files
- [Converters](converters.md) - Converting between formats
- {ref}`api_reference` - Detailed normalizer API

