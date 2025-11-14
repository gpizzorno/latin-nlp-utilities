# Normalization

This guide covers normalizing and standardizing linguistic annotations.

## Overview

Normalization utilities ensure consistency in annotation format:

- **Feature normalization**: Fix capitalization, sort alphabetically, validate format
- **XPOS normalization**: Standardize language-specific POS tags
- **Whitespace normalization**: Handle text processing exceptions

These tools are essential for:

- Cleaning imported or converted annotations
- Ensuring Universal Dependencies compliance
- Preparing data for validation and evaluation
- Standardizing annotations across annotators

## Quick Start

Normalizing morphological features:

```python
from nlp_utilities.normalizers import normalize_features

# Fix capitalization and ordering
messy = "number=Sing|case=Nom|gender=MASC"
clean = normalize_features(messy)
print(clean)  # "Case=Nom|Gender=Masc|Number=Sing"
```

Normalizing XPOS tags:

```python
from nlp_utilities.normalizers import normalize_xpos

# Standardize case and format
tag = "v3spia---"
normalized = normalize_xpos(tag, language='la')
print(normalized)  # Standardized Perseus tag
```

## Feature Normalization

The feature normalizer ensures morphological features meet CoNLL-U specifications.

### Basic Usage

```python
from nlp_utilities.normalizers import normalize_features

examples = [
    "number=Sing|case=Nom",           # Wrong capitalization
    "Gender=Masc|Case=Nom|Number=Sing", # Wrong order
    "Case=Nom|Number=Sing|case=Gen",  # Duplicate keys
    "Case=Nom||Number=Sing",          # Extra separator
]

for feature_string in examples:
    normalized = normalize_features(feature_string)
    print(f"{feature_string:40s} → {normalized}")
```

### What Gets Normalized

1. **Alphabetical Sorting**

   Features are sorted by name:

   `Number=Sing|Gender=Masc|Case=Nom` → `Case=Nom|Gender=Masc|Number=Sing`

2. **Format Cleaning**

   Removes extra separators and whitespace:

   `Case=Nom | Number=Sing` → `Case=Nom|Number=Sing`
   `Case=Nom||Number=Sing` → `Case=Nom|Number=Sing`
   `Case=Nom|` → `Case=Nom`

3. **Duplicate Removal**

   Keeps first occurrence of duplicate features:

   `Case=Nom|Number=Sing|Case=Gen` → `Case=Nom|Number=Sing`

### Advanced Feature Normalization

With validation:

```python
from nlp_utilities.normalizers import normalize_features
from nlp_utilities.loaders import load_language_data

# Load valid feature set for language
feature_set = load_language_data('la')

# Normalize with validation
features = "Case=Nom|Number=Sing|Gender=Masc"
normalized = normalize_features(
    features,
    feature_set=feature_set,
    strict=True  # Raise error on invalid features
)
```

Custom feature mappings:

```python
# Map non-standard values to standard
custom_mappings = {
    'Case': {
        'nominative': 'Nom',
        'genitive': 'Gen',
        'accusative': 'Acc',
    }
}

normalized = normalize_features(
    "Case=nominative|Number=singular",
    value_mappings=custom_mappings
)
# Result: "Case=Nom|Number=singular"
```

## XPOS Normalization

Standardize language-specific POS tags.

### Basic Usage

```python
from nlp_utilities.normalizers import normalize_xpos

# Perseus-style tags
tags = [
    "V3SPIA---",   # Wrong case
    "v3spia   ",   # Extra whitespace
    "v-3-s-p-i-a-", # Wrong separator format
]

for tag in tags:
    normalized = normalize_xpos(tag, language='la')
    print(f"{tag:20s} → {normalized}")
```

### Language-Specific Normalization

Different normalization rules by language/tagset:

```python
from nlp_utilities.normalizers import normalize_xpos

# Latin (Perseus format)
latin_tag = normalize_xpos("V3SPIA---", language='la')
# Expected: "v3spia---" (lowercase, dash-padded)

# Custom tagset
custom_tag = normalize_xpos(
    "VERB-3-SING-PRES",
    language='custom',
    format_spec='dash-separated'
)
```

### What Gets Normalized

1. **Case standardization**

   `V3SPIA---` → `v3spia---`  # Lowercase
   `N-S---FN-` → `n-s---fn-`  # Lowercase

2. **Whitespace removal**

   `v3spia--- ` → `v3spia---`
   ` n-s---fn-` → `n-s---fn-`

3. **Format validation**

   Check length and structure:
   ```python
   # Perseus tags should be 9 characters
   assert len(normalize_xpos("v3spia---", 'la')) == 9
   ```

## Feature Set Loading

Load language-specific feature sets for validation.

### Basic Loading

```python
from nlp_utilities.loaders import load_language_data

# Load Latin feature set
la_features = load_language_data('la')

print(la_features['upos'])      # Valid UPOS tags
print(la_features['deprels'])   # Valid dependency relations
print(la_features['features'])  # Valid morphological features
```

### Using with Normalization

```python
from nlp_utilities.loaders import load_language_data
from nlp_utilities.normalizers import normalize_features

feature_set = load_language_data('la')

# Validate during normalization
try:
    normalized = normalize_features(
        "Case=Nom|InvalidFeature=Value",
        feature_set=feature_set,
        strict=True
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

### Available Languages

Currently supported language codes:

- `la`: Latin
- `en`: English (for testing/examples)

### Custom Feature Sets

Define your own feature set:

```python
custom_features = {
    'upos': ['NOUN', 'VERB', 'ADJ', ...],
    'features': {
        'Case': ['Nom', 'Gen', 'Acc', 'Dat', 'Abl'],
        'Number': ['Sing', 'Plur'],
        'Gender': ['Masc', 'Fem', 'Neut'],
    },
    'deprels': ['nsubj', 'obj', 'obl', ...],
}

normalized = normalize_features(
    features_string,
    feature_set=custom_features,
    strict=True
)
```

## Whitespace Exceptions

Handle special tokenization cases.

### Loading Exceptions

```python
from nlp_utilities.loaders import load_whitespace_exceptions

# Load exceptions for a language
exceptions = load_whitespace_exceptions('la')

print(exceptions)
# {'single': ['l', 'D', 'd'], 'before': [...], 'after': [...]}
```

### Using Exceptions

Apply during tokenization:

```python
def tokenize_with_exceptions(text, language='la'):
    """Tokenize respecting whitespace exceptions."""
    exceptions = load_whitespace_exceptions(language)

    # Single-character tokens
    for char in exceptions.get('single', []):
        # Handle 'l', 'D', 'd' as separate tokens
        text = text.replace(f' {char} ', f' {char}')

    # Tokens that should have space before
    for token in exceptions.get('before', []):
        text = text.replace(token, f' {token}')

    # Tokens that should have space after
    for token in exceptions.get('after', []):
        text = text.replace(token, f'{token} ')

    return text.split()
```

Common exceptions for Latin:

Single-letter tokens:

`Marcus M. Tullius` → [`Marcus`, `M`, `.`, `Tullius`]

Abbreviations:

`D.M.` → [`D`, `.`, `M`, `.`]  # Dis Manibus

## Normalization Workflows

### Batch File Normalization

Normalize all features in a CoNLL-U file:

```python
from nlp_utilities.normalizers import normalize_features
from nlp_utilities.loaders import load_conllu, load_language_data

def normalize_conllu_file(input_file, output_file, language='la'):
    """Normalize all features in a file."""
    # Load data
    sentences = load_conllu(input_file)
    feature_set = load_language_data(language)

    # Normalize each token's features
    for sentence in sentences:
        for token in sentence:
            if token['feats'] != '_':
                try:
                    token['feats'] = normalize_features(
                        token['feats'],
                        feature_set=feature_set,
                        strict=False  # Continue on errors
                    )
                except Exception as e:
                    print(f"Warning: Could not normalize {token['feats']}: {e}")

    # Save normalized
    save_conllu(sentences, output_file)

# Process file
normalize_conllu_file('input.conllu', 'normalized.conllu')
```

### Pre-validation Normalization

Normalize before validation to catch format issues:

```python
from nlp_utilities.normalizers import normalize_features, normalize_xpos
from nlp_utilities.conllu.validators import Validator

def normalize_and_validate(filename, language='la'):
    """Normalize then validate a file."""
    # Load and normalize
    sentences = load_conllu(filename)

    for sentence in sentences:
        for token in sentence:
            # Normalize features
            if token['feats'] != '_':
                token['feats'] = normalize_features(token['feats'])

            # Normalize XPOS
            if token['xpos'] != '_':
                token['xpos'] = normalize_xpos(token['xpos'], language)

    # Save normalized version
    temp_file = 'normalized_temp.conllu'
    save_conllu(sentences, temp_file)

    # Validate
    validator = Validator(temp_file, language=language)
    is_valid = validator.validate()

    if not is_valid:
        validator.report_errors()

    return is_valid
```

### Post-conversion Normalization

Normalize after format conversion:

```python
from nlp_utilities.brat import brat_to_conllu
from nlp_utilities.normalizers import normalize_features
from nlp_utilities.loaders import load_language_data

def convert_and_normalize(brat_dir, output_file, ref_file):
    """Convert from Brat and normalize features."""
    # Load feature set
    feature_set = load_language_data('la')

    # Convert
    brat_to_conllu(
        input_directory=brat_dir,
        output_directory='temp/',
        ref_conllu=ref_file,
        feature_set=feature_set
    )

    # Load converted file
    sentences = load_conllu('temp/converted.conllu')

    # Normalize
    for sentence in sentences:
        for token in sentence:
            if token['feats'] != '_':
                token['feats'] = normalize_features(
                    token['feats'],
                    feature_set=feature_set
                )

    # Save final version
    save_conllu(sentences, output_file)
```

## Normalization Best Practices

1. **Normalize Early**

   Apply normalization as early as possible in your pipeline:
   ```python
   # Immediately after import/conversion
   data = import_data(source)
   data = normalize_all(data)
   data = validate(data)
   ```
2. **Log Normalization Changes**

   Track what was changed:
   ```python
   def normalize_with_logging(features):
       """Normalize and log changes."""
       original = features
       normalized = normalize_features(features)

       if original != normalized:
           logger.info(f"Normalized: {original} → {normalized}")

       return normalized
   ```
3. **Validate After Normalization**

   Ensure normalization produced valid output:
   ```python
   from nlp_utilities.conllu.validators import FeatureValidator

   normalized = normalize_features(features)
   validator = FeatureValidator()

   if not validator.validate_feature_string(normalized):
       raise ValueError(f"Normalization produced invalid result: {normalized}")
   ```
4. **Handle Errors Gracefully**

   Don’t fail on single bad tokens:
   ```python
   for token in sentence:
       try:
           token['feats'] = normalize_features(token['feats'])
       except Exception as e:
           logger.warning(f"Could not normalize token {token['id']}: {e}")
           # Keep original or use placeholder
           continue
   ```
5. **Document Normalization Rules**

   Keep record of what normalization was applied:
   ```python
   # Add to sentence metadata
   sentence['metadata']['normalization'] = {
       'features': 'capitalized, sorted, validated',
       'xpos': 'lowercased, length-checked',
       'timestamp': datetime.now().isoformat(),
   }
   ```

## Common Normalization Issues

### Non-standard Feature Names

**Problem**: Features use non-UD names.

**Solution**: Map to standard names before normalization:

```python
# Define mapping
FEATURE_NAME_MAP = {
    'case': 'Case',
    'num': 'Number',
    'pers': 'Person',
    'gen': 'Gender',
}

def map_and_normalize(features):
    """Map non-standard names then normalize."""
    # Replace feature names
    for old, new in FEATURE_NAME_MAP.items():
        features = features.replace(f'{old}=', f'{new}=')

    # Then normalize
    return normalize_features(features)
```

### Conflicting Feature Values

**Problem**: Same feature appears multiple times with different values.

**Solution**: Resolve conflicts before normalization:

```python
def resolve_conflicts(features):
    """Resolve duplicate features."""
    feat_dict = {}

    for pair in features.split('|'):
        name, value = pair.split('=')

        if name in feat_dict and feat_dict[name] != value:
            # Conflict! Choose resolution strategy
            logger.warning(f"Conflict: {name}={feat_dict[name]} vs {name}={value}")
            # Strategy: keep first, keep last, or merge?
            continue  # Keep first

        feat_dict[name] = value

    # Reconstruct
    return '|'.join(f'{k}={v}' for k, v in sorted(feat_dict.items()))
```

### Invalid Feature Values

**Problem**: Feature values don’t match expected set.

**Solution**: Map or flag for manual review:

```python
def validate_and_normalize(features, feature_set):
    """Normalize and validate feature values."""
    normalized = normalize_features(features)

    # Check values
    for feat in normalized.split('|'):
        name, value = feat.split('=')

        valid_values = feature_set['features'].get(name, [])
        if value not in valid_values:
            logger.error(f"Invalid value: {name}={value}")
            # Flag for manual review
            raise ValueError(f"Invalid feature value: {name}={value}")

    return normalized
```

## See Also

- [Validation](validation.md) - Validating normalized files
- [Converters](converters.md) - Converting between formats
- {ref}`api_reference` - Detailed normalizer API
