# Latin NLP Utilities

[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://www.python.org)
[![Tests](https://github.com/gpizzorno/latin-nlp-utilities/actions/workflows/tests.yml/badge.svg)](https://github.com/gpizzorno/latin-nlp-utilities/actions/workflows/tests.yml)
[![Documentation](https://img.shields.io/badge/Docs-latest-blue.svg)](https://gpizzorno.github.io/latin-nlp-utilities/)

**Latin NLP Utilities** is a set of convenience tools for working with Latin treebanks and annotated corpora. It provides converters, evaluation scripts, validation tools, and utilities for transforming, validating, and comparing Latin linguistic data in [CoNLL-U](https://universaldependencies.org/format.html) and [brat](https://brat.nlplab.org) standoff formats.

[Read the documentation](https://gpizzorno.github.io/latin-nlp-utilities/)

## Features

- **brat/CoNLL-U Interoperability**: Convert between brat [standoff](https://brat.nlplab.org/standoff.html) and [CoNLL-U](https://universaldependencies.org/format.html)
- **Morphological Feature Utilities**: Normalize and map features across tagsets ([Perseus](https://universaldependencies.org/treebanks/la_perseus/index.html), [ITTB](https://universaldependencies.org/treebanks/la_ittb/index.html), [PROIEL](https://universaldependencies.org/treebanks/la_proiel/index.html), [DALME](https://dalme.org))
- **Validation**: Check CoNLL-U files for format and annotation guideline compliance
- **Evaluation**: Score system outputs against gold-standard CoNLL-U files, including enhanced dependencies
- **Extensible**: Easily add new tagset converters or feature mappings

For detailed information about each feature, see the [User Guide](https://gpizzorno.github.io/latin-nlp-utilities/user_guide/index.html).

## Installation

### Quick Install

```sh
pip install latin-nlp-utilities
```

For detailed installation instructions, including platform-specific guidance and troubleshooting, see the [Installation Guide](https://gpizzorno.github.io/latin-nlp-utilities/installation.html).

## Quick Start

### Convert CoNLL-U to brat

```python
from nlp_utilities.brat import conllu_to_brat

conllu_to_brat(
    conllu_filename='path/to/conllu/yourfile.conllu',
    output_directory='path/to/brat/files',
    sents_per_doc=10,
    output_root=True,
)

# Outputs .ann and .txt files to 'path/to/brat/files', alongside
# annotation.conf, tools.conf, visual.conf, and metadata.json

```

### Convert brat to CoNLL-U

```python
from nlp_utilities.brat import brat_to_conllu
from nlp_utilities.loaders import load_language_data

feature_set = load_language_data('feats', language='la')
brat_to_conllu(
    input_directory='path/to/brat/files',
    output_directory='path/to/conllu',
    ref_conllu='yourfile.conllu',
    feature_set=feature_set,
    output_root=True
)

# Outputs yourfile-from_brat.conllu to 'path/to/conllu'
```

### Validate CoNLL-U Files

```python
from nlp_utilities.conllu import ConlluValidator

validator = ConlluValidator(lang='la', level=2)
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

### Evaluate CoNLL-U Files

```python
from nlp_utilities.conllu import ConlluEvaluator

evaluator = ConlluEvaluator(eval_deprels=True, treebank_type='0')
scores = evaluator.evaluate_files(
    gold_path='path/to/gold_standard.conllu',
    system_path='path/to/system_output.conllu',
)

print(f'UAS: {scores["UAS"].f1:.2%}')
print(f'LAS: {scores["LAS"].f1:.2%}')

# Example output:
# UAS: 64.82%
# LAS: 48.16%
```

### Convert Between Tagsets

```python
from nlp_utilities.converters.upos import dalme_to_upos, upos_to_perseus
from nlp_utilities.converters.xpos import ittb_to_perseus, llct_to_perseus
from nlp_utilities.converters.features import feature_string_to_dict, feature_dict_to_string

print(dalme_to_upos('adjective'))
# Returns 'ADJ'

print(upos_to_perseus('NOUN'))
# Returns 'n'

print(ittb_to_perseus('VERB', 'gen4|tem1|mod1'))  
# Returns 'v1sp-----'

print(llct_to_perseus('VERB', 'v|v|3|s|p|i|a|-|-|-', 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act'))
# Returns 'v3spia---'

feat_dict = feature_string_to_dict('Case=Nom|Gender=Neut|Number=Sing')
# Returns a dictionary: 
{'Case': 'Nom', 'Gender': 'Neut', 'Number': 'Sing'}

print(feature_dict_to_string(feat_dict)) 
# Returns 'Case=Nom|Gender=Neut|Number=Sing'
```

### Normalize Morphology

```python
from nlp_utilities.loaders import load_language_data
from nlp_utilities.normalizers import normalize_morphology

feature_set = load_language_data('feats', language='la')

# Normalize morphology with feature reconciliation
# VerbForm is missing from feats but present in ref_feats
xpos, feats = normalize_morphology(
    upos='VERB',
    xpos='v-s-ga-g-',
    feats='Aspect=Perf|Case=Gen|Degree=Pos|Number=Sing|Voice=Act',
    feature_set=feature_set,
    ref_features='Aspect=Perf|Case=Gen|Degree=Pos|Number=Sing|VerbForm=Ger|Voice=Act'
)

print(xpos)
# Returns 'v-stga-g-' (normalized and validated)

print(feats)
# Returns {'Aspect': 'Perf', 'Case': 'Gen', 'Degree': 'Pos', 'Number': 'Sing', 'VerbForm': 'Ger', 'Voice': 'Act'}
```

For more examples and detailed usage, see the [Quickstart Guide](https://gpizzorno.github.io/latin-nlp-utilities/quickstart.html).

## Documentation

The full documentation includes:

- **[Installation Guide](https://gpizzorno.github.io/latin-nlp-utilities/installation.html)**: Detailed installation instructions and troubleshooting
- **[Quickstart Guide](https://gpizzorno.github.io/latin-nlp-utilities/quickstart.html)**: Get started quickly with common tasks
- **[User Guide](https://gpizzorno.github.io/latin-nlp-utilities/user_guide/index.html)**: Comprehensive guides for all features
  - [brat Conversion](https://gpizzorno.github.io/latin-nlp-utilities/user_guide/brat_conversion.html): CoNLL-U ↔ brat conversion
  - [Validation](https://gpizzorno.github.io/latin-nlp-utilities/user_guide/validation.html): Validation framework and recipes
  - [Evaluation](https://gpizzorno.github.io/latin-nlp-utilities/user_guide/evaluation.html): Metrics and evaluation workflows
  - [Converters](https://gpizzorno.github.io/latin-nlp-utilities/user_guide/converters.html): Tagset conversions
  - [Normalization](https://gpizzorno.github.io/latin-nlp-utilities/user_guide/normalization.html): Feature normalization
- **[API Reference](https://gpizzorno.github.io/latin-nlp-utilities/api_reference/index.html)**: Complete API documentation
- **[Developer Guide](https://gpizzorno.github.io/latin-nlp-utilities/developer_guide/index.html)**: Architecture and testing guides for contributors


## Acknowledgments

This toolkit builds upon and extends code from several sources:

- CoNLL-U/brat conversion logic is based on the [tools](https://github.com/nlplab/brat/tree/master/tools) made available by the [brat team](https://brat.nlplab.org/about.html).
- CoNLL-U evaluation is based on the work of Milan Straka and Martin Popel for the [CoNLL 2018 UD shared task](https://universaldependencies.org/conll18/), and Gosse Bouma for the [IWPT 2020 shared task](https://universaldependencies.org/iwpt20/task_and_evaluation.html).
- CoNLL-U validation is based on [work](https://github.com/UniversalDependencies/tools/blob/b3925718ba7205976d80eda7628687218474b541/validate.py) by Filip Ginter and Sampo Pyysalo.

## License

The project is licensed under the [MIT License](LICENSE), allowing free use, modification, and distribution.
