# Normalization Examples

Examples for normalizing morphological annotations in CoNLL-U files.

## Basic Normalization

The following examples assume you have loaded a feature set:

```python
from conllu_tools.io import load_language_data
from conllu_tools.utils import normalize_morphology

feature_set = load_language_data('feats', language='la')
```

### Example 1: VERB with Gerund Features

```python
xpos, feats = normalize_morphology(
    upos='VERB',
    xpos='v-s-ga-g-',
    feats='Aspect=Perf|Case=Gen|Degree=Pos|Number=Sing|Voice=Act',
    feature_set=feature_set,
    ref_features='Aspect=Perf|Case=Gen|Degree=Pos|Number=Sing|VerbForm=Ger|Voice=Act'
)

print(xpos)
# Output: 'v-stga-g-' (position 3 filled from features)

print(feats)
# Output: {'Aspect': 'Perf', 'Case': 'Gen', 'Degree': 'Pos', 'Number': 'Sing', 'VerbForm': 'Ger', 'Voice': 'Act'}
```

### Example 2: AUX with Finite Verb Features

```python
xpos, feats = normalize_morphology(
    upos='AUX',
    xpos='v2spia---',
    feats='Mood=Ind|Number=Sing|Person=2|Tense=Pres|VerbForm=Fin|Voice=Act',
    feature_set=feature_set
)

print(xpos)
# Output: 'v2spia---' (all positions validated)

print(feats)
# Output: {'Mood': 'Ind', 'Number': 'Sing', 'Person': 2', 'Tense': 'Pres', 'VerbForm': 'Fin', 'Voice': 'Act'}
```

### Example 3: ADJ with Degree Reconciliation

```python
xpos, feats = normalize_morphology(
    upos='ADJ',
    xpos='a-s---nbp',
    feats='Case=Abl|Degree=Pos|Gender=Neut|Number=Sing',
    feature_set=feature_set,
    ref_features='Case=Abl|Gender=Masc|Number=Sing'  # Gender conflicts - feats wins
)

print(xpos)
# Output: 'a-s---nbp' (validated)

print(feats)
# Output: {'Case': 'Abl', 'Degree': 'Pos', 'Gender': 'Neut', 'Number': 'Sing'}
# Note: Gender=Neut from feats takes precedence over Gender=Masc from ref_features
```

### Example 4: NOUN with XPOS/UPOS Mismatch Correction

```python
# XPOS suggests VERB, but UPOS is NOUN
xpos, feats = normalize_morphology(
    upos='NOUN',
    xpos='v2spma---',  # Wrong UPOS character
    feats='Mood=Imp|Number=Sing|Person=2|Tense=Pres|VerbForm=Fin|Voice=Act',
    feature_set=feature_set
)

print(xpos)
# Output: 'n-s------' (corrected to NOUN format, invalid features removed)

print(feats)
# Output: {'Number': 'Sing'} (only Number is valid for NOUN)
```


## Normalization Workflows

## Normalizing a CoNLL-U File

Process an entire CoNLL-U file to normalize all morphological annotations:

```python
from conllu_tools.io import load_language_data
from conllu_tools.utils import normalize_morphology, feature_dict_to_string

# Load feature set
feature_set = load_language_data('feats', language='la')

# Load CoNLL-U file (assuming you have a load function)
sentences = load_conllu('input.conllu')

# Normalize all annotations
for sentence in sentences:
    for token in sentence:
        # Skip multiword tokens and empty nodes
        if '-' in str(token['id']) or '.' in str(token['id']):
            continue
        
        # Normalize morphology
        if token['upos'] != '_' and token['xpos'] != '_':
            xpos, feats = normalize_morphology(
                upos=token['upos'],
                xpos=token['xpos'],
                feats=token['feats'] if token['feats'] != '_' else {},
                feature_set=feature_set
            )
            
            # Update token
            token['xpos'] = xpos
            token['feats'] = feature_dict_to_string(feats) if feats else '_'

```

## Cleaning Imported Annotations

Normalize annotations from external sources with ref_features:

```python
from conllu_tools.io import load_language_data
from conllu_tools.utils import normalize_morphology, feature_dict_to_string

feature_set = load_language_data('feats', language='la')

def clean_annotation(token, feature_set, ref_token=None):
    """Clean a single token's annotation."""
    if token['upos'] == '_':
        return token
    
    try:
        # Get reference features if available
        ref_features = None
        if ref_token and ref_token['feats'] != '_':
            ref_features = ref_token['feats']
        
        # Normalize
        xpos, feats = normalize_morphology(
            upos=token['upos'],
            xpos=token['xpos'] if token['xpos'] != '_' else f"{token['upos'][0].lower()}--------",
            feats=token['feats'] if token['feats'] != '_' else {},
            feature_set=feature_set,
            ref_features=ref_features
        )
        
        token['xpos'] = xpos
        token['feats'] = feature_dict_to_string(feats) if feats else '_'
        
    except Exception as e:
        print(f"Warning: Could not normalize token {token['form']}: {e}")
        token['xpos'] = f"{token['upos'][0].lower()}--------"
        token['feats'] = '_'
    
    return token

# Apply to all tokens with reference
for sentence, ref_sentence in zip(imported_sentences, reference_sentences):
    for token, ref_token in zip(sentence, ref_sentence):
        if isinstance(token['id'], int):
            clean_annotation(token, feature_set, ref_token)
```

## Validating After Normalization

Always validate after normalizing to ensure correctness:

```python
from conllu_tools.io import load_language_data
from conllu_tools.validation import ConlluValidator
from conllu_tools.utils import normalize_morphology

# Normalize
feature_set = load_language_data('feats', language='la')
# ... normalization code ...

# Validate
validator = ConlluValidator(lang='la', level=2)
reporter = validator.validate_file('output_normalized.conllu')

if reporter.get_error_count() > 0:
    print(f"Found {reporter.get_error_count()} errors after normalization")
    for error in reporter.format_errors():
        print(error)
else:
    print("All annotations normalized successfully!")
```

## Batch Normalization

Normalize multiple files in batch:

```python
from pathlib import Path
from conllu_tools.io import load_language_data
from conllu_tools.utils import normalize_morphology, feature_dict_to_string

def normalize_directory(input_dir, output_dir):
    """Normalize all CoNLL-U files in a directory."""
    feature_set = load_language_data('feats', language='la')
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for conllu_file in input_path.glob('*.conllu'):
        print(f"Processing {conllu_file.name}...")
        sentences = load_conllu(str(conllu_file))
        
        # Normalize each sentence
        for sentence in sentences:
            for token in sentence:
                if isinstance(token['id'], int) and token['upos'] != '_':
                    try:
                        xpos, feats = normalize_morphology(
                            upos=token['upos'],
                            xpos=token['xpos'] if token['xpos'] != '_' else f"{token['upos'][0].lower()}--------",
                            feats=token['feats'] if token['feats'] != '_' else {},
                            feature_set=feature_set
                        )
                        token['xpos'] = xpos
                        token['feats'] = feature_dict_to_string(feats) if feats else '_'
                    except Exception as e:
                        print(f"  Error in {token['form']}: {e}")
        
        # Save normalized file
        output_file = output_path / conllu_file.name
        save_conllu(sentences, str(output_file))
        print(f"Saved to {output_file}")

# Process all files
normalize_directory('raw_annotations/', 'normalized_annotations/')
```

## Error Handling

### Handling Normalization Errors

```python
from conllu_tools.utils import normalize_morphology, validate_features, validate_xpos

# Validation errors
try:
    result = validate_xpos(None, 'n-s---mn-')
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: UPOS must be provided to validate XPOS

try:
    result = validate_features(None, 'Case=Nom', feature_set)
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: UPOS and feature set must be provided to validate FEATS

# Format detection errors
try:
    xpos, feats = normalize_morphology('NOUN', None, {}, feature_set)
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: Both UPOS and FEATS must be provided to format XPOS
```

### Safe Normalization with Fallbacks

```python
from conllu_tools.utils import normalize_morphology, feature_dict_to_string

def safe_normalize_morphology(upos, xpos, feats, feature_set, ref_features=None):
    """Normalize morphology with fallback."""
    try:
        return normalize_morphology(upos, xpos, feats, feature_set, ref_features)
    except Exception as e:
        print(f"Warning: Could not normalize for UPOS '{upos}': {e}")
        # Return safe defaults
        default_xpos = f"{upos[0].lower()}--------" if upos else '---------'
        return default_xpos, {}

# Use safe version in production
for token in sentence:
    if token['upos'] != '_':
        xpos, feats = safe_normalize_morphology(
            token['upos'],
            token['xpos'],
            token['feats'],
            feature_set
        )
        token['xpos'] = xpos
        token['feats'] = feature_dict_to_string(feats) if feats else '_'
```

## See Also

- [Utilities User Guide](../user_guide/utils.md) for detailed documentation
