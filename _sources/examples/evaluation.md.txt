# Evaluation Examples

Examples for evaluating parser output against gold-standard annotations.

## Parser Development

Track progress during parser development:

```python
from conllu_tools.evaluation import ConlluEvaluator
from pathlib import Path

evaluator = ConlluEvaluator()
dev_gold = 'data/dev.conllu'

# Evaluate each parser iteration
for model_file in sorted(Path('models/').glob('iter_*.conllu')):
    scores = evaluator.evaluate_files(dev_gold, str(model_file))

    print(f"{model_file.stem}:")
    print(f"  LAS: {scores['LAS'].f1:.2%}")
    print(f"  UAS: {scores['UAS'].f1:.2%}")
```

## Cross-Validation

Evaluate multiple folds:

```python
from conllu_tools.evaluation import ConlluEvaluator
import numpy as np

evaluator = ConlluEvaluator()
las_scores = []
uas_scores = []

for fold in range(1, 6):
    gold_file = f'fold_{fold}_gold.conllu'
    system_file = f'fold_{fold}_system.conllu'

    scores = evaluator.evaluate_files(gold_file, system_file)

    las_scores.append(scores['LAS'].f1)
    uas_scores.append(scores['UAS'].f1)

print(f"Mean LAS: {np.mean(las_scores):.2%} (±{np.std(las_scores):.2f})")
print(f"Mean UAS: {np.mean(uas_scores):.2%} (±{np.std(uas_scores):.2f})")
```

## Baseline Comparison

Compare multiple systems:

```python
from conllu_tools.evaluation import ConlluEvaluator

evaluator = ConlluEvaluator()
gold_file = 'test.conllu'
systems = {
    'Baseline': 'baseline_output.conllu',
    'Model A': 'model_a_output.conllu',
    'Model B': 'model_b_output.conllu',
}

print(f"{'System':<15} {'UAS':>8} {'LAS':>8} {'UPOS':>8}")
print("-" * 45)

for name, system_file in systems.items():
    scores = evaluator.evaluate_files(gold_file, system_file)

    print(f"{name:<15} {scores['UAS'].f1:>7.2%} {scores['LAS'].f1:>7.2%} {scores['UPOS'].f1:>7.2%}")
```

## Integration Examples

### Evaluate Conversion Accuracy

Measure how well a round-trip conversion preserved structure:

```python
from conllu_tools.io import brat_to_conllu, load_language_data
from conllu_tools.evaluation import ConlluEvaluator

# Convert
feature_set = load_language_data('feats', language='la')
brat_to_conllu(
    input_directory='brat_files/',
    output_directory='output/',
    ref_conllu='original.conllu',
    feature_set=feature_set
)

# Evaluate: how well did round-trip preserve structure?
evaluator = ConlluEvaluator()
scores = evaluator.evaluate_files('original.conllu', 'output/original-from_brat.conllu')

print(f"Round-trip preservation:")
print(f"  LAS: {scores['LAS'].f1:.2%} (should be ~100%)")
```

### Export Results to JSON/CSV

Save evaluation results for further analysis:

```python
import json
from conllu_tools.evaluation import ConlluEvaluator

evaluator = ConlluEvaluator()
scores = evaluator.evaluate_files('gold.conllu', 'system.conllu')

# Save as JSON
results_dict = {
    metric: {
        'precision': score.precision,
        'recall': score.recall,
        'f1': score.f1,
        'gold_total': score.gold_total,
        'system_total': score.system_total,
        'correct': score.correct
    }
    for metric, score in scores.items()
}

with open('eval_results.json', 'w') as f:
    json.dump(results_dict, f, indent=2)

# Save as CSV for spreadsheet analysis
import csv
with open('eval_results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Metric', 'Precision', 'Recall', 'F1'])
    for metric, score in scores.items():
        writer.writerow([metric, f"{score.precision:.2f}", f"{score.recall:.2f}", f"{score.f1:.2f}"])
```

## See Also

- [Evaluation User Guide](../user_guide/evaluation.md) for detailed documentation
