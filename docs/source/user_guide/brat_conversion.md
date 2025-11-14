# Brat Conversion

This guide covers converting between Brat standoff annotation format and CoNLL-U format.

## Overview

Brat is a web-based annotation tool that uses standoff format (separate `.ann` and `.txt` files).
CoNLL-U is a tabular format for representing linguistic annotations, especially dependency trees.

The conversion utilities allow you to:

- Convert CoNLL-U treebanks to Brat format for annotation/review
- Convert Brat annotations back to CoNLL-U format
- Handle enhanced dependencies and complex structures
- Preserve morphological features and metadata

## CoNLL-U to Brat

Converting CoNLL-U files to Brat standoff format enables visual annotation and review using the Brat tool.

### Basic Usage

```python
from nlp_utilities.brat import conllu_to_brat

conllu_to_brat(
    conllu_filename='input.conllu',
    output_directory='brat_output/',
    output_root=True,
    sents_per_doc=10
)
```

This creates:

- `.txt` files containing the raw text
- `.ann` files containing the annotations in Brat standoff format
- Configuration files (`annotation.conf`, `visual.conf`, `tools.conf`)

### Parameters

**conllu_filename** (str)
: Path to the input CoNLL-U file.

**output_directory** (str)
: Directory where Brat files will be created.

**output_root** (bool, optional)
: If `True`, creates explicit ROOT nodes for sentence roots. This makes the dependency
  structure more visible in Brat. Default: `False`.

**sents_per_doc** (int, optional)
: Number of sentences per output document. If specified, long files are split into
  multiple documents (e.g., `doc-001`, `doc-002`). If `None`, all sentences
  go into one document. Default: `None`.

### Output Structure

The output directory will contain:

```text
brat_output/
├── annotation.conf    # Defines annotation types
├── visual.conf        # Visual styling
├── tools.conf         # Tool configuration
├── metadata.json      # Conversion metadata
├── input-doc-001.txt  # Text for document 1
├── input-doc-001.ann  # Annotations for document 1
├── input-doc-002.txt
└── input-doc-002.ann
```

### Features

- **Multiword tokens**: Correctly handles multi-word tokens
- **ROOT nodes**: Optional explicit ROOT entity for dependency visualization
- **Metadata preservation**: Stores original CoNLL-U metadata
- **Automatic splitting**: Can split large files into manageable documents

## Brat to CoNLL-U

Converting Brat annotations back to CoNLL-U format after manual annotation or review.

### Basic Usage

```python
from nlp_utilities.brat import brat_to_conllu
from nlp_utilities.loaders import load_language_data

# Load feature set for validation
feature_set = load_language_data('la')

brat_to_conllu(
    input_directory='brat_output/',
    output_directory='conllu_output/',
    ref_conllu='original.conllu',
    feature_set=feature_set,
    output_root=True,
    sents_per_doc=10
)
```

### Parameters

**input_directory** (str)
: Directory containing Brat `.ann` and `.txt` files.

**output_directory** (str)
: Directory where the output CoNLL-U file will be created.

**ref_conllu** (str)
: Path to a reference CoNLL-U file. This provides morphological features and
  other information not captured in Brat annotations.

**feature_set** (dict)
: Feature set definition loaded from {func}`nlp_utilities.loaders.load_language_data`.
  Used to validate and normalize features.

**output_root** (bool, optional)
: Must match the value used when creating the Brat files. Default: `False`.

**sents_per_doc** (int, optional)
: Must match the value used when creating the Brat files. Default: `None`.

### Features

- **Morphology from reference**: Retrieves LEMMA, XPOS, FEATS from reference file
- **Dependency from Brat**: Uses HEAD and DEPREL from Brat annotations
- **Enhanced dependencies**: Supports enhanced dependency graphs
- **ID renumbering**: Handles ID conflicts when merging multiple files
- **Automatic UPOS correction**: Changes VERB→AUX for auxiliary verbs based on deprel

## Round-trip Conversion

For a complete workflow where you start with CoNLL-U, annotate in Brat, and return to CoNLL-U:

```python
from nlp_utilities.brat import conllu_to_brat, brat_to_conllu
from nlp_utilities.loaders import load_language_data

# Step 1: Convert to Brat
conllu_to_brat(
    conllu_filename='corpus.conllu',
    output_directory='for_annotation/',
    output_root=True,
    sents_per_doc=50
)

# ... Manual annotation in Brat ...

# Step 2: Convert back to CoNLL-U
feature_set = load_language_data('la')
brat_to_conllu(
    input_directory='for_annotation/',
    output_directory='annotated_output/',
    ref_conllu='corpus.conllu',  # Use original as reference
    feature_set=feature_set,
    output_root=True,
    sents_per_doc=50
)
```

### Important Notes

1. Keep `output_root` and `sents_per_doc` consistent between conversions
2. The reference CoNLL-U file should have the same sentences in the same order
3. Only dependency structure (HEAD/DEPREL) is modified; morphology comes from reference

## IOB Tag Conversion

For Named Entity Recognition (NER) annotations with IOB tags.

### Converting IOB-tagged CoNLL-U to Brat

If you have NER tags in the MISC column of your CoNLL-U file:

```python
from nlp_utilities.brat import conllubio_to_brat

conllubio_to_brat(
    filename='ner_tagged.conllu',
    output_directory='brat_ner/'
)
```

This reads IOB tags from the MISC column and creates entity spans in Brat format.

### IOB Tag Format

The MISC column should contain tags like:

- `B-PER`: Beginning of a person entity
- `I-PER`: Inside a person entity
- `O`: Outside any entity

Example CoNLL-U with IOB tags:

```text
# text = Marcus Tullius Cicero wrote books.
1  Marcus   Marcus   PROPN  ...  B-PER
2  Tullius  Tullius  PROPN  ...  I-PER
3  Cicero   Cicero   PROPN  ...  I-PER
4  wrote    write    VERB   ...  O
5  books    book     NOUN   ...  O
6  .        .        PUNCT  ...  O
```

## Troubleshooting

### ID Mismatches

If you get “ID mismatch” errors during brat_to_conllu:

- Ensure the reference file has the same sentences as the Brat files
- Check that sentence order hasn’t changed
- Verify `sents_per_doc` parameter matches original conversion

### Missing Features

If converted CoNLL-U is missing morphological features:

- Ensure you provided a valid reference CoNLL-U file with features
- Check that the reference file sentences align with Brat sentences
- Verify the feature_set is loaded correctly

### Encoding Issues

If you see garbled characters:

- Ensure all files use UTF-8 encoding
- Check that your text editor/viewer supports UTF-8

## See Also

- {ref}`api_reference` - Detailed API documentation
- [Validation](validation.md) - Validating converted CoNLL-U files
- [Evaluation](evaluation.md) - Evaluating conversion accuracy
