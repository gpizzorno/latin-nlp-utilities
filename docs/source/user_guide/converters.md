# Converters

This guide covers converting between different tagsets and annotation schemes for Latin treebanks.

## Overview

The converters module provides utilities for standardizing annotations from various Latin treebanks
to a common format. This includes:

- **UPOS conversion**: Language-specific POS tags → Universal POS tags
- **Feature conversion**: Various morphological annotation schemes → Universal Features
- **XPOS conversion**: Normalizing language-specific POS tags across treebanks

These converters are useful for:

- Harmonizing annotations across different Latin treebanks
- Creating cross-treebank training datasets
- Adapting legacy annotations to Universal Dependencies standards

## Quick Start

Converting from PROIEL UPOS AND FEATS to Perseus XPOS:

```python
from nlp_utilities.converters.xpos import proiel_to_perseus

proiel_upos = 'NOUN'
proiel_feats = 'Case=Acc|Gender=Neut|Number=Sing'
new_xpos = proiel_to_perseus(proiel_upos, proiel_feats) # PROIEL XPOS = 'Nb'
print(new_xpos)  # "n-s---na-"
```

Converting from ITTB UPOS and XPOS to Perseus XPOS:

```python
from nlp_utilities.converters.xpos import ittb_to_perseus

ittb_upos = 'ADJ'
ittb_xpos = 'C1|grn1|casB|gen1'
new_xpos = ittb_to_perseus(ittb_upos, ittb_xpos)
print(new_xpos)  # "a-s---mgp"
```

## XPOS Converters

The XPOS converters normalize language-specific POS tags from different treebanks to a
common Perseus-style format.

### Supported Treebanks

- **PROIEL**: e.g., `Pp`
- **ITTB**: e.g., `J3|modJ|tem3|gen6`
- **LLCT**: e.g., `v|v|1|s|r|i|a|-|-|-`
- **Perseus**: Target format (e.g., `v3spia---`)

### PROIEL to Perseus

The PROIEL converter takes UPOS and FEATS:

```python
from nlp_utilities.converters.xpos import proiel_to_perseus

print(proiel_to_perseus('NOUN', 'Case=Nom|Gender=Masc|Number=Sing'))
# Returns 'n-s---mn-'

print(proiel_to_perseus('VERB', 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Pass'))
# Returns 'v3spip---'

print(proiel_to_perseus('PRON', 'Case=Dat|Number=Sing|Person=1'))
# Returns 'p1s----d-'
```

### ITTB to Perseus

The ITTB converter takes UPOS and XPOS:

```python
from nlp_utilities.converters.xpos import ittb_to_perseus

print(ittb_to_perseus('ADJ', 'gen2|casB|grp3'))
# Returns 'a-s---fgs'

print(ittb_to_perseus('ADJ', 'gen1|casA|grn2'))
# Returns 'a-s---mnc'

print(ittb_to_perseus('NOUN', 'gen1|casA'))
# Returns 'n-s---mn-'
```

### LLCT to Perseus

LLCT uses a pipe-separated format that combines UPOS, XPOS, and FEATS information. The converter needs all three columns to generate standard XPOS:

```python
from nlp_utilities.converters.xpos import llct_to_perseus

# LLCT format: requires UPOS, XPOS (10-part pipe-separated), and FEATS
upos = 'VERB'
xpos = 'v|v|3|s|p|i|a|-|-|-'  # POS|POS_repeat|person|number|tense|mood|voice|gender|case|degree
feats = 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act'

new_xpos = llct_to_perseus(upos, xpos, feats)
print(new_xpos)  # "v3spia---"
```

## UPOS Converters

Convert language-specific POS tags to Universal POS tags.

### DALME to UPOS

Convert DALME project tags to Universal POS:

```python
from nlp_utilities.converters.upos import dalme_to_upos

dalme_tag = 'coordinating conjunction'
upos_tag = dalme_to_upos(dalme_tag)
print(upos_tag)  # 'CCONJ'
```

### UPOS to Perseus

Convert a UPOS tag to a Perseus XPOS tag:

```python
from nlp_utilities.converters.upos import upos_to_perseus

upos = "NOUN"
perseus_tag = upos_to_perseus(upos)
print(perseus_tag)  # 'n'
```

## Feature Converters

Convert morphological feature representations between formats.

### Feature Dictionary ↔ String

Convert between dictionary and CoNLL-U string format:

```python
from nlp_utilities.converters.features import feature_dict_to_string, feature_string_to_dict

# Dict to string
features = {
    'Case': 'Nom',
    'Gender': 'Masc',
    'Number': 'Sing'
}
feat_string = feature_dict_to_string(features)
print(feat_string)  # 'Case=Nom|Gender=Masc|Number=Sing'

# String to dict
feat_string = 'Case=Gen|Number=Plur'
features = feature_string_to_dict(feat_string)
print(features)  # {'Case': 'Gen', 'Number': 'Plur'}
```

**Automatic sorting**: Output is alphabetically sorted by feature name.

## See Also

- [Normalization](normalization.md) - Normalizing features and tags
- [Validation](validation.md) - Validating converted files
- {ref}`api_reference` - Detailed converter API
