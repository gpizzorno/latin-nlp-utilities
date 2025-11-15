# Normalization

This guide covers normalizing and standardizing linguistic annotations.

## Overview

Normalization utilities ensure consistency in annotation format:

- **Feature normalization**: Fix capitalization, sort alphabetically, validate format
- **XPOS normalization**: Standardize language-specific POS tags

These tools are useful for:

- Cleaning imported or converted annotations
- Ensuring Universal Dependencies compliance
- Preparing data for validation and evaluation
- Standardizing annotations across annotators

## Quick Start

Normalizing morphological features:

```python
from nlp_utilities.normalizers import normalize_features
from nlp_utilities.loaders import load_language_data

# Load feature set for Latin
feature_set = load_language_data('feats', language='la')

# Normalize features (removes invalid features for the UPOS)
normalized = normalize_features(
    'NOUN',
    'Case=Nom|Gender=Masc|Number=Sing|Mood=Ind',  # Mood is invalid for NOUN
    feature_set
)
print(normalized)
# Output: {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}
```

## Feature Normalization

The feature normalizer ensures morphological features meet CoNLL-U specifications and are valid for the given UPOS tag.

### Basic Usage

```python
from nlp_utilities.normalizers import normalize_features
from nlp_utilities.loaders import load_language_data

# Load feature set
feature_set = load_language_data('feats', language='la')

# Normalize with dictionary input
features = {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}
normalized = normalize_features('NOUN', features, feature_set)
print(normalized)
# Output: {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}

# Normalize with string input (CoNLL-U format)
features = 'Case=Nom|Gender=Masc|Number=Sing'
normalized = normalize_features('NOUN', features, feature_set)
print(normalized)
# Output: {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}
```

### What Gets Normalized

The normalizer performs several operations:

1. **Removes invalid features for UPOS**: Features that are not valid for the given part of speech are filtered out.

```python
# VerbForm is only valid for VERB, not NOUN
features = {'Case': 'Nom', 'VerbForm': 'Fin'}
normalized = normalize_features('NOUN', features, feature_set)
print(normalized)
# Output: {'Case': 'Nom'}  # VerbForm removed
```

2. **Removes invalid feature values**: Feature values that are marked as invalid (0) in the feature set are filtered out.

```python
# If 'Fem' is marked as invalid for nouns in the feature set
features = {'Case': 'Nom', 'Gender': 'Fem'}
normalized = normalize_features('NOUN', features, feature_set)
# Output: {'Case': 'Nom'}  # Gender=Fem removed if invalid
```

3. **Filters unknown attributes**: Features not in the feature set are removed.

```python
features = {'Case': 'Nom', 'UnknownAttr': 'Value'}
normalized = normalize_features('NOUN', features, feature_set)
print(normalized)
# Output: {'Case': 'Nom'}  # UnknownAttr removed
```

4. **Handles empty/missing features**: Returns empty dict for underscore, empty string, or empty dict.

```python
# Empty feature marker
normalized = normalize_features('NOUN', '_', feature_set)
print(normalized)
# Output: {}

# Empty string
normalized = normalize_features('NOUN', '', feature_set)
print(normalized)
# Output: {}
```

5. **Preserves insertion order**: Feature order is preserved (Python 3.7+).

```python
features = {'Number': 'Sing', 'Case': 'Nom', 'Gender': 'Masc'}
normalized = normalize_features('NOUN', features, feature_set)
# Order preserved: Number, Case, Gender
```

## XPOS Normalization

Standardize language-specific POS tags and ensure correct correlation with UPOS.

### Basic Usage

```python
from nlp_utilities.normalizers import normalize_xpos

# Normalize XPOS based on UPOS
# Corrects first character and validates position-specific characters
result = normalize_xpos('NOUN', 'a-s---fn-')
print(result)
# Output: 'n-s---fn-'  # First char corrected from 'a' to 'n'

# Another example with VERB
result = normalize_xpos('VERB', 'n3spia---')
print(result)
# Output: 'v3spia---'  # First char corrected from 'n' to 'v'
```

### What Gets Normalized

The XPOS normalizer performs position-based validation:

1. **Corrects the first character**: Sets it to match the Perseus tag for the UPOS.

```python
# PROPN should start with 'n' (same as NOUN in Perseus)
result = normalize_xpos('PROPN', 'a-s---fn-')
print(result)
# Output: 'n-s---fn-'  # First char corrected to 'n'

# Unknown UPOS maps to '-'
result = normalize_xpos('INTJ', 'i-s---fn-')
print(result)
# Output: '---------'  # First char becomes '-'
```

2. **Validates each position**: Each position has specific valid characters based on the Perseus XPOS scheme.

```python
# Position 2: only valid for 'v' (verbs)
result = normalize_xpos('NOUN', 'n1s---mn-')
print(result)
# Output: 'n-s---mn-'  # Position 2 becomes '-' (not valid for 'n')

# Position 2: valid for verbs
result = normalize_xpos('VERB', 'v3spia---')
print(result)
# Output: 'v3spia---'  # Position 2 kept (valid for 'v')
```

**Position validity rules**:
- Position 2: valid for 'v' (verbs only)
- Position 3: valid for 'n', 'v', 'a', 'p', 'm' (nouns, verbs, adjectives, pronouns, numerals)
- Position 4: valid for 'v' (verbs only)
- Position 5: valid for 'v' (verbs only)
- Position 6: valid for 'v' (verbs only)
- Position 7: valid for 'n', 'v', 'a', 'p', 'm'
- Position 8: valid for 'n', 'v', 'a', 'p', 'm'
- Position 9: valid for 'a' (adjectives only)

3. **Ensures lowercase**: All characters are converted to lowercase.

```python
result = normalize_xpos('NOUN', 'N-S---MN-')
print(result)
# Output: 'n-s---mn-'  # All lowercase
```

4. **Pads to correct length**: Ensures the result is exactly 9 characters.

```python
# Short XPOS gets padded
result = normalize_xpos('NOUN', 'Ns')
print(result)
# Output: 'n-s------'  # Padded to 9 characters

# Long XPOS gets truncated after processing
result = normalize_xpos('VERB', 'V3spia---extra')
print(result)
# Output: 'v3spia----'  # Processed and padded
```

### Examples by Part of Speech

```python
from nlp_utilities.normalizers import normalize_xpos

# Verb: most positions are valid
result = normalize_xpos('VERB', 'Vabcdefgh')
print(result)
# Output: 'vabcdefg-'  # Positions 2-8 valid, 9 invalid for verbs

# Adjective: positions 3, 7, 8, 9 valid
result = normalize_xpos('ADJ', 'Aabcdefgh')
print(result)
# Output: 'a-b---fgh'  # Only positions 3, 7, 8, 9 kept

# Noun: positions 3, 7, 8 valid
result = normalize_xpos('NOUN', 'Nabcdefgh')
print(result)
# Output: 'n-b---fg-'  # Only positions 3, 7, 8 kept

# Pronoun: same as noun
result = normalize_xpos('PRON', 'Pabcdefgh')
print(result)
# Output: 'p-b---fg-'  # Only positions 3, 7, 8 kept
```

## Feature Set Loading

Load language-specific feature sets for validation.

### Basic Loading

```python
from nlp_utilities.loaders import load_language_data

# Load Latin feature set
feature_set = load_language_data('feats', language='la')

# Feature set structure:
# {
#     'Case': {
#         'byupos': {
#             'NOUN': {'Nom': 1, 'Gen': 1, 'Dat': 1, 'Acc': 1, 'Voc': 1, 'Abl': 1},
#             'ADJ': {'Nom': 1, 'Gen': 1, 'Dat': 1, 'Acc': 1, 'Voc': 1, 'Abl': 1},
#             'VERB': {'Nom': 0, 'Gen': 0, ...},  # Invalid for verbs
#         }
#     },
#     'Gender': {
#         'byupos': {
#             'NOUN': {'Masc': 1, 'Fem': 1, 'Neut': 1},
#             'ADJ': {'Masc': 1, 'Fem': 1, 'Neut': 1},
#             ...
#         }
#     },
#     ...
# }

# Use with normalize_features
from nlp_utilities.normalizers import normalize_features

normalized = normalize_features('NOUN', 'Case=Nom|Gender=Masc', feature_set)
```

### Understanding the Feature Set Format

Each feature in the set has a `byupos` dictionary that maps UPOS tags to valid values:

- **Value `1`**: Valid for this UPOS
- **Value `0`**: Invalid/not allowed for this UPOS
- **Missing UPOS**: Feature not applicable to this UPOS

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

Process an entire CoNLL-U file to normalize all features and XPOS tags:

```python
from nlp_utilities.loaders import load_language_data, load_conllu
from nlp_utilities.normalizers import normalize_features, normalize_xpos
from nlp_utilities.converters.features import feature_dict_to_string

# Load feature set
feature_set = load_language_data('feats', language='la')

# Load CoNLL-U file
sentences = load_conllu('input.conllu')

# Normalize all annotations
for sentence in sentences:
    for token in sentence:
        # Skip multiword tokens and empty nodes
        if '-' in str(token['id']) or '.' in str(token['id']):
            continue
        
        # Normalize features
        if token['feats'] != '_':
            normalized_feats = normalize_features(
                token['upos'],
                token['feats'],
                feature_set
            )
            # Convert back to string for CoNLL-U
            if normalized_feats:
                token['feats'] = feature_dict_to_string(normalized_feats)
            else:
                token['feats'] = '_'
        
        # Normalize XPOS
        if token['xpos'] != '_' and token['upos'] != '_':
            token['xpos'] = normalize_xpos(token['upos'], token['xpos'])

# Save normalized file
save_conllu(sentences, 'output_normalized.conllu')
```

### Cleaning Imported Annotations

Normalize annotations from external sources:

```python
from nlp_utilities.normalizers import normalize_features, normalize_xpos
from nlp_utilities.loaders import load_language_data

feature_set = load_language_data('feats', language='la')

def clean_annotation(token, feature_set):
    """Clean a single token's annotation."""
    # Normalize XPOS
    if token['xpos'] != '_' and token['upos'] != '_':
        try:
            token['xpos'] = normalize_xpos(token['upos'], token['xpos'])
        except ValueError as e:
            print(f"Warning: Could not normalize XPOS for token {token['form']}: {e}")
            token['xpos'] = '_'
    
    # Normalize features
    if token['feats'] != '_':
        try:
            normalized = normalize_features(token['upos'], token['feats'], feature_set)
            if normalized:
                from nlp_utilities.converters.features import feature_dict_to_string
                token['feats'] = feature_dict_to_string(normalized)
            else:
                token['feats'] = '_'
        except ValueError as e:
            print(f"Warning: Could not normalize features for token {token['form']}: {e}")
            token['feats'] = '_'
    
    return token

# Apply to all tokens
for sentence in sentences:
    for token in sentence:
        if isinstance(token['id'], int):  # Skip multiword tokens
            clean_annotation(token, feature_set)
```

### Validating After Normalization

Always validate after normalizing to ensure correctness:

```python
from nlp_utilities.normalizers import normalize_features, normalize_xpos
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
from nlp_utilities.normalizers import normalize_features, normalize_xpos
from nlp_utilities.loaders import load_language_data

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
                if isinstance(token['id'], int):
                    # Normalize XPOS
                    if token['xpos'] != '_' and token['upos'] != '_':
                        token['xpos'] = normalize_xpos(token['upos'], token['xpos'])
                    
                    # Normalize features
                    if token['feats'] != '_':
                        normalized = normalize_features(
                            token['upos'],
                            token['feats'],
                            feature_set
                        )
                        if normalized:
                            from nlp_utilities.converters.features import feature_dict_to_string
                            token['feats'] = feature_dict_to_string(normalized)
                        else:
                            token['feats'] = '_'
        
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
from nlp_utilities.normalizers import normalize_features, normalize_xpos

# XPOS normalization errors
try:
    result = normalize_xpos(None, 'n-s---mn-')
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: Must pass both UPOS and XPOS

try:
    result = normalize_xpos('NOUN', '')
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: Must pass both UPOS and XPOS

# Feature normalization errors
try:
    result = normalize_features(None, 'Case=Nom', feature_set)
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: Must pass UPOS, FEATS, and a Feature set

try:
    result = normalize_features('NOUN', 'Case=Nom', None)
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: Must pass UPOS, FEATS, and a Feature set
```

### Safe Normalization with Fallbacks

```python
def safe_normalize_xpos(upos, xpos):
    """Normalize XPOS with fallback."""
    try:
        return normalize_xpos(upos, xpos)
    except (ValueError, KeyError) as e:
        print(f"Warning: Could not normalize XPOS '{xpos}' for UPOS '{upos}': {e}")
        return '_'  # Return empty marker on error

def safe_normalize_features(upos, feats, feature_set):
    """Normalize features with fallback."""
    try:
        normalized = normalize_features(upos, feats, feature_set)
        if normalized:
            from nlp_utilities.converters.features import feature_dict_to_string
            return feature_dict_to_string(normalized)
        return '_'
    except (ValueError, KeyError) as e:
        print(f"Warning: Could not normalize features '{feats}' for UPOS '{upos}': {e}")
        return '_'

# Use safe versions in production
for token in sentence:
    token['xpos'] = safe_normalize_xpos(token['upos'], token['xpos'])
    token['feats'] = safe_normalize_features(token['upos'], token['feats'], feature_set)
```

## See Also

- [Validation](validation.md) - Validating normalized files
- [Converters](converters.md) - Converting between formats
- {ref}`api_reference` - Detailed normalizer API

