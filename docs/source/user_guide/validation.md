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
from nlp_utilities.conllu.validators import Validator

# Create validator instance
validator = Validator('corpus.conllu')

# Run validation
is_valid = validator.validate()

if not is_valid:
    # Print errors to console
    validator.report_errors()
```

The validator runs all checks by default and reports any issues found.

## Validation Levels

Validators are organized by the aspects they check:

### Format Validators

Check basic CoNLL-U format compliance:

- **format.py**: Overall line structure, column counts
- **metadata.py**: Sentence-level metadata comments
- **unicode.py**: Character encoding issues
- **id_sequence.py**: Token ID validity and sequencing
- **spans.py**: Multi-word token and empty node span validity

```python
# Format-only validation
from nlp_utilities.conllu.validators import FormatValidator

validator = FormatValidator('file.conllu')
validator.validate()
```

### Content Validators

Check linguistic annotation validity:

- **content_validators.py**: Core column content (UPOS, DEPREL, FEATS)
- **feature_format.py**: Morphological feature syntax
- **enhanced_deps.py**: Enhanced dependency format
- **misc_column.py**: MISC column format
- **upos_deprel_compatibility.py**: Valid UPOS-DEPREL combinations

```python
# Content validation
from nlp_utilities.conllu.validators import ContentValidator

validator = ContentValidator('file.conllu')
validator.validate()
```

### Structural Validators

Check tree structure validity:

- **structural_constraints.py**: Dependency tree properties
- **functional_leaves.py**: Leaf node restrictions
- **tree_validation.py**: Graph cycles, connectivity

```python
# Structural validation
from nlp_utilities.conllu.validators import StructuralValidator

validator = StructuralValidator('file.conllu')
validator.validate()
```

### Language-Specific Validators

Validate against language-specific tagsets:

- **language_content.py**: Language-specific UPOS/DEPREL sets
- **language_format.py**: Language-specific feature formats
- **character_constraints.py**: Allowed characters by language

```python
# Language-specific validation for Latin
from nlp_utilities.conllu.validators import LanguageValidator

validator = LanguageValidator('la_corpus.conllu', language='la')
validator.validate()
```

## Advanced Usage

### Custom Validator Configuration

Configure which validators to run:

```python
from nlp_utilities.conllu.validators import Validator

validator = Validator(
    'corpus.conllu',
    # Disable specific validators
    check_format=True,
    check_content=True,
    check_structure=False,  # Skip structural checks
    check_language=False    # Skip language-specific checks
)

validator.validate()
```

### Accessing Error Details

Get structured error information:

```python
validator = Validator('corpus.conllu')
validator.validate()

# Access errors programmatically
errors = validator.get_errors()

for error in errors:
    print(f"Line {error.line}: {error.message}")
    print(f"  Severity: {error.severity}")
    print(f"  Category: {error.category}")
```

### Error Categories

Errors are categorized for filtering:

- `FORMAT_ERROR`: Syntax violations
- `CONTENT_ERROR`: Invalid values
- `STRUCTURE_ERROR`: Tree structure issues
- `LANGUAGE_ERROR`: Language-specific violations

### Error Severity Levels

- `CRITICAL`: Must be fixed (prevents parsing)
- `ERROR`: Should be fixed (violates specification)
- `WARNING`: May need attention (unusual but valid)

## Validation Recipes

### Pre-submission Validation

Before submitting to Universal Dependencies:

```python
from nlp_utilities.conllu.validators import Validator

# Full validation with all checks
validator = Validator(
    'submission.conllu',
    language='la',
    strict=True  # Treat warnings as errors
)

if not validator.validate():
    validator.report_errors()
    exit(1)
```

### Post-Conversion Validation

After converting from another format:

```python
from nlp_utilities.conllu.validators import Validator
from nlp_utilities.loaders import load_language_data

# Load expected feature set
feature_set = load_language_data('la')

validator = Validator(
    'converted.conllu',
    language='la',
    feature_set=feature_set,
    # Focus on structure and content
    check_structure=True,
    check_content=True
)

validator.validate()
validator.report_errors()
```

### Batch Validation

Validate multiple files:

```python
from pathlib import Path
from nlp_utilities.conllu.validators import Validator

corpus_dir = Path('corpus/')
all_valid = True

for file in corpus_dir.glob('*.conllu'):
    print(f"\nValidating {file.name}...")
    validator = Validator(str(file))

    if not validator.validate():
        all_valid = False
        validator.report_errors()

if all_valid:
    print("\n✓ All files valid!")
else:
    print("\n✗ Some files have errors")
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

### Feature Format Errors

**Error**: “Invalid feature format”

**Cause**: Features must be `Name=Value` pairs, pipe-separated, alphabetically sorted.

**Fix**:

```text
# Wrong
Case=Nom|Number=Sing|gender=Masc

# Right
Case=Nom|Gender=Masc|Number=Sing
```

Use the normalizer to fix automatically:

```python
from nlp_utilities.normalizers import normalize_features

fixed = normalize_features("Case=Nom|Number=Sing|gender=Masc")
# Returns: "Case=Nom|Gender=Masc|Number=Sing"
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

## Validation Best Practices

1. **Validate Early and Often**

   Run validation after each major editing step to catch issues quickly.
2. **Use Language-Specific Settings**

   Always specify the language code for accurate validation:
   ```python
   validator = Validator('file.conllu', language='la')
   ```
3. **Address Critical Errors First**

   Fix `CRITICAL` errors before `ERROR` level, and `ERROR` before `WARNING`.
4. **Keep Reference Data Updated**

   Ensure your feature sets and tagsets match the UD version you’re targeting.
5. **Automate Validation**

   Include validation in your CI/CD pipeline:
   ```bash
   python -m nlp_utilities.conllu.validators corpus.conllu
   ```

## Integration with Other Tools

### With Evaluation

Validate before evaluating:

```python
from nlp_utilities.conllu.validators import Validator
from nlp_utilities.conllu.evaluators import Evaluator

# Validate both files first
for filename in ['gold.conllu', 'system.conllu']:
    validator = Validator(filename)
    if not validator.validate():
        print(f"{filename} has validation errors!")
        validator.report_errors()
        exit(1)

# Then evaluate
evaluator = Evaluator('gold.conllu', 'system.conllu')
results = evaluator.evaluate()
```

### With Conversion

Validate after conversion:

```python
from nlp_utilities.brat import brat_to_conllu
from nlp_utilities.conllu.validators import Validator
from nlp_utilities.loaders import load_language_data

# Convert
feature_set = load_language_data('la')
brat_to_conllu(
    input_directory='brat_files/',
    output_directory='output/',
    ref_conllu='reference.conllu',
    feature_set=feature_set
)

# Validate result
validator = Validator('output/converted.conllu', language='la')
if not validator.validate():
    print("Conversion produced invalid CoNLL-U!")
    validator.report_errors()
```

## See Also

- [Evaluation](evaluation.md) - Evaluating annotation accuracy
- [Brat Conversion](brat_conversion.md) - Converting between formats
- {ref}`api_reference` - Detailed validator API
