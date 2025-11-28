# Validation

This guide covers validating CoNLL-U files using the comprehensive validation framework.

## Overview

The validation module provides extensive checking for CoNLL-U files to ensure they meet format
specifications and linguistic constraints. The validators catch:

- Format violations (invalid characters, malformed columns)
- Structural issues (ID sequences, dependency cycles, orphaned nodes)
- Content problems (invalid UPOS tags, feature formats)
- Language-specific constraints (tagset compatibility, feature values)
- Enhanced dependency issues

## Quick Start

Basic validation of a CoNLL-U file:

```python
from conllu_tools.validation import ConlluValidator

# Create validator instance
validator = ConlluValidator(lang='la', level=2)

# Run validation
errors = validator.validate_file('corpus.conllu')

if errors.get_error_count() > 0:
    # Print errors to console
    print('\n'.join(errors.format_errors()))
```

The validator runs checks based on the specified level (1-5) and reports any issues found.

## Validation Levels

The validator uses a 5-level system to control validation strictness:

### Level 1: Basic Format

Checks essential CoNLL-U format compliance:

- Unicode validity
- Basic format structure and column counts
- Token ID validity and sequencing  
- Basic tree structure (connectivity, cycles)

```python
from conllu_tools.validation import ConlluValidator

validator = ConlluValidator(level=1)
errors = validator.validate_file('file.conllu')
```

### Level 2: Standard Validation (Default)

Adds content and metadata validation:

- Metadata comments format
- MISC column format
- Character constraints in various columns
- Morphological feature format and values
- Enhanced dependency format
- All Level 1 checks

```python
validator = ConlluValidator(level=2)  # Default level
errors = validator.validate_file('file.conllu')
```

### Level 3: Extended Validation

Adds structural and content constraints:

- Left-to-right relations
- Single subject constraint
- Orphan validation
- "goes with" and "fixed" span validation
- Projective punctuation
- Functional leaves
- All Level 1-2 checks

```python
validator = ConlluValidator(level=3)
errors = validator.validate_file('file.conllu')
```

### Level 4: Language-Specific Format

Validates language-specific format requirements:

- Language-specific feature sets
- Language-specific dependency relations
- Language-specific auxiliary verbs
- Whitespace exceptions
- All Level 1-3 checks

```python
validator = ConlluValidator(lang='la', level=4)
errors = validator.validate_file('file.conllu')
```

### Level 5: Language-Specific Content

Full language-specific validation:

- Language-specific content constraints
- All Level 1-4 checks

```python
validator = ConlluValidator(lang='la', level=5)
errors = validator.validate_file('file.conllu')
```

## Advanced Usage

### Custom Validator Configuration

Configure language-specific data sources:

```python
from conllu_tools.validation import ConlluValidator

validator = ConlluValidator(
    lang='la',
    level=4,
    add_features='custom_features.json',  # Additional features file
    add_deprels='custom_deprels.json',     # Additional deprels file
    add_auxiliaries='custom_aux.json',     # Additional auxiliaries file
    add_whitespace_exceptions='custom_whitespace.txt',  # Additional whitespace rules
    load_dalme=False  # Whether to load DALME-specific data
)

errors = validator.validate_file('corpus.conllu')
```

### Validating String Content

Validate CoNLL-U content directly from a string:

```python
validator = ConlluValidator(lang='la', level=2)

conllu_text = """# sent_id = 1
# text = example
1\texample\texample\tNOUN\t_\t_\t0\troot\t_\t_

"""

errors = validator.validate_string(conllu_text)
if errors.get_error_count() > 0:
    print('\n'.join(errors.format_errors()))
```

### Accessing Error Details

Get structured error information:

```python
validator = ConlluValidator(lang='la', level=2)
errors = validator.validate_file('corpus.conllu')

# Check error count
if errors.get_error_count() > 0:
    print(f"Found {errors.get_error_count()} errors")

    # Get formatted error messages
    for error_msg in errors.format_errors():
        print(error_msg)

    # Access error statistics
    print(f"\nError counts by type: {errors.error_counter}")
```

## Common Validation Errors

### ID Sequence Errors

**Error**: “Non-consecutive token IDs”

**Cause**: Token IDs must form a continuous sequence (1, 2, 3, …).

**Fix**: Renumber tokens sequentially:

```python
# The validator will identify which sentences have gaps
# Manually renumber or use ID reassignment tools
```

### Multi-word Token Errors

**Error**: “Invalid multiword token range”

**Cause**: Multi-word token range (e.g., `1-2`) doesn’t match component tokens.

**Fix**: Ensure the range spans exactly the tokens it should combine:

```text
1-2    del       _         _      ...
1      de        de        ADP    ...
2      il        il        DET    ...
```


### UPOS-DEPREL Compatibility

**Error**: “Invalid UPOS-DEPREL combination”

**Cause**: Some UPOS-DEPREL pairs are semantically invalid (e.g., `NOUN:aux`).

**Fix**: Check the Universal Dependencies guidelines for valid combinations. Common issues:

- Auxiliaries must be `AUX`, not `VERB`
- Coordinating conjunctions must be `CCONJ`
- Proper use of `nsubj` vs `nsubj:pass`

### Tree Structure Errors

**Error**: “Cycle detected in dependency tree”

**Cause**: A token has itself as an ancestor (direct or indirect).

**Fix**: Review the HEAD assignments to eliminate circular dependencies:

```text
# Wrong: Token 2 points to 3, token 3 points to 2
2  word2  ...  3  deprel
3  word3  ...  2  deprel
```

## See Also

- [Evaluation](evaluation.md) - Evaluating annotation accuracy
- [Conversion](conversion.md) - Converting between formats
- {doc}`../api_reference/validation` - Detailed validation API
