# Validation Examples

Examples for validating CoNLL-U files for format and annotation guideline compliance.

## Post-Conversion Validation

After converting from another format:

```python
from conllu_tools.validation import ConlluValidator

# Focus on structure and content (level 3)
validator = ConlluValidator(lang='la', level=3)

errors = validator.validate_file('converted.conllu')

if errors.get_error_count() > 0:
    print(f"Found {errors.get_error_count()} validation errors")
    print('\n'.join(errors.format_errors()))
```

## Batch Validation

Validate multiple files:

```python
from pathlib import Path
from conllu_tools.validation import ConlluValidator

corpus_dir = Path('corpus/')
validator = ConlluValidator(lang='la', level=2)
all_valid = True

for file in corpus_dir.glob('*.conllu'):
    print(f"\nValidating {file.name}...")
    errors = validator.validate_file(str(file))

    if errors.get_error_count() > 0:
        all_valid = False
        print('\n'.join(errors.format_errors()))

if all_valid:
    print("\nAll files valid!")
else:
    print("\nSome files have errors")
```

## Integration with Other Tools

### Validate Before Evaluation

Validate before evaluating:

```python
from conllu_tools.validation import ConlluValidator
from conllu_tools.evaluation import ConlluEvaluator

# Validate both files first
validator = ConlluValidator(lang='la', level=2)

for filename in ['gold.conllu', 'system.conllu']:
    errors = validator.validate_file(filename)
    if errors.get_error_count() > 0:
        print(f"{filename} has validation errors!")
        print('\n'.join(errors.format_errors()))
        exit(1)

# Then evaluate
evaluator = ConlluEvaluator()
scores = evaluator.evaluate_files('gold.conllu', 'system.conllu')
```

### Validate After Conversion

Validate after conversion:

```python
from conllu_tools.io import brat_to_conllu, load_language_data
from conllu_tools.validation import ConlluValidator

# Convert
feature_set = load_language_data('feats', language='la')
brat_to_conllu(
    input_directory='brat_files/',
    output_directory='output/',
    ref_conllu='reference.conllu',
    feature_set=feature_set
)

# Validate result
validator = ConlluValidator(lang='la', level=3)
errors = validator.validate_file('output/reference-from_brat.conllu')

if errors.get_error_count() > 0:
    print("Conversion produced invalid CoNLL-U!")
    print('\n'.join(errors.format_errors()))
```

## See Also

- [Validation User Guide](../user_guide/validation.md) for detailed documentation
