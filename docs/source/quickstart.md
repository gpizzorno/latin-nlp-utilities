(quickstart)=
# Quick Start Guide

This guide will get you up and running with `latin-nlp-utilities` in minutes.

## Installation

First, install the package:

```bash
pip install latin-nlp-utilities
```

Verify the installation:

```bash
python -c "import nlp_utilities; print('Ready to go!')"
```

## Conversion

Let’s convert a CoNLL-U file to brat format for visual annotation.

### CoNLL-U to brat

```python
from nlp_utilities.brat import conllu_to_brat

# Convert CoNLL-U to brat format
conllu_to_brat(
    conllu_filename='my_corpus.conllu',
    output_directory='brat_annotations/',
    output_root=True,  # Show ROOT nodes
    sents_per_doc=10,  # 10 sentences per document
)

print("Conversion complete! Check brat_annotations directory")
```

**What happens:**

- Creates `.txt` files with raw text
- Creates `.ann` files with standoff annotations
- Adds configuration files for brat visualization
- Adds `metadata.json` with information about the conversion parameters (used by `brat_to_conllu`)
- Splits long files into manageable documents

### brat to CoNLL-U

After annotating in brat, convert back to CoNLL-U:

```python
from nlp_utilities.brat import brat_to_conllu
from nlp_utilities.loaders import load_language_data

# Load feature set for validation
feature_set = load_language_data('feats', language='la')

# Convert back to CoNLL-U
brat_to_conllu(
    input_directory='brat_annotations/',
    output_directory='updated_conllu/',
    ref_conllu='my_corpus.conllu',  # Original for features
    feature_set=feature_set,
)

print("Converted back to CoNLL-U!")
```

## Evaluation

Evaluate parser output against gold standard.

### Basic Evaluation

```python
from nlp_utilities.conllu import ConlluEvaluator

# Compare gold standard with system output
evaluator = ConlluEvaluator(eval_deprels=True, treebank_type='0')
scores = evaluator.evaluate_files(
    gold_path='path/to/gold_standard.conllu',
    system_path='path/to/parser_output.conllu',
)

# Print results
print(f"Unlabeled Attachment Score (UAS): {results['UAS']:.2f}%")
print(f"Labeled Attachment Score (LAS): {results['LAS']:.2f}%")
print(f"UPOS Accuracy: {results['UPOS']:.2f}%")
```

## Validation

Validate CoNLL-U files for format and linguistic correctness.

### Basic Validation

```python
from nlp_utilities.conllu import ConlluValidator

# Create validator
validator = ConlluValidator(lang='la', level=2)

# Run validation checks
reporter = validator.validate_file('path/to/yourfile.conllu')

# Print error count
print(f'Errors found: {reporter.get_error_count()}')

# Inspect first error
sent_id, order, testlevel, error = reporter.errors[0]
print(f'Sentence ID: {sent_id}')  # e.g. 34
print(f'Testing at level: {sent_id}')  # e.g. 2
print(f'Error test level: {error.testlevel}')  # e.g. 1
print(f'Error type: {error.error_type}')  # e.g. "Metadata"
print(f'Test ID: {error.testid}')  # e.g. "text-mismatch"
print(f'Error message: {error.msg}')  # Full error message (see below)

# Print all errors formatted as strings
for error in reporter.format_errors():
    print(error)

# Example output:
# Sentence 34:
# [L2 Metadata text-mismatch] The text attribute does not match the text 
# implied by the FORM and SpaceAfter=No values. Expected: 'Una scala....' 
# Reconstructed: 'Una scala ....' (first diff at position 9)
```

## Tagset Conversion

Convert between different tagsets.

### XPOS Conversion

Standardize XPOS tags from different treebanks:

```python
from nlp_utilities.converters.upos import dalme_to_upos, upos_to_perseus
from nlp_utilities.converters.xpos import ittb_to_perseus, llct_to_perseus

print(dalme_to_upos('adjective'))
# Returns 'ADJ'

print(upos_to_perseus('NOUN'))
# Returns 'n'

print(ittb_to_perseus('VERB', 'gen4|tem1|mod1'))  
# Returns 'v1sp-----'

# LLCT converter requires UPOS, XPOS, and FEATS
print(llct_to_perseus('NOUN', 'n|n|-|s|-|-|-|m|n|-', 'Case=Nom|Gender=Masc|Number=Sing'))
# Returns 'n-s---mn-'
```

### Feature Conversion

Convert between feature string and dictionary formats:

```python
from nlp_utilities.converters.features import feature_string_to_dict, feature_dict_to_string

# String to dictionary
feat_string = "Case=Nom|Gender=Masc|Number=Sing"
feat_dict = feature_string_to_dict(feat_string)
print(feat_dict)
# Output: {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}

# Dictionary to string (automatically sorted)
feat_dict = {'Number': 'Sing', 'Case': 'Gen', 'Gender': 'Fem'}
feat_string = feature_dict_to_string(feat_dict)
print(feat_string)
# Output: Case=Gen|Gender=Fem|Number=Sing
```

## Normalization

Clean and standardize morphological annotations.

### Normalize Morphology

Normalize XPOS and FEATS together with automatic format detection and validation:

```python
from nlp_utilities.loaders import load_language_data
from nlp_utilities.normalizers import normalize_morphology

feature_set = load_language_data('feats', language='la')

# Example: NUM with NumForm feature reconciliation
xpos, feats = normalize_morphology(
    upos='NUM',
    xpos='m-p---fa-',
    feats='Case=Acc|Gender=Fem|Number=Plur',
    feature_set=feature_set,
    ref_features='NumForm=Word'  # Missing feature added from reference
)

print(xpos)
# Output: 'm-p---fa-' (validated)

print(feats)
# Output: {'Case': 'Acc', 'Gender': 'Fem', 'NumForm': 'Word', 'Number': 'Plur'}
```

**What it does:**
- Detects and converts XPOS format (LLCT, ITTB, PROIEL → Perseus)
- Validates XPOS positions against UPOS
- Filters invalid features for the given UPOS
- Reconciles with reference features (ref_features)
- Returns tuple of (normalized_xpos, validated_features)

## Validation

Validate morphological annotations at the value level.

### Validate Features

Filter features to only those valid for a given UPOS:

```python
from nlp_utilities.loaders import load_language_data
from nlp_utilities.validators import validate_features

feature_set = load_language_data('feats', language='la')

# Mood is invalid for NOUN - will be filtered out
validated = validate_features(
    upos='NOUN',
    feats='Case=Nom|Gender=Fem|Number=Sing|Mood=Ind',
    feature_set=feature_set
)

print(validated)
# Output: {'Case': 'Nom', 'Gender': 'Fem', 'Number': 'Sing'}
# Note: Mood=Ind removed (not valid for NOUN)
```

### Validate XPOS

Ensure XPOS positions are valid for the given UPOS:

```python
from nlp_utilities.validators import validate_xpos

# First character wrong for NOUN (should be 'n', not 'a')
validated = validate_xpos(upos='NOUN', xpos='a-s---fn-')
print(validated)
# Output: 'n-s---fn-' (first character corrected)

# Position 2 is only valid for verbs - will be removed
validated = validate_xpos(upos='NOUN', xpos='n1s---mn-')
print(validated)
# Output: 'n-s---mn-' (position 2 cleared)
```

**Use cases:**
- `validate_features()` and `validate_xpos()` are used internally by `normalize_morphology()`
- Can be used standalone for validation-only tasks
- Useful for checking annotations before file-level validation

## Next Steps

Now that you’ve seen the basics, dive deeper:

**User Guides**

- [brat Conversion](user_guide/brat_conversion.md) - Complete brat conversion guide
- [Validation](user_guide/validation.md) - Comprehensive validation guide
- [Evaluation](user_guide/evaluation.md) - Detailed evaluation metrics
- [Converters](user_guide/converters.md) - Tagset conversion guide
- [Normalization](user_guide/normalization.md) - Normalization workflows

**API Reference**

- {doc}`api_reference/brat` - brat conversion API
- {doc}`api_reference/conllu` - Validators and evaluators
- {doc}`api_reference/converters` - Converter functions
- {doc}`api_reference/loaders` - Data loading utilities
- {doc}`api_reference/normalizers` - Normalization functions

## Need Help?

- **Issues**: [https://github.com/gpizzorno/latin-nlp-utilities/issues](https://github.com/gpizzorno/latin-nlp-utilities/issues)
- **Documentation**: Use the search bar in these docs
- **Examples**: Check the test files for more usage examples
