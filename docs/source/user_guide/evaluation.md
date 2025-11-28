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
from conllu_tools.evaluation import ConlluEvaluator

# Create evaluator
evaluator = ConlluEvaluator()

# Evaluate files
scores = evaluator.evaluate_files(
    gold_path='gold.conllu',
    system_path='system.conllu'
)

# Print results (scores are returned as percentages 0-100)
print(f"UAS: {scores['UAS'].f1:.2f}%")
print(f"LAS: {scores['LAS'].f1:.2f}%")
print(f"UPOS: {scores['UPOS'].f1:.2f}%")
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

### Disabling Dependency Evaluation

Skip dependency evaluation if not needed:

```python
from conllu_tools.evaluation import ConlluEvaluator

evaluator = ConlluEvaluator(eval_deprels=False)

scores = evaluator.evaluate_files('gold.conllu', 'system.conllu')

# UAS and LAS will return None values when eval_deprels=False
```

### Treebank Type Configuration

Configure enhancement type handling for specific treebank types:

```python
evaluator = ConlluEvaluator(
    treebank_type='12'  # Disable enhancement types 1 and 2
)

scores = evaluator.evaluate_files('gold.conllu', 'system.conllu')
```

Treebank type flags:
- `'1'`: Disable gapping enhancements
- `'2'`: Disable shared parents in coordination
- `'3'`: Disable shared dependents in coordination
- `'4'`: Disable control
- `'5'`: Disable external arguments of relative clauses
- `'6'`: Disable case information

### Accessing Score Details

`Score` objects provide detailed metrics:

```python
evaluator = ConlluEvaluator()
scores = evaluator.evaluate_files('gold.conllu', 'system.conllu')

las_score = scores['LAS']
print(f"Precision: {las_score.precision:.2f}%")
print(f"Recall: {las_score.recall:.2f}%")
print(f"F1: {las_score.f1:.2f}%")
print(f"Gold total: {las_score.gold_total}")
print(f"System total: {las_score.system_total}")
print(f"Correct: {las_score.correct}")

# Some metrics also have aligned_accuracy
if las_score.aligned_total:
    print(f"Aligned accuracy: {las_score.aligned_accuracy:.2f}%")
```



## Common Issues

### File Alignment

**Problem**: "Sentence count mismatch" or `UDError`

**Cause**: Gold and system files have different numbers of sentences.

**Solution**: Ensure both files have identical sentence structure:

```python
# Check sentence counts
import conllu

with open('gold.conllu', encoding='utf-8') as f:
    gold_sents = conllu.parse(f.read())

with open('system.conllu', encoding='utf-8') as f:
    system_sents = conllu.parse(f.read())

print(f"Gold: {len(gold_sents)} sentences")
print(f"System: {len(system_sents)} sentences")
```

### Token Count Mismatch

**Problem**: "Token count mismatch in sentence X"

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

## See Also

- [Validation](validation.md) - Validating CoNLL-U files
- [Conversion](conversion.md) - Converting between formats
- {ref}`api_reference/evaluation` - Detailed evaluation API
