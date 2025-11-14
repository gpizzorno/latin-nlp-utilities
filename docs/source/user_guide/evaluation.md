# Evaluation

This guide covers evaluating CoNLL-U annotations by comparing gold standard and system outputs.

## Overview

The evaluation module computes standard metrics for dependency parsing and linguistic annotation:

- **UAS** (Unlabeled Attachment Score): Percentage of correct HEAD assignments
- **LAS** (Labeled Attachment Score): Percentage of correct HEAD + DEPREL pairs
- **UPOS Accuracy**: Percentage of correct universal POS tags
- **XPOS Accuracy**: Percentage of correct language-specific POS tags
- **Feature Accuracy**: Percentage of correct morphological feature sets

## Quick Start

Basic evaluation comparing gold standard and system output:

```python
from nlp_utilities.conllu.evaluators import Evaluator

# Create evaluator
evaluator = Evaluator(
    gold_file='gold.conllu',
    system_file='system.conllu'
)

# Compute all metrics
results = evaluator.evaluate()

# Print results
print(f"UAS: {results['UAS']:.2f}%")
print(f"LAS: {results['LAS']:.2f}%")
print(f"UPOS: {results['UPOS']:.2f}%")
```

## Understanding Metrics

### Unlabeled Attachment Score (UAS)

Measures how often the parser correctly identifies which word is the head (governor) of each token,
regardless of the dependency label.

```python
# Gold:  word1 → word2 (nsubj)
# System: word1 → word2 (obj)
# Result: Correct for UAS (head is right), incorrect for LAS (label is wrong)
```

**When to use**: Evaluating basic syntactic structure understanding.

### Labeled Attachment Score (LAS)

Measures how often the parser correctly identifies both the head AND the dependency relation label.

```python
# Gold:  word1 → word2 (nsubj)
# System: word1 → word2 (nsubj)
# Result: Correct for both UAS and LAS
```

**When to use**: Full parsing accuracy evaluation.

### UPOS Accuracy

Measures correct universal part-of-speech tagging.

```python
# Gold:  VERB
# System: NOUN
# Result: Incorrect
```

**When to use**: Evaluating morphological tagging.

### XPOS Accuracy

Measures correct language-specific POS tagging.

```python
# Gold:  VBD (past tense verb)
# System: VBZ (3rd person singular present)
# Result: Incorrect
```

**When to use**: Evaluating fine-grained morphological analysis.

### Features Accuracy

Measures correct morphological feature sets (FEATS column).

```python
# Gold:  Case=Nom|Gender=Masc|Number=Sing
# System: Case=Nom|Gender=Masc|Number=Plur
# Result: Incorrect (Number differs)
```

**When to use**: Evaluating detailed morphological annotation.

## Advanced Usage

### Partial Credit Metrics

Use partial credit for features to get more nuanced evaluation:

```python
from nlp_utilities.conllu.evaluators import Evaluator

evaluator = Evaluator(
    gold_file='gold.conllu',
    system_file='system.conllu',
    partial_credit=True  # Count partially correct features
)

results = evaluator.evaluate()

# Now features get partial credit
# If gold is "Case=Nom|Number=Sing" and system is "Case=Nom|Number=Plur"
# System gets 50% credit (Case correct, Number wrong)
```

### Ignoring Punctuation

Exclude punctuation tokens from evaluation:

```python
evaluator = Evaluator(
    gold_file='gold.conllu',
    system_file='system.conllu',
    ignore_punct=True  # Exclude PUNCT tokens
)

results = evaluator.evaluate()
```

This gives a clearer picture of content word parsing accuracy.

### Per-Sentence Results

Get detailed per-sentence breakdown:

```python
evaluator = Evaluator('gold.conllu', 'system.conllu')

sentence_results = evaluator.evaluate_sentences()

for idx, sent_result in enumerate(sentence_results, 1):
    print(f"Sentence {idx}:")
    print(f"  UAS: {sent_result['UAS']:.1f}%")
    print(f"  LAS: {sent_result['LAS']:.1f}%")
    print(f"  Errors: {sent_result['errors']}")
```

This helps identify problematic sentences for error analysis.

### Confusion Matrices

Analyze systematic errors:

```python
evaluator = Evaluator('gold.conllu', 'system.conllu')

# Get UPOS confusion matrix
upos_matrix = evaluator.upos_confusion_matrix()

print("Most common UPOS confusions:")
for (gold_tag, sys_tag), count in upos_matrix.most_common(10):
    print(f"  Gold: {gold_tag:6s} → System: {sys_tag:6s}  ({count} times)")

# Get DEPREL confusion matrix
deprel_matrix = evaluator.deprel_confusion_matrix()
```

Use this to identify systematic tagging or parsing errors.

## Evaluation Recipes

### Parser Development

Track progress during parser development:

```python
from nlp_utilities.conllu.evaluators import Evaluator
from pathlib import Path

dev_gold = 'data/dev.conllu'

# Evaluate each parser iteration
for model_file in sorted(Path('models/').glob('iter_*.conllu')):
    evaluator = Evaluator(dev_gold, str(model_file))
    results = evaluator.evaluate()

    print(f"{model_file.stem}:")
    print(f"  LAS: {results['LAS']:.2f}%")
    print(f"  UAS: {results['UAS']:.2f}%")
```

### Cross-Validation

Evaluate multiple folds:

```python
from nlp_utilities.conllu.evaluators import Evaluator
import numpy as np

las_scores = []
uas_scores = []

for fold in range(1, 6):
    gold_file = f'fold_{fold}_gold.conllu'
    system_file = f'fold_{fold}_system.conllu'

    evaluator = Evaluator(gold_file, system_file)
    results = evaluator.evaluate()

    las_scores.append(results['LAS'])
    uas_scores.append(results['UAS'])

print(f"Mean LAS: {np.mean(las_scores):.2f}% (±{np.std(las_scores):.2f})")
print(f"Mean UAS: {np.mean(uas_scores):.2f}% (±{np.std(uas_scores):.2f})")
```

### Error Analysis

Detailed error investigation:

```python
from nlp_utilities.conllu.evaluators import Evaluator

evaluator = Evaluator('gold.conllu', 'system.conllu')

# Get errors by type
errors = evaluator.get_errors()

head_errors = [e for e in errors if e['type'] == 'head']
deprel_errors = [e for e in errors if e['type'] == 'deprel']
upos_errors = [e for e in errors if e['type'] == 'upos']

print(f"Head errors: {len(head_errors)}")
print(f"Deprel errors: {len(deprel_errors)}")
print(f"UPOS errors: {len(upos_errors)}")

# Examine specific error
if head_errors:
    error = head_errors[0]
    print(f"\nExample head error:")
    print(f"  Token: {error['form']}")
    print(f"  Gold head: {error['gold_head']} ({error['gold_head_form']})")
    print(f"  System head: {error['system_head']} ({error['system_head_form']})")
```

### Baseline Comparison

Compare multiple systems:

```python
from nlp_utilities.conllu.evaluators import Evaluator

gold_file = 'test.conllu'
systems = {
    'Baseline': 'baseline_output.conllu',
    'Model A': 'model_a_output.conllu',
    'Model B': 'model_b_output.conllu',
}

print(f"{'System':<15} {'UAS':>8} {'LAS':>8} {'UPOS':>8}")
print("-" * 45)

for name, system_file in systems.items():
    evaluator = Evaluator(gold_file, system_file)
    results = evaluator.evaluate()

    print(f"{name:<15} {results['UAS']:>7.2f}% {results['LAS']:>7.2f}% {results['UPOS']:>7.2f}%")
```

## Common Issues

### File Alignment

**Problem**: “Sentence count mismatch”

**Cause**: Gold and system files have different numbers of sentences.

**Solution**: Ensure both files have identical sentence structure:

```python
# Check sentence counts
from nlp_utilities.loaders import load_conllu

gold_sents = load_conllu('gold.conllu')
system_sents = load_conllu('system.conllu')

print(f"Gold: {len(gold_sents)} sentences")
print(f"System: {len(system_sents)} sentences")
```

### Token Count Mismatch

**Problem**: “Token count mismatch in sentence X”

**Cause**: Sentence has different number of tokens in gold vs system.

**Solution**: Check for:

- Multi-word token handling differences
- Empty node differences
- Missing or extra tokens

```python
# Compare token counts per sentence
for idx, (gold_sent, sys_sent) in enumerate(zip(gold_sents, system_sents), 1):
    if len(gold_sent) != len(sys_sent):
        print(f"Sentence {idx}: gold has {len(gold_sent)}, system has {len(sys_sent)}")
```

### Missing Baseline

If you need a baseline for comparison:

```python
# Simple baseline: attach everything to the first token
from nlp_utilities.conllu.evaluators import SimpleBaseline

baseline = SimpleBaseline('test.conllu')
baseline.create_baseline('baseline_output.conllu')

# Then evaluate
evaluator = Evaluator('test.conllu', 'baseline_output.conllu')
results = evaluator.evaluate()
```

## Evaluation Best Practices

1. **Validate First**

   Always validate files before evaluation:
   ```python
   from nlp_utilities.conllu.validators import Validator

   for file in ['gold.conllu', 'system.conllu']:
       validator = Validator(file)
       if not validator.validate():
           print(f"{file} has errors!")
           exit(1)
   ```
2. **Use Consistent Metrics**

   Use the same evaluation settings when comparing systems.
3. **Report Multiple Metrics**

   Don’t rely solely on LAS; report UAS, UPOS, and Features too.
4. **Consider Domain**

   Parsing accuracy varies by domain. Test on representative data.
5. **Significance Testing**

   For comparing systems, use statistical significance tests:
   ```python
   from scipy import stats

   # LAS scores from two systems
   system_a_scores = [85.3, 84.9, 85.7, ...]  # Per fold or sample
   system_b_scores = [86.1, 85.8, 86.4, ...]

   t_stat, p_value = stats.ttest_rel(system_a_scores, system_b_scores)

   if p_value < 0.05:
       print("System B is significantly better")
   ```

## Integration Examples

### With Validation

```python
from nlp_utilities.conllu.validators import Validator
from nlp_utilities.conllu.evaluators import Evaluator

# Validate before evaluating
for filename in ['gold.conllu', 'system.conllu']:
    validator = Validator(filename)
    if not validator.validate():
        print(f"Error: {filename} is invalid!")
        validator.report_errors()
        exit(1)

# Safe to evaluate
evaluator = Evaluator('gold.conllu', 'system.conllu')
results = evaluator.evaluate()
```

### With Conversion

Evaluate conversion accuracy:

```python
from nlp_utilities.brat import brat_to_conllu
from nlp_utilities.conllu.evaluators import Evaluator
from nlp_utilities.loaders import load_language_data

# Convert
feature_set = load_language_data('la')
brat_to_conllu(
    input_directory='brat_files/',
    output_directory='output/',
    ref_conllu='original.conllu',
    feature_set=feature_set
)

# Evaluate: how well did round-trip preserve structure?
evaluator = Evaluator('original.conllu', 'output/converted.conllu')
results = evaluator.evaluate()

print(f"Round-trip preservation:")
print(f"  LAS: {results['LAS']:.2f}% (should be ~100%)")
```

### Export Results

Save evaluation results:

```python
import json
from nlp_utilities.conllu.evaluators import Evaluator

evaluator = Evaluator('gold.conllu', 'system.conllu')
results = evaluator.evaluate()

# Save as JSON
with open('eval_results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Save as CSV for spreadsheet analysis
import csv
with open('eval_results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Metric', 'Score'])
    for metric, score in results.items():
        writer.writerow([metric, f"{score:.2f}"])
```

## See Also

- [Validation](validation.md) - Validating CoNLL-U files
- [Brat Conversion](brat_conversion.md) - Converting between formats
- {ref}`api_reference` - Detailed evaluator API
