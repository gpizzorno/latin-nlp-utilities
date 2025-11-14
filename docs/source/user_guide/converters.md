# Converters

This guide covers converting between different tagsets and annotation schemes for Latin treebanks.

## Overview

The converters module provides utilities for standardizing annotations from various Latin treebanks
to a common format. This includes:

- **UPOS conversion**: Language-specific POS tags → Universal POS tags
- **Feature conversion**: Various morphological annotation schemes → Universal Features
- **XPOS conversion**: Normalizing language-specific POS tags across treebanks

These converters are essential for:

- Harmonizing annotations across different Latin treebanks
- Creating cross-treebank training datasets
- Adapting legacy annotations to Universal Dependencies standards

## Quick Start

Converting from PROIEL XPOS to Perseus XPOS:

```python
from nlp_utilities.converters.xpos import proiel_to_perseus

proiel_tag = "V-3PAI---3S---"
perseus_tag = proiel_to_perseus(proiel_tag)
print(perseus_tag)  # "v3spia---"
```

Converting from ITTB XPOS to Perseus XPOS:

```python
from nlp_utilities.converters.xpos import ittb_to_perseus

ittb_tag = "Vif3s3"
perseus_tag = ittb_to_perseus(ittb_tag)
print(perseus_tag)  # "v3sfia---"
```

## XPOS Converters

The XPOS converters normalize language-specific POS tags from different treebanks to a
common Perseus-style format.

### Supported Treebanks

- **PROIEL**: Prague-style tags (e.g., `V-3PAI---3S---`)
- **ITTB**: Index Thomisticus Treebank tags (e.g., `Vif3s3`)
- **LLCT**: Late Latin Charter Treebank tags (custom format)
- **Perseus**: Target format (e.g., `v3spia---`)

### PROIEL to Perseus

PROIEL uses detailed morphological codes:

```python
from nlp_utilities.converters.xpos import proiel_to_perseus

examples = [
    ("V-3PAI---3S---", "v3spia---"),  # Verb: 3rd person, present, active, indicative
    ("Nb---mn--n---", "n-s---mn-"),   # Noun: masculine, nominative
    ("A-p---mn-----", "a-p---mn-"),   # Adjective: plural, masculine, nominative
]

for proiel, expected_perseus in examples:
    result = proiel_to_perseus(proiel)
    print(f"{proiel:15s} → {result:10s} (expected: {expected_perseus})")
```

**Format details**:

- Position-based encoding with dashes for N/A features
- Extensive mood, voice, and case information
- 13-character tag length

### ITTB to Perseus

ITTB uses compact alphanumeric codes:

```python
from nlp_utilities.converters.xpos import ittb_to_perseus

examples = [
    ("Vif3s3", "v3sfia---"),    # Verb: indicative future, 3rd singular, active
    ("Ncnsa", "n-s---na-"),     # Noun: common, neuter, singular, accusative
    ("A1nmpa", "a-p---mn-"),    # Adjective: 1st declension, nominative, masculine, plural
]

for ittb, expected_perseus in examples:
    result = ittb_to_perseus(ittb)
    print(f"{ittb:10s} → {result:10s} (expected: {expected_perseus})")
```

**Format details**:

- Letter codes for POS and morphological features
- Number codes for person and declension
- 5-7 character tag length

### LLCT to Perseus

LLCT uses custom codes for Late Latin:

```python
from nlp_utilities.converters.xpos import llct_to_perseus

# LLCT tags often include medieval Latin features
llct_tag = "VF3S3A"  # Example LLCT format
perseus_tag = llct_to_perseus(llct_tag)
```

**Special considerations**:

- Handles medieval orthographic variants

### Perseus to Other Formats

For reverse conversion or cross-referencing:

```python
from nlp_utilities.converters.xpos import perseus_to_proiel, perseus_to_ittb

perseus_tag = "v3spia---"

# Convert to PROIEL format
proiel_tag = perseus_to_proiel(perseus_tag)

# Convert to ITTB format
ittb_tag = perseus_to_ittb(perseus_tag)
```

**Note**: Reverse conversion may be lossy as Perseus format has less granularity.

## UPOS Converters

Convert language-specific POS tags to Universal POS tags.

### DALME to UPOS

Convert DALME project tags to Universal POS:

```python
from nlp_utilities.converters.upos import dalme_to_upos

dalme_tag = "NC"  # Common noun
upos_tag = dalme_to_upos(dalme_tag)
print(upos_tag)  # "NOUN"
```

Mapping examples:

```python
mappings = {
    'NC': 'NOUN',      # Common noun
    'NP': 'PROPN',     # Proper noun
    'VA': 'VERB',      # Active verb
    'VP': 'VERB',      # Passive verb
    'ADJ': 'ADJ',      # Adjective
    'ADV': 'ADV',      # Adverb
    'PRE': 'ADP',      # Preposition
    'CON': 'CCONJ',    # Conjunction
}
```

### Perseus to UPOS

Infer UPOS from Perseus XPOS tags:

```python
from nlp_utilities.converters.upos import perseus_to_upos

perseus_tag = "v3spia---"
upos = perseus_to_upos(perseus_tag)
print(upos)  # "VERB"

perseus_tag = "n-s---fn-"
upos = perseus_to_upos(perseus_tag)
print(upos)  # "NOUN"
```

**Inference rules**:

- First character indicates broad POS (

  ```
  ``
  ```

  v\`\`→VERB, 

  ```
  ``
  ```

  n\`\`→NOUN, etc.)
- Additional features may refine classification
- Handles auxiliary verbs based on context

## Feature Converters

Convert morphological feature representations between formats.

### Feature Dictionary ↔ String

Convert between dictionary and CoNLL-U string format:

```python
from nlp_utilities.converters.features import (
    feature_dict_to_string,
    feature_string_to_dict
)

# Dict to string
features = {
    'Case': 'Nom',
    'Gender': 'Masc',
    'Number': 'Sing'
}
feat_string = feature_dict_to_string(features)
print(feat_string)  # "Case=Nom|Gender=Masc|Number=Sing"

# String to dict
feat_string = "Case=Gen|Number=Plur"
features = feature_string_to_dict(feat_string)
print(features)  # {'Case': 'Gen', 'Number': 'Plur'}
```

**Automatic sorting**: Output is alphabetically sorted by feature name.

### Feature Normalization

Normalize feature strings (capitalization, sorting, validation):

```python
from nlp_utilities.normalizers import normalize_features

# Fix capitalization and sort
messy = "number=Sing|case=Nom|gender=MASC"
clean = normalize_features(messy)
print(clean)  # "Case=Nom|Gender=Masc|Number=Sing"

# Validate and correct feature names
invalid = "Kase=Nom|Numer=Sing"
corrected = normalize_features(invalid, strict=True)
# Raises exception or returns corrected version
```

## Integration Workflows

### Harmonizing Multiple Treebanks

Create a unified dataset from multiple sources:

```python
from nlp_utilities.converters.xpos import proiel_to_perseus, ittb_to_perseus
from nlp_utilities.loaders import load_conllu

def harmonize_xpos(conllu_file, source_format):
    """Convert XPOS tags to Perseus format in-place."""
    sentences = load_conllu(conllu_file)

    converter = {
        'proiel': proiel_to_perseus,
        'ittb': ittb_to_perseus,
    }[source_format]

    for sentence in sentences:
        for token in sentence:
            if token['xpos'] != '_':
                token['xpos'] = converter(token['xpos'])

    return sentences

# Harmonize multiple treebanks
proiel_data = harmonize_xpos('proiel.conllu', 'proiel')
ittb_data = harmonize_xpos('ittb.conllu', 'ittb')

# Combine into unified dataset
all_data = proiel_data + ittb_data
```

### Cross-Treebank Training

Prepare data for cross-treebank model training:

```python
from nlp_utilities.converters.xpos import proiel_to_perseus, ittb_to_perseus
from nlp_utilities.normalizers import normalize_features

def prepare_for_training(conllu_files):
    """Standardize multiple treebanks for joint training."""
    unified = []

    for file, format_type in conllu_files:
        sentences = load_conllu(file)

        # Convert XPOS to unified format
        converter = proiel_to_perseus if format_type == 'proiel' else ittb_to_perseus

        for sentence in sentences:
            for token in sentence:
                # Standardize XPOS
                if token['xpos'] != '_':
                    token['xpos'] = converter(token['xpos'])

                # Normalize features
                if token['feats'] != '_':
                    token['feats'] = normalize_features(token['feats'])

            unified.append(sentence)

    return unified

# Prepare training data
treebanks = [
    ('la_proiel-ud-train.conllu', 'proiel'),
    ('la_ittb-ud-train.conllu', 'ittb'),
]
training_data = prepare_for_training(treebanks)
```

### Legacy Data Migration

Migrate old annotations to UD format:

```python
from nlp_utilities.converters import (
    dalme_to_upos,
    perseus_to_upos,
    feature_dict_to_string
)

def migrate_legacy_annotation(old_file, new_file):
    """Convert legacy format to UD CoNLL-U."""
    sentences = load_legacy_format(old_file)  # Custom loader

    for sentence in sentences:
        for token in sentence:
            # Convert POS tags
            if 'dalme_pos' in token:
                token['upos'] = dalme_to_upos(token['dalme_pos'])

            # Convert features
            if 'legacy_features' in token:
                feature_dict = parse_legacy_features(token['legacy_features'])
                token['feats'] = feature_dict_to_string(feature_dict)

            # Clean up old fields
            del token['dalme_pos']
            del token['legacy_features']

    save_conllu(sentences, new_file)
```

## Conversion Best Practices

1. **Validate After Conversion**

   Always validate converted files:
   ```python
   from nlp_utilities.conllu.validators import Validator
   from nlp_utilities.converters.xpos import proiel_to_perseus

   # Convert
   converted = convert_treebank('input.conllu')
   save_conllu(converted, 'output.conllu')

   # Validate
   validator = Validator('output.conllu', language='la')
   if not validator.validate():
       print("Conversion produced invalid CoNLL-U!")
   ```
2. **Preserve Original Annotations**

   Keep originals in MISC column:
   ```python
   for token in sentence:
       original_xpos = token['xpos']
       token['xpos'] = converter(original_xpos)

       # Preserve in MISC
       token['misc'] = f"OrigXPOS={original_xpos}"
   ```
3. **Document Conversion Decisions**

   Record any lossy conversions or ambiguity resolutions:
   ```python
   # Log ambiguous conversions
   conversion_log = []

   for token in sentence:
       old_tag = token['xpos']
       new_tag = converter(old_tag)

       if is_ambiguous_conversion(old_tag, new_tag):
           conversion_log.append({
               'sentence_id': sentence['id'],
               'token_id': token['id'],
               'old': old_tag,
               'new': new_tag,
               'note': 'Ambiguous gender/number'
           })
   ```
4. **Test on Representative Sample**

   Validate converter accuracy on annotated samples:
   ```python
   from nlp_utilities.conllu.evaluators import Evaluator

   # Manual gold standard conversions
   gold_conversions = load_gold_conversions('gold_sample.conllu')

   # Automatic conversions
   auto_conversions = convert_sample('sample.conllu')

   # Evaluate
   evaluator = Evaluator(gold_conversions, auto_conversions)
   accuracy = evaluator.evaluate()['XPOS']

   if accuracy < 95.0:
       print(f"Warning: Conversion accuracy only {accuracy:.1f}%")
   ```
5. **Handle Edge Cases**

   Account for treebank-specific quirks:
   ```python
   def safe_convert(tag, converter):
       """Convert with fallback for edge cases."""
       try:
           return converter(tag)
       except ValueError as e:
           # Log problematic tag
           logger.warning(f"Could not convert '{tag}': {e}")
           # Return original or default
           return tag
   ```

## Common Conversion Issues

### Missing Mappings

**Problem**: Converter raises exception for unknown tag.

**Solution**: Check if tag is non-standard or typo:

```python
from nlp_utilities.converters.xpos import proiel_to_perseus

try:
    result = proiel_to_perseus(unknown_tag)
except KeyError:
    print(f"Unknown tag: {unknown_tag}")
    # Manually inspect and add to converter if valid
```

### Ambiguous Conversions

**Problem**: Multiple possible target tags for one source tag.

**Solution**: Use context or default to most common:

```python
def context_aware_conversion(token, converter):
    """Use context to resolve ambiguity."""
    base_conversion = converter(token['xpos'])

    # Refine based on dependency relation
    if token['deprel'] == 'aux' and base_conversion.startswith('v'):
        # Verb in auxiliary relation
        token['upos'] = 'AUX'

    return base_conversion
```

### Lossy Conversions

**Problem**: Target format has less detail than source.

**Solution**: Preserve lost information in MISC:

```python
def convert_with_preservation(token, converter):
    """Convert while preserving lost details."""
    original = token['xpos']
    converted = converter(original)

    # Detect information loss
    if has_lost_information(original, converted):
        # Preserve in MISC column
        if token['misc'] == '_':
            token['misc'] = f"OrigXPOS={original}"
        else:
            token['misc'] += f"|OrigXPOS={original}"

    token['xpos'] = converted
```

## See Also

- [Normalization](normalization.md) - Normalizing features and tags
- [Validation](validation.md) - Validating converted files
- {ref}`api_reference` - Detailed converter API
