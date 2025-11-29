# Evaluation

This guide covers evaluating CoNLL-U annotations by comparing gold standard and system outputs.

## Overview

The evaluation module computes standard metrics for dependency parsing and linguistic annotation:

- **Tokens**: measures how well system tokens match gold tokens.
- **Sentences**: measures how well system sentences match gold sentences.
- **Words**: measures how well system words can be aligned to gold words.
- **UPOS** (Universal Part-of-Speech): F1-score over the set of UPOS in the system output and the gold standard.
- **XPOS** (Extended Part-of-Speech): F1-score over the set of XPOS in the system output and the gold standard.
- **UFeats** (Universal Features): F1-score over the set of UFeats in the system output and the gold standard.
- **AllTags**: combines morphological tagging scores: UPOS, XPOS, and UFeats.
- **Lemmas**: F1-score over the set of lemmata in the system output and the gold standard.
- **UAS** (Unlabeled Attachment Score): F1-score over the set of HEAD values in the system output and the gold standard.
- **LAS** (Labeled Attachment Score): F1-score over the set of dependencies (HEAD and DEPREL) in the system output and the gold standard (ignores subtypes).
- **ELAS** (Enhanced-Dependency Labeled Attachment Score): F1-score over the set of enhanced dependencies in the system output and the gold standard (taking subtypes into account).
- **EULAS** (Enhanced-Dependency Universal-Label Attachment Score): F1-score over the set of enhanced dependencies in the system output and the gold standard where labels are restricted to the universal dependency relation (ignores subtypes).
- **CLAS** (Content-Word Labeled Attachment Score): F1-score over the set of dependencies (HEAD and DEPREL) in the system output and the gold standard for words with content DEPREL (ignores subtypes).
- **MLAS** (Morphology-Aware Labeled Attachment Score): extension of CLAS that, in addition to HEAD and DEPREL, also includes UPOS, UFeats, and the scores of functional children in the score calculation.
- **BLEX** (Bilexical Dependency Score): extension of CLAS that adds lemmas to the score calculation. 

**References**:

- https://universaldependencies.org/conll17/evaluation.html
- https://universaldependencies.org/conll18/evaluation.html
- https://universaldependencies.org/iwpt20/task_and_evaluation.html
- https://universaldependencies.org/iwpt21/task_and_evaluation.html


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
- {doc}`../api_reference/evaluation` - Detailed evaluation API
