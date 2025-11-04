# Latin NLP Utilities

[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://www.python.org)
[![Tests](https://github.com/gpizzorno/latin-nlp-utilities/actions/workflows/tests.yml/badge.svg)](https://github.com/gpizzorno/latin-nlp-utilities/actions/workflows/tests.yml)

**Latin NLP Utilities** is a set of convenience tools for working with Latin treebanks and annotated corpora. It provides converters, evaluation scripts, validation tools, and utilities for transforming, validating, and comparing Latin linguistic data in CoNLL-U and [Brat](https://brat.nlplab.org/manual.html) standoff formats.

## Features

- **Brat/CoNLL-U Interoperability**: Convert between Brat [standoff](https://brat.nlplab.org/standoff.html) and [CoNLL-U](https://universaldependencies.org/format.html), including support for [IOB-tagged](https://en.wikipedia.org/wiki/Inside–outside–beginning_(tagging)) data
- **Morphological Feature Normalization**: Normalize and map features across tagsets ([Perseus](https://universaldependencies.org/treebanks/la_perseus/index.html), [ITTB](https://universaldependencies.org/treebanks/la_ittb/index.html), [PROIEL](https://universaldependencies.org/treebanks/la_proiel/index.html), [DALME](https://dalme.org))
- **Validation**: Check CoNLL-U files for format and annotation guideline compliance
- **Evaluation**: Score system outputs against gold-standard CoNLL-U files, including enhanced dependencies
- **Extensible**: Easily add new tagset converters or feature mappings

## Installation

Clone the repository and install the dependencies via:

```sh
pip install -r requirements.txt
```

## Tools and Usage

### 1. **Brat ↔ CoNLL-U Conversion**

#### **Convert Brat standoff to CoNLL-U**

Convert Brat annotation files (`.ann` and `.txt`) to CoNLL-U format with dependency parsing and morphological feature alignment.

```python
from latin_utilities import brat_to_conllu

brat_to_conllu(
    input_dir='path/to/brat/files',           # Directory containing .ann and .txt files
    conllu_dir='path/to/output',              # Output directory for .conllu files
    lang='la',                                # Language code (e.g., 'la' for Latin)
    additional_features='extra_feats.json',   # Optional: path to extra features JSON
    reference_corpus_path='reference.conllu'  # Optional: reference corpus for morphology
)
```

**Features:**
- Handles discontinuous spans (e.g., `T1 NOUN 0 3;5 8 foo bar`)
- Automatically renumbers conflicting IDs when joining multiple files
- Maps Brat relations to CoNLL-U HEAD/DEPREL columns
- Supports enhanced dependencies in DEPS column
- Automatically corrects UPOS tags (e.g., `aux` relations trigger `VERB` → `AUX`)
- Generates sentence concordance mapping between Brat and CoNLL-U

**Input:** 
- Brat `.ann` files with textbound annotations and relations
- Corresponding `.txt` files with raw text
- Base CoNLL-U file for morphological information

**Output:**
- CoNLL-U format file with dependency structure
- JSON concordance file mapping sentence IDs

#### **Convert CoNLL-U to Brat standoff**

Convert CoNLL-U dependency treebanks to Brat standoff format for annotation.

```python
from latin_utilities import conllu_to_brat

conllu_to_brat(
    filename='input.conllu',                 # Path to input .conllu file
    output_directory='output/dir',           # Output directory for .ann and .txt files
    sents_per_doc=5,                         # Optional: split into docs of N sentences
    output_root=True                         # Optional: add explicit ROOT node
)
```

**Features:**
- Splits long documents into smaller annotation files
- Creates explicit ROOT nodes for dependency visualization
- Handles multiword tokens correctly
- Generates both `.ann` (annotations) and `.txt` (text) files

#### **Convert CoNLL-U with IOB tags to Brat**

Convert CoNLL-U files containing IOB (Inside-Outside-Begin) named entity tags to Brat format.

```python
from latin_utilities import conllubio_to_brat

conllubio_to_brat(
    filename='tagged_input.conllu',          # Path to input .conllu file with IOB tags
    output_directory='output/dir'            # Output directory for .ann and .txt files
)
```

**Features:**
- Parses IOB/BIO tags from MISC column
- Creates entity spans for consecutive B-I tag sequences
- Handles quote characters and spacing correctly
- Supports document boundaries with special markers


### 2. **Evaluation**

#### **Evaluate CoNLL-U Files**

Comprehensive evaluation of system output against gold standard using [Universal Dependencies](https://universaldependencies.org/format.html) metrics.

```python
from latin_utilities import evaluate_ud_files

scores = evaluate_ud_files(
    gold_path='gold_standard.conllu',        # Path to gold-standard .conllu file
    system_path='system_output.conllu',      # Path to system output .conllu file
    tb_type='0',                             # Treebank enhancement flags (see below)
    eval_deprels=True                        # Evaluate dependency relations (default: True)
)

# Print results
for metric, score in scores.items():
    print(f'{metric}: P={score.precision:.3f} R={score.recall:.3f} F1={score.f1:.3f}')
```

**Treebank Types (tb_type parameter):**
- `'0'`: Evaluate all enhancement types
- `'1'`: No gapping
- `'2'`: No coordination shared parents
- `'3'`: No coordination shared dependents  
- `'4'`: No xsubj (control verbs)
- `'5'`: No relative clauses
- `'6'`: No case info in deprels
- Values can be combined: `'12'` = both 1 and 2

**Metrics Returned:**
- **Tokens**: Token boundary detection
- **Sentences**: Sentence boundary detection
- **Words**: Word alignment accuracy
- **UPOS**: Universal POS tag accuracy
- **XPOS**: Language-specific POS tag accuracy
- **UFeats**: Universal morphological features accuracy
- **AllTags**: Combined UPOS+XPOS+FEATS accuracy
- **Lemmas**: Lemma accuracy
- **UAS**: Unlabeled Attachment Score (syntax heads)
- **LAS**: Labeled Attachment Score (heads + relations)
- **CLAS**: Content-word Labeled Attachment Score
- **MLAS**: Morphology-aware Labeled Attachment Score
- **BLEX**: Bilexical dependency accuracy
- **ELAS**: Enhanced Labeled Attachment Score
- **EULAS**: Enhanced Unlabeled Attachment Score


### 3. **Validation**

#### **Validate CoNLL-U Files**

Comprehensive validation of CoNLL-U files against [Universal Dependencies](https://universaldependencies.org/format.html) guidelines.

```python
from latin_utilities import validate_conllu

with open('yourfile.conllu', encoding='utf-8') as f:
    validate_conllu(
        f,                                   # File handle
        lang='la',                           # Language code
        level=2,                             # Validation level (1-5)
        add_features='extra_features.json'   # Optional: additional feature definitions
    )
```

**Validation Levels:**
- **Level 1**: Basic CoNLL-U format validation
- **Level 2**: Universal Dependencies structural validation
- **Level 3**: UD annotation guideline compliance
- **Level 4**: Language-specific formal validation
- **Level 5**: Language-specific annotation guidelines

**Checks Performed:**
- Column count and format
- ID sequence validity
- Unicode normalization (NFC)
- HEAD/DEPREL consistency
- Feature format and values
- Dependency tree structure
- Projectivity and non-projectivity
- Enhanced dependency validity


### 4. **Tagset Conversion Utilities**

#### **DALME POS → Universal POS**

Convert [DALME](https://dalme.org) Part-of-Speech (POS) tags to [Universal Dependencies PoS](https://universaldependencies.org/u/pos/index.html).

```python
from latin_utilities.converters import dalmepos_to_upos

upos = dalmepos_to_upos('adjective')                # Returns 'ADJ'
upos = dalmepos_to_upos('coordinating conjunction') # Returns 'CCONJ'
upos = dalmepos_to_upos('unknown_tag')              # Returns 'X'
```

#### **Universal POS → Perseus Extended Part-of-Speech**

Convert Universal POS tags to [Perseus Extended Part-of-Speech format](https://github.com/PerseusDL/treebank_data/blob/master/v2.1/Latin/TAGSET.txt).

```python
from latin_utilities.converters import upos_to_perseus

perseus_tag = upos_to_perseus('NOUN')        # Returns 'n'
perseus_tag = upos_to_perseus('VERB')        # Returns 'v'
perseus_tag = upos_to_perseus('ADJ')         # Returns 'a'
```

#### **ITTB/PROIEL → Perseus Morphological Features**

Convert morphological features from [ITTB](https://github.com/UniversalDependencies/UD_Latin-ITTB/tree/master) (Index Thomisticus Treebank) or [PROIEL](https://github.com/UniversalDependencies/UD_Latin-PROIEL/tree/master) format to Perseus positional tags.

```python
# ITTB converters
from latin_utilities.converters.ittb_to_perseus import (
    gen_to_person, cas_to_case, tem_to_tense, mod_to_mood, mod_to_voice
)

person = gen_to_person('4')                  # Returns '1' (first person)
case = cas_to_case('A')                      # Returns 'n' (nominative)
tense = tem_to_tense('1')                    # Returns 'p' (present)
mood = mod_to_mood('A')                      # Returns 'i' (indicative)
voice = mod_to_voice('A')                    # Returns 'a' (active)

# PROIEL converters  
from latin_utilities.converters.proiel_to_perseus import (
    to_number, to_tense, to_mood, to_voice, to_gender, to_case, to_degree
)

number = to_number('Sing')                   # Returns 's' (singular)
tense = to_tense('Pres')                     # Returns 'p' (present)
mood = to_mood('Ind')                        # Returns 'i' (indicative)
voice = to_voice('Act')                      # Returns 'a' (active)
gender = to_gender('Masc')                   # Returns 'm' (masculine)
case = to_case('Nom')                        # Returns 'n' (nominative)
degree = to_degree('Pos')                    # Returns 'p' (positive)
```

### 5. **Feature Normalization and Utilities**

#### **Feature String/Dictionary Conversion**

Convert between string and dictionary representations of morphological features.

```python
from latin_utilities import feature_string_to_dict, feature_dict_to_string

# String to dictionary
d = feature_string_to_dict('Case=Nom|Gender=Masc|Number=Sing')
# Returns: {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}

# Dictionary to string
s = feature_dict_to_string({'Case': 'Nom', 'Gender': 'Masc'})
# Returns: 'Case=Nom|Gender=Masc'

# Empty/null features
empty_dict = feature_string_to_dict('_')     # Returns: {}
empty_str = feature_dict_to_string({})       # Returns: '_'
```

#### **Normalize Features**

Normalize morphological features based on UPOS tag and language-specific feature set.

```python
from latin_utilities import normalize_features, load_lang_features

# Load feature definitions
featset = load_lang_features('la', 'additional_features.json')

# Normalize features
normalized = normalize_features(
    'NOUN',                                  # UPOS tag
    {'Case': 'Nom', 'InvalidFeature': 'X'},  # Feature dictionary
    featset                                  # Feature set definition
)
# Returns only valid features for the given UPOS: {'Case': 'Nom'}
```

#### **Normalize Extended Part-of-Speech**

Normalize language-specific POS tags to Perseus format based on UPOS.

```python
from latin_utilities import normalize_xpos

# Normalize Perseus-style XPOS tag
norm_xpos = normalize_xpos('NOUN', 'n-s---mn-')
# Returns normalized Perseus tag with '-' for invalid positions

# Convert UPOS to basic Perseus tag
norm_xpos = normalize_xpos('VERB', 'irregular_tag')
# Returns 'v--------' (verb with empty morphology)
```

## Testing

Run the full test suite:

```sh
pytest --cov=latin_utilities
```

Run specific test modules:

```sh
pytest latin_utilities/tests/test_brat2conllu.py -v
pytest latin_utilities/tests/test_evaluate_conllu.py -v
```


## Acknowledgments

This toolkit builds upon and extends code from several sources:

- CoNLL-U/Brat conversion logic is based on the [tools](https://github.com/nlplab/brat/tree/master/tools) made available by the [Brat team](https://brat.nlplab.org/about.html).
- CoNLL-U evaluation is based on the work of Milan Straka and Martin Popel for the [CoNLL 2018 UD shared task](https://universaldependencies.org/conll18/), and Gosse Bouma for the [IWPT 2020 shared task](https://universaldependencies.org/iwpt20/task_and_evaluation.html).
- CoNLL-U validation is based on [work](https://github.com/UniversalDependencies/tools/blob/b3925718ba7205976d80eda7628687218474b541/validate.py) by Filip Ginter and Sampo Pyysalo.

## License

The project is licensed under the [MIT License](LICENSE), allowing free use, modification, and distribution.
