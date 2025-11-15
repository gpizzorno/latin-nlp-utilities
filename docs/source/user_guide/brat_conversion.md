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
- `metadata.json` file containing conversion parameters (used for round-trip conversion)

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
├── metadata.json      # Conversion parameters (for round-trip conversion)
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
- **metadata.json**: Automatically creates a metadata file containing conversion parameters

### The `metadata.json` File

The `conllu_to_brat` function automatically creates a `metadata.json` file in the output directory containing:

```json
{
  "conllu_filename": "input.conllu",
  "sents_per_doc": 10,
  "output_root": true
}
```

**Purpose**: This file stores the conversion parameters so that `brat_to_conllu` can automatically use the same settings for round-trip conversion. When you call `brat_to_conllu`, it will:

1. Check for `metadata.json` in the input directory
2. Load the parameters from the file if present
3. Use those values if you don't explicitly provide them

**Benefits**:
- Ensures consistency between forward and reverse conversions
- Eliminates the need to remember or document conversion parameters
- Reduces errors from parameter mismatches

**Note**: You can override metadata values by explicitly passing parameters to `brat_to_conllu`.

## Brat to CoNLL-U

Converting Brat annotations back to CoNLL-U format after manual annotation or review.

### Basic Usage

```python
from nlp_utilities.brat import brat_to_conllu
from nlp_utilities.loaders import load_language_data

# Load feature set for validation
feature_set = load_language_data('feats', language='la')

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
: Directory where the output CoNLL-U file will be created. The output file will be named
  `{basename}-from_brat.conllu` where `{basename}` is derived from the reference file name.

**ref_conllu** (str)
: Path to a reference CoNLL-U file. This provides morphological features (LEMMA, XPOS, FEATS)
  and other information not captured in Brat annotations. Optional if `metadata.json` exists
  in the input directory with this information.

**feature_set** (dict)
: Feature set definition loaded from {func}`nlp_utilities.loaders.load_language_data`.
  Used to validate and normalize features. Required parameter.

**output_root** (bool, optional)
: Must match the value used when creating the Brat files (whether ROOT entities were included).
  While not used in the conversion logic itself, this parameter is required to ensure consistency
  and must match the original conversion settings. Optional if `metadata.json` exists
  in the input directory with this information.

**sents_per_doc** (int, optional)
: Must match the value used when creating the Brat files. Can be `None` if all sentences
  were in one document. Optional if `metadata.json` exists in the input directory.

### Features

- **Morphology from reference**: Retrieves LEMMA, XPOS, FEATS from reference file
- **Dependency from Brat**: Uses HEAD and DEPREL from Brat annotations
- **Enhanced dependencies**: Supports enhanced dependency graphs
- **ID renumbering**: Handles ID conflicts when merging multiple files
- **Automatic UPOS correction**: Changes VERB→AUX for auxiliary verbs based on deprel
- **Automatic parameter loading**: Reads conversion parameters from `metadata.json` if present

### Using metadata.json for Automatic Configuration

If you converted to Brat using `conllu_to_brat`, a `metadata.json` file was created. You can use it to simplify the conversion back:

```python
from nlp_utilities.brat import brat_to_conllu
from nlp_utilities.loaders import load_language_data

# Load feature set (still required)
feature_set = load_language_data('feats', language='la')

# metadata.json in input directory provides ref_conllu, sents_per_doc, and output_root
brat_to_conllu(
    input_directory='brat_output/',
    output_directory='conllu_output/',
    feature_set=feature_set
)
# No need to specify ref_conllu, output_root, or sents_per_doc!
```

The function will automatically:
1. Look for `metadata.json` in `brat_output/`
2. Read `conllu_filename` (used as `ref_conllu`)
3. Read `output_root` and `sents_per_doc` values
4. Use those parameters for conversion

**Manual parameters override metadata**: If you provide parameters explicitly, they take precedence over metadata values.

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
# This creates metadata.json with all the conversion parameters

# ... Manual annotation in Brat ...

# Step 2: Convert back to CoNLL-U
feature_set = load_language_data('feats', language='la')
brat_to_conllu(
    input_directory='for_annotation/',
    output_directory='annotated_output/',
    feature_set=feature_set
)
# metadata.json automatically provides ref_conllu, output_root, and sents_per_doc!
```

### Important Notes

1. The `metadata.json` file simplifies round-trip conversion by storing parameters
2. If `metadata.json` is not present, you must provide `ref_conllu` and `output_root` explicitly
3. The reference CoNLL-U file should have the same sentences in the same order
4. Only dependency structure (HEAD/DEPREL) is modified; morphology comes from reference

## Troubleshooting

### Missing metadata.json

If you get `AssertionError: No ref_conllu value passed and no metadata file found`:

**Cause**: The `brat_to_conllu` function needs to know the reference file and conversion parameters, but no `metadata.json` exists and you didn't provide them explicitly.

**Solutions**:
1. If you have the original parameters, provide them explicitly:
   ```python
   brat_to_conllu(
       input_directory='brat_output/',
       output_directory='conllu_output/',
       feature_set=feature_set,
       ref_conllu='original.conllu',
       output_root=True,
       sents_per_doc=10
   )
   ```

2. If you don't know the parameters, check how the Brat files were created or try:
   ```python
   # Start with defaults
   brat_to_conllu(
       input_directory='brat_output/',
       output_directory='conllu_output/',
       feature_set=feature_set,
       ref_conllu='original.conllu',
       output_root=False,  # Try False first
       sents_per_doc=None
   )
   ```

### ID Mismatches

If you get "ID mismatch" or "Sentence length mismatch" errors during brat_to_conllu:

- Ensure the reference file has the same sentences as the Brat files
- Check that sentence order hasn't changed
- Verify `sents_per_doc` parameter matches original conversion (or use metadata.json)
- Check that you haven't added or removed sentences in Brat

### Token Mismatch Errors

If you get "Token mismatch in sentence X" errors:

**Cause**: The tokens in the Brat `.txt` file don't match the tokens in the reference CoNLL-U file.

**Solutions**:
- Ensure you're using the correct reference file (the one originally converted)
- Check that no tokens were edited in the Brat `.txt` files
- Verify that tokenization is identical between files (case-insensitive comparison is used)

### Missing Features

If converted CoNLL-U is missing morphological features:

- Ensure you provided a valid reference CoNLL-U file with features
- Check that the reference file sentences align with Brat sentences
- Verify the feature_set is loaded correctly with: `load_language_data('feats', language='la')`
- Remember: Brat only stores UPOS, HEAD, and DEPREL - all other fields come from the reference file

### Missing Output File

If no output file is created:

- Check that the input directory contains `.ann` files
- Verify the output directory path is writable
- Ensure `feature_set` parameter is provided (it's required)
- Check for error messages about missing reference files

### Encoding Issues

If you see garbled characters:

- Ensure all files use UTF-8 encoding
- Check that your text editor/viewer supports UTF-8

## See Also

- {ref}`api_reference` - Detailed API documentation
- [Validation](validation.md) - Validating converted CoNLL-U files
- [Evaluation](evaluation.md) - Evaluating conversion accuracy
