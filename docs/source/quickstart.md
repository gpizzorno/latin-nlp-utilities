(quickstart)=
# Quick Start Guide

This guide will get you up and running with CoNLL-U Tools in minutes.

## Installation

First, install the package:

```bash
pip install conllu_tools
```

Verify the installation:

```bash
python -c "import conllu_tools; print('Ready to go!')"
```

## Conversion

Let’s convert a CoNLL-U file to brat format for visual annotation.

### CoNLL-U to brat

```python
from conllu_tools.io import conllu_to_brat

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
from conllu_tools.io import brat_to_conllu
from conllu_tools.io import load_language_data

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

## Validation

Validate CoNLL-U files for format and linguistic correctness.

### Basic Validation

```python
from conllu_tools import ConlluValidator

# Create validator
validator = ConlluValidator(lang='la', level=2)

# Run validation checks
reporter = validator.validate_file('path/to/yourfile.conllu')

# Print error count
print(f'Errors found: {reporter.get_error_count()}')

# Inspect first error
sent_id, order, testlevel, error = reporter.errors[0]
print(f'Sentence ID: {sent_id}')  # e.g. 34
print(f'Testing at level: {testlevel}')  # e.g. 2
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

## Evaluation

Evaluate parser output against gold standard.

### Basic Evaluation

```python
from conllu_tools import ConlluEvaluator

# Compare gold standard with system output
evaluator = ConlluEvaluator(eval_deprels=True, treebank_type='0')
scores = evaluator.evaluate_files(
    gold_path='path/to/gold_standard.conllu',
    system_path='path/to/parser_output.conllu',
)

# Print scores
print(f"Unlabeled Attachment Score (UAS): {scores['UAS']:.2f}%")
print(f"Labeled Attachment Score (LAS): {scores['LAS']:.2f}%")
print(f"UPOS Accuracy: {scores['UPOS']:.2f}%")
```

## Pattern Matching

[ADD CONTENT]


## Utils

[ADD INTRO]

### Normalize Morphology

Normalize XPOS and FEATS together with automatic format detection and validation:

```python
from conllu_tools.io import load_language_data
from conllu_tools.utils.normalization import normalize_morphology

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

Convert between different tagsets.

### XPOS Conversion

Standardize XPOS tags from different treebanks:

```python
from conllu_tools.utils.upos import dalme_to_upos, upos_to_perseus
from conllu_tools.utils.xpos import ittb_to_perseus, llct_to_perseus

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
from conllu_tools.utils.features import feature_string_to_dict, feature_dict_to_string

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


## Next Steps

Now that you’ve seen the basics, dive deeper:

**User Guides**

- [Conversion](user_guide/brat_conversion.md) - Conversion guide
- [Validation](user_guide/validation.md) - Validation guide
- [Evaluation](user_guide/evaluation.md) - Detailed evaluation metrics
- [Matching](user_guide/matching.md) - Pattern matching guide
- [Utils](user_guide/utils.md) - Utils guide

**Examples**

- [Input/Output](examples/io.md)
- [Validation](examples/validation.md)
- [Evaluation](examples/evaluation.md)
- [Normalization](examples/normalization.md)

**API Reference**

- {doc}`api_reference/io` - Input/Output/Conversion API
- {doc}`api_reference/validation` - Validation API
- {doc}`api_reference/evaluation` - Evaluation API
- {doc}`api_reference/matching` - Pattern matching API
- {doc}`api_reference/utils` - Utils functions

## Need Help?

- **Issues**: [https://github.com/gpizzorno/conllu_tools/issues](https://github.com/gpizzorno/conllu_tools/issues)
- **Documentation**: Use the search bar in these docs
- **More examples**: Check the test files for more usage examples
