# CoNLL-U Tools

[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://www.python.org)
[![Tests](https://github.com/gpizzorno/conllu_tools/actions/workflows/tests.yml/badge.svg)](https://github.com/gpizzorno/conllu_tools/actions/workflows/tests.yml)
[![Documentation](https://img.shields.io/badge/Docs-latest-blue.svg)](https://gpizzorno.github.io/conllu_tools/)

**CoNLL-U Tools** is a Python toolkit for working with CoNLL-U files, Universal Dependencies treebanks, and annotated corpora. It provides utilities for format conversion, validation, evaluation, pattern matching, and morphological normalization, supporting workflows with [CoNLL-U](https://universaldependencies.org/format.html) and [brat](https://brat.nlplab.org) standoff formats.

[Read the documentation](https://gpizzorno.github.io/conllu_tools/)

## Features

- **Format Conversion**: Bidirectional conversion between brat [standoff](https://brat.nlplab.org/standoff.html) and [CoNLL-U](https://universaldependencies.org/format.html) formats
- **Validation**: Check CoNLL-U files for format compliance and annotation guideline adherence
- **Evaluation**: Score parser outputs against gold-standard files with comprehensive metrics
- **Pattern Matching**: Find tokens and sentences matching complex linguistic criteria
- **Morphological Utilities**: Normalize features, convert between tagsets ([Perseus](https://universaldependencies.org/treebanks/la_perseus/index.html), [ITTB](https://universaldependencies.org/treebanks/la_ittb/index.html), [PROIEL](https://universaldependencies.org/treebanks/la_proiel/index.html), [LLCT](https://universaldependencies.org/treebanks/la_llct/index.html))
- **Extensible**: Add custom tagset converters and feature mappings

For detailed information about each feature, see the [User Guide](https://gpizzorno.github.io/conllu_tools/user_guide/index.html).

## Installation

### Quick Install

```sh
pip install conllu_tools
```

For detailed installation instructions, including platform-specific guidance and troubleshooting, see the [Installation Guide](https://gpizzorno.github.io/conllu_tools/installation.html).

## Quick Start

### Convert CoNLL-U to brat

```python
from conllu_tools.io import conllu_to_brat

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
from conllu_tools.io import brat_to_conllu
from conllu_tools.io import load_language_data

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
from conllu_tools import ConlluValidator

validator = ConlluValidator(lang='la', level=2)
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

### Evaluate CoNLL-U Files

```python
from conllu_tools import ConlluEvaluator

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

### Pattern Matching

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

# More pattern examples:
build_pattern('NOUN:lemma=rex')                    # Noun with lemma 'rex'
build_pattern('NOUN:feats=(Case=Abl)')             # Ablative noun
build_pattern('DET+ADJ{0,2}+NOUN')                 # Det + 0-2 adjectives + noun
build_pattern('ADP+NOUN:feats=(Case=Acc)')         # Preposition + accusative noun
```

For more examples and detailed usage, see the [Quickstart Guide](https://gpizzorno.github.io/conllu_tools/quickstart.html).

## Documentation

The full documentation includes:

- **[Installation Guide](https://gpizzorno.github.io/conllu_tools/installation.html)**: Detailed installation instructions and troubleshooting
- **[Quickstart Guide](https://gpizzorno.github.io/conllu_tools/quickstart.html)**: Get started quickly with common tasks
- **[User Guide](https://gpizzorno.github.io/conllu_tools/user_guide/index.html)**: Comprehensive guides for all features
  - [Conversion](https://gpizzorno.github.io/conllu_tools/user_guide/conversion.html): CoNLL-U ↔ brat conversion
  - [Validation](https://gpizzorno.github.io/conllu_tools/user_guide/validation.html): Validation framework and recipes
  - [Evaluation](https://gpizzorno.github.io/conllu_tools/user_guide/evaluation.html): Metrics and evaluation workflows
  - [Pattern Matching](https://gpizzorno.github.io/conllu_tools/user_guide/matching.html): Find complex linguistic patterns
  - [Utilities](https://gpizzorno.github.io/conllu_tools/user_guide/utils.html): Tagset conversion and normalization
- **[API Reference](https://gpizzorno.github.io/conllu_tools/api_reference/index.html)**: Complete API documentation


## Acknowledgments

This toolkit builds upon and extends code from several sources:

- CoNLL-U/brat conversion logic is based on the [tools](https://github.com/nlplab/brat/tree/master/tools) made available by the [brat team](https://brat.nlplab.org/about.html).
- CoNLL-U evaluation is based on the work of Milan Straka and Martin Popel for the [CoNLL 2018 UD shared task](https://universaldependencies.org/conll18/), and Gosse Bouma for the [IWPT 2020 shared task](https://universaldependencies.org/iwpt20/task_and_evaluation.html).
- CoNLL-U validation is based on [work](https://github.com/UniversalDependencies/tools/blob/b3925718ba7205976d80eda7628687218474b541/validate.py) by Filip Ginter and Sampo Pyysalo.

## License

The project is licensed under the [MIT License](LICENSE), allowing free use, modification, and distribution.
