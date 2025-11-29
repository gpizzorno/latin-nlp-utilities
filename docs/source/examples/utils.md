# Utilities Examples

Examples for working with feature strings, XPOS tags, and format conversion utilities.

## Convert Features to XPOS

### Complete Workflow

```python
from conllu_tools.utils import features_to_xpos, feature_string_to_dict, validate_xpos

# Start with features only
feats_str = 'Case=Gen|Gender=Fem|Number=Plur'
feats_dict = feature_string_to_dict(feats_str)

# Generate XPOS from features
xpos = features_to_xpos(feats_dict)
print(f"Generated XPOS: {xpos}")  # '-p---fg-'

# Validate for specific UPOS
validated_xpos = validate_xpos('NOUN', xpos)
print(f"Validated XPOS: {validated_xpos}")  # 'n-p---fg-'
```

### Filling Partial XPOS

```python
from conllu_tools.utils import features_to_xpos

# You have partial XPOS and want to fill gaps from features
provided_xpos = 'v--pi----'  # Tense and Mood known
features = 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act'

# Generate from features
xpos_from_feats = features_to_xpos(features)
print(xpos_from_feats)  # '-3spia---'

# Reconcile: provided positions take precedence, fill gaps
final_xpos = list(provided_xpos)
for i, char in enumerate(xpos_from_feats):
    if final_xpos[i] == '-' and char != '-':
        final_xpos[i] = char

print(''.join(final_xpos))  # 'v3spia---' (combined)
```

## Format XPOS

### Processing Mixed Formats

```python
from conllu_tools.utils import format_xpos

# Process tokens from different source treebanks
tokens = [
    {'upos': 'VERB', 'xpos': 'v|v|3|s|p|i|a|-|-|-', 'feats': 'Mood=Ind|...', 'source': 'LLCT'},
    {'upos': 'NOUN', 'xpos': 'gen2|casA', 'feats': 'Case=Nom|...', 'source': 'ITTB'},
    {'upos': 'ADJ', 'xpos': 'Nb', 'feats': 'Case=Acc|...', 'source': 'PROIEL'},
]

for token in tokens:
    token['xpos_normalized'] = format_xpos(
        token['upos'],
        token['xpos'],
        token['feats']
    )
    print(f"{token['source']}: {token['xpos']} → {token['xpos_normalized']}")

# Output:
# LLCT: v|v|3|s|p|i|a|-|-|- → v3spia---
# ITTB: gen2|casA → n-s---fn-
# PROIEL: Nb → n-s---na-
```

## See Also

- {doc}`/user_guide/utils` for detailed documentation
