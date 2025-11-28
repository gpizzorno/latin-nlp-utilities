# Data Loading

This guide covers loading language-specific data and configurations.

## Feature Set Loading

Load language-specific feature sets.

### Basic Loading

```python
from conllu_tools.io import load_language_data

# Load Latin feature set
feature_set = load_language_data('feats', language='la')

# Use with validate_features
from from conllu_tools.utils.features import validate_features

normalized = validate_features('NOUN', 'Case=Nom|Gender=Masc', feature_set)
```

### Understanding the Feature Set Format

Each feature in the set has a `byupos` dictionary that maps UPOS tags to valid values:

- **Value `1`**: Valid for this UPOS
- **Value `0`**: Invalid/not allowed for this UPOS
- **Missing UPOS**: Feature not applicable to this UPOS

JSON representation:

```json
{
    "Case": {
            "byupos": {
            "NOUN": {"Nom": 1, "Gen": 1, "Dat": 1, "Acc": 1, "Voc": 1, "Abl": 1},
            "ADJ": {"Nom": 1, "Gen": 1, "Dat": 1, "Acc": 1, "Voc": 1, "Abl": 1},
            "VERB": {"Nom": 0, "Gen": 0}
        }
    },
    "Gender": {
        "byupos": {
            "NOUN": {"Masc": 1, "Fem": 1, "Neut": 1},
            "ADJ": {"Masc": 1, "Fem": 1, "Neut": 1}
        }
    }
}
```

Working with feature sets as Python dictionaries:

```python
# Example: Case feature
feature_set['Case']['byupos']['NOUN']
# {'Nom': 1, 'Gen': 1, 'Dat': 1, 'Acc': 1, 'Voc': 1, 'Abl': 1, 'Loc': 1}

# Case not valid for verbs in most contexts
feature_set['Case']['byupos']['VERB']
# {'Nom': 0, 'Gen': 0, ...}  # All marked as invalid

# VerbForm only valid for verbs
feature_set['VerbForm']['byupos']['VERB']
# {'Fin': 1, 'Inf': 1, 'Part': 1, 'Ger': 1, 'Gdv': 1, 'Sup': 1}

feature_set['VerbForm']['byupos'].get('NOUN')
# None or not present - VerbForm doesn't apply to nouns
```

### Custom Feature Sets

Define your own feature set for specialized treebanks or annotation schemes:

```python
# Define a custom feature set
custom_feature_set = {
    'Case': {
        'byupos': {
            'NOUN': {'Nom': 1, 'Gen': 1, 'Acc': 1},  # Only 3 cases
            'ADJ': {'Nom': 1, 'Gen': 1, 'Acc': 1},
        }
    },
    'Gender': {
        'byupos': {
            'NOUN': {'Masc': 1, 'Fem': 1},  # No neuter
            'ADJ': {'Masc': 1, 'Fem': 1},
        }
    },
    'Number': {
        'byupos': {
            'NOUN': {'Sing': 1, 'Plur': 1},
            'ADJ': {'Sing': 1, 'Plur': 1},
            'VERB': {'Sing': 1, 'Plur': 1},
        }
    },
}

# Use custom feature set
from conllu_tools.utils.normalization import normalize_features

# This will remove Dat case (not in custom set)
normalized = normalize_features(
    'NOUN',
    'Case=Nom|Case=Dat|Gender=Masc',
    custom_feature_set
)
print(normalized)
# Output: {'Case': 'Nom', 'Gender': 'Masc'}
```

## Loading Other Language Data

```python
from conllu_tools.io import load_language_data

# Load dependency relations
deprels = load_language_data('deprels', language='la')

# Load auxiliary verbs list
auxiliaries = load_language_data('auxiliaries', language='la')
```

## See Also

- {ref}`api_reference/io` - Detailed API documentation
