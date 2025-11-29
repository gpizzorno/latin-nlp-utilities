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

Validate CoNLL-U files for format and linguistic correctness:

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

Evaluate parser output against gold standard:

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
```

## Pattern Matching

Find linguistic patterns in your CoNLL-U corpus.

### Basic Pattern Search

```python
import conllu
from conllu_tools.matching import build_pattern, find_in_corpus

# Load corpus
with open('corpus.conllu', encoding='utf-8') as f:
    corpus = conllu.parse(f.read())

# Find all adjective + noun sequences
pattern = build_pattern('ADJ+NOUN', name='adj-noun')
matches = find_in_corpus(corpus, [pattern])

for match in matches:
    print(f"[{match.sentence_id}] {match.substring}")
    print(f"  Forms: {match.forms}")
    print(f"  Lemmata: {match.lemmata}")
```

### Pattern Syntax Examples

```python
# Match by UPOS
build_pattern('NOUN')              # Any noun
build_pattern('NOUN|VERB')         # Noun or verb
build_pattern('*')                 # Any token

# Match with conditions
build_pattern('NOUN:lemma=rex')                    # Noun with lemma 'rex'
build_pattern('NOUN:feats=(Case=Abl)')             # Ablative noun
build_pattern('NOUN:feats=(Case=Nom,Number=Sing)') # Singular nominative

# Multi-token sequences
build_pattern('DET+NOUN')                  # Determiner + noun
build_pattern('ADP+NOUN:feats=(Case=Acc)') # Preposition + accusative noun
build_pattern('DET+ADJ{0,2}+NOUN')         # Det + 0-2 adjectives + noun

# Negation and substring matching
build_pattern('!PUNCT')              # Not punctuation
build_pattern('*:form=<ae>')         # Form contains 'ae'
build_pattern('NOUN:form=um>')       # Noun ending in 'um'
```


## Utils

Utilities for tagset conversion, morphology normalization, and feature validation.

### Normalize Morphology

The main utility function for harmonizing morphological annotations:

```python
from conllu_tools.io import load_language_data
from conllu_tools.utils import normalize_morphology

feature_set = load_language_data('feats', language='la')

xpos, feats = normalize_morphology(
    upos='VERB',
    xpos='v|v|3|s|p|i|a|-|-|-',  # LLCT format (auto-detected)
    feats='Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act',
    feature_set=feature_set,
)

print(xpos)   # 'v3spia---' (converted to Perseus format)
print(feats)  # {'Mood': 'Ind', 'Number': 'Sing', 'Person': '3', ...}
```

**What it does:** Auto-detects XPOS format (LLCT, ITTB, PROIEL) → converts to Perseus → validates against UPOS → reconciles features.

### Feature Conversion

```python
from conllu_tools.utils import feature_string_to_dict, feature_dict_to_string

# String ↔ dictionary conversion
feat_dict = feature_string_to_dict("Case=Nom|Gender=Masc|Number=Sing")
# {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}

feat_str = feature_dict_to_string({'Number': 'Sing', 'Case': 'Gen'})
# 'Case=Gen|Number=Sing' (sorted alphabetically)
```

### XPOS Conversion

```python
from conllu_tools.utils import format_xpos, upos_to_perseus

# Convert UPOS to Perseus code
upos_to_perseus('NOUN')  # 'n'

# Auto-detect and convert any XPOS format to Perseus
format_xpos('VERB', 'v|v|3|s|p|i|a|-|-|-', feats)  # LLCT → 'v3spia---'
format_xpos('NOUN', 'gen2|casA', feats)             # ITTB → 'n-s---fn-'
format_xpos('NOUN', 'Nb', feats)                    # PROIEL → 'n-s---na-'
```


## Next Steps

Now that you’ve seen the basics, dive deeper:

**User Guides**

- {doc}`user_guide/conversion` - Detailed conversion workflows
- {doc}`user_guide/validation` - Comprehensive validation guide
- {doc}`user_guide/evaluation` - Advanced evaluation metrics
- {doc}`user_guide/matching` - Pattern matching patterns
- {doc}`user_guide/utils` - Utility functions guide

**Examples**

- {doc}`examples/io` - I/O examples
- {doc}`examples/validation` - Validation examples
- {doc}`examples/evaluation` - Evaluation examples
- {doc}`examples/normalization` - Normalization examples

**API Reference**

- {doc}`api_reference/io` - I/O and conversion API
- {doc}`api_reference/validation` - Validation API
- {doc}`api_reference/evaluation` - Evaluation API
- {doc}`api_reference/matching` - Pattern matching API
- {doc}`api_reference/utils` - Utility functions API
- {doc}`api_reference/constants` - Package constants

## Need Help?

- **Issues**: [https://github.com/gpizzorno/conllu_tools/issues](https://github.com/gpizzorno/conllu_tools/issues)
- **Documentation**: Use the search bar in these docs
- **More examples**: Check the test files for more usage examples
