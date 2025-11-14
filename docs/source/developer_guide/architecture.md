# Architecture

This document explains the architecture and design patterns of the `latin-nlp-utilities` package.

## Overview

The package is organized into five main modules:

- **brat**: CoNLL-U ↔ brat standoff format conversion
- **conllu**: Validation and evaluation of CoNLL-U files
- **converters**: Tagset and feature format conversion
- **loaders**: Data loading utilities
- **normalizers**: Annotation normalization

## Package Structure

```text
nlp_utilities/
├── __init__.py
├── constants.py          # Package-wide constants
├── brat/                 # brat conversion module
│   ├── __init__.py
│   ├── brat_to_conllu.py
│   ├── conllu_to_brat.py
│   └── utils.py
├── conllu/              # Validation & evaluation
│   ├── evaluators/      # Evaluation metrics
│   │   ├── base.py
│   │   ├── evaluator.py
│   │   ├── helpers.py
│   │   ├── tree_validation.py
│   │   └── word_processing.py
│   └── validators/      # CoNLL-U validation
│       ├── validator.py
│       ├── format.py
│       ├── structure.py
│       ├── content_validators.py
│       └── ...
├── converters/          # Format conversion
│   ├── features.py      # Feature conversion
│   ├── upos.py          # UPOS conversion
│   └── xpos/            # XPOS converters
│       ├── ittb_converters.py
│       ├── proiel_converters.py
│       └── llct_converters.py
├── loaders.py           # Data loading utilities
├── normalizers.py       # Feature normalization
└── data/                # Reference data
    ├── feats.json
    ├── deprels.json
    ├── auxiliaries.json
    └── ...
```

## Module Design

### brat Module

**Purpose**: Convert between CoNLL-U and brat standoff formats.

**Key Components**:

1. **conllu_to_brat.py**
   - Reads CoNLL-U sentences
   - Generates `.txt` files (raw text)
   - Generates `.ann` files (standoff annotations)
   - Creates brat configuration files
2. **brat_to_conllu.py**
   - Reads brat standoff annotations
   - Maps back to CoNLL-U format
   - Retrieves morphology from reference file
   - Handles entity-to-token mapping
3. **utils.py**
   - Shared utility functions
   - ID concordance management
   - Entity relationship handling

**Design Pattern**: Stateless conversion functions

```python
def conllu_to_brat(
    conllu_filename: str,
    output_directory: str,
    output_root: bool = False,
    sents_per_doc: Optional[int] = None
) -> None:
    """Convert CoNLL-U to brat format."""
    # Read CoNLL-U
    # Split into documents
    # Generate .txt and .ann files
    # Create config files
```

**Key Design Elements**:

- **Stateless functions**: All conversion functions are pure functions
- **Reference file**: brat → CoNLL-U uses reference for morphology
- **ID concordance**: Maps between CoNLL-U IDs and brat entity IDs
- **ROOT handling**: Optional explicit ROOT entities for visualization

### CoNLL-U Module

**Purpose**: Validate and evaluate CoNLL-U files.

#### Validators Submodule

**Architecture**: Validator composition pattern

```text
ConlluValidator (Main class)
├── Format Validators
│   ├── format.py          # Line structure
│   ├── id_sequence.py     # Token ID validation
│   ├── metadata.py        # Metadata validation
│   └── unicode.py         # Character encoding
├── Content Validators
│   ├── content_validators.py  # UPOS, DEPREL, FEATS
│   ├── feature_format.py      # Feature syntax
│   └── enhanced_deps.py       # Enhanced dependencies
└── Structural Validators
    ├── structure.py           # Tree structure
    ├── structural_constraints.py
    └── tree_validation.py     # Cycles, connectivity
```

**Design Pattern**: Strategy pattern with validator composition

```python
class ConlluValidator:
    """Main validator that composes multiple validators."""

    def __init__(self, lang: str = None, level: int = 2):
        self.validators = [
            FormatValidator(),
            ContentValidator(),
            StructureValidator(),
        ]
        if lang:
            self.validators.append(LanguageValidator(lang))

    def validate(self) -> bool:
        """Run all validators."""
        for validator in self.validators:
            if not validator.validate():
                return False
        return True
```

**Validation Levels**:

1. **Format**: Basic CoNLL-U format compliance
2. **Content**: Valid tags and features
3. **Structure**: Tree properties (no cycles, single root)
4. **Language-specific**: Language-appropriate tagsets

#### Evaluators Submodule

**Architecture**: Mixin-based evaluation

```text
ConlluEvaluator (Main class)
├── WordProcessingMixin    # Token-level processing
└── TreeValidationMixin    # Tree structure validation
    ├── calculate_las()    # Labeled attachment
    ├── calculate_uas()    # Unlabeled attachment
    ├── calculate_upos()   # POS accuracy
    └── calculate_feats()  # Feature accuracy
```

**Design Pattern**: Mixin composition for metrics

```python
class ConlluEvaluator(WordProcessingMixin, TreeValidationMixin):
    """Evaluator combining multiple metric calculations."""

    def evaluate(self) -> dict:
        """Compute all metrics."""
        return {
            'LAS': self.calculate_las(),
            'UAS': self.calculate_uas(),
            'UPOS': self.calculate_upos(),
            'XPOS': self.calculate_xpos(),
            'FEATS': self.calculate_feats(),
        }
```

**Key Design Elements**:

- **Mixins**: Separate concerns (word processing vs tree validation)
- **Lazy evaluation**: Metrics computed on demand
- **Flexible comparison**: Support for partial credit, punctuation exclusion
- **Error reporting**: Detailed per-token error information

### Converters Module

**Purpose**: Convert between different annotation schemes.

**Architecture**: Function-based converters

```text
converters/
├── features.py          # Feature dict ↔ string
├── upos.py             # Language-specific → UPOS
└── xpos/               # XPOS converters
    ├── ittb_converters.py      # ITTB → Perseus
    ├── proiel_converters.py    # PROIEL → Perseus
    └── llct_converters.py      # LLCT → Perseus
```

**Design Pattern**: Simple function mapping

```python
def proiel_to_perseus(proiel_tag: str) -> str:
    """Convert PROIEL XPOS to Perseus format.

    Args:
        proiel_tag: PROIEL format tag (e.g., "V-3PAI---3S---")

    Returns:
        Perseus format tag (e.g., "v3spia---")
    """
    # Parse PROIEL tag
    # Map to Perseus positions
    # Return 9-character Perseus tag
```

**Converter Types**:

1. **UPOS Converters**: Language-specific POS → Universal POS
2. **XPOS Converters**: Between different positional tag schemes
3. **Feature Converters**: Dictionary ↔ CoNLL-U string format

**Key Design Elements**:

- **Pure functions**: Stateless, no side effects
- **Explicit mappings**: Clear lookup tables for transparency
- **Error handling**: Raise exceptions on unknown tags
- **Format validation**: Check input/output format correctness

### Loaders Module

**Purpose**: Load reference data and language-specific resources.

**Architecture**: Simple loader functions with caching

```python
def load_language_data(language: str) -> dict:
    """Load language-specific feature sets.

    Returns:
        dict with keys: 'upos', 'deprels', 'features'
    """
    # Load from data/ directory
    # Parse JSON files
    # Return structured data

def load_whitespace_exceptions(language: str) -> dict:
    """Load tokenization exceptions."""
    # Load language-specific exceptions
    # Return dict of special tokens
```

**Data Sources**:

- `data/feats.json`: Valid Universal Features
- `data/deprels.json`: Valid dependency relations
- `data/auxiliaries.json`: Auxiliary verb definitions
- `data/dalme_features.json`: DALME-specific mappings

**Key Design Elements**:

- **JSON format**: Human-readable, easy to edit
- **Package resources**: Data bundled with package
- **Lazy loading**: Load on demand, cache if needed
- **Validation**: Validate data structure on load

### Normalizers Module

**Purpose**: Normalize and standardize annotations.

**Architecture**: Transformation functions

```python
def normalize_features(
    upos: str,
    features: dict,
    feature_set: dict
) -> dict:
    """Normalize morphological features."""
    # Filter valid features for UPOS
    # Sort by feature name
    # Return cleaned dict

def normalize_xpos(
    xpos: str,
    upos: str,
    language: str = 'la'
) -> str:
    """Normalize XPOS tag to standard format."""
    # Check format validity
    # Apply language-specific rules
    # Return normalized tag
```

**Key Design Elements**:

- **Non-destructive**: Return new values, don’t modify input
- **Validation-aware**: Use feature sets for validation
- **Flexible**: Support partial normalization
- **Consistent**: Apply same rules across codebase

## Design Patterns

### Dependency Injection

Used in validators and evaluators:

```python
# Inject feature set for validation
validator = ConlluValidator(
    feature_set=load_language_data('la')
)

# Inject custom validators
validator.add_validator(CustomValidator())
```

### Strategy Pattern

Used for validation levels:

```python
class ConlluValidator:
    """Choose validation strategy based on level."""

    def __init__(self, level: int):
        if level == 1:
            self.strategy = BasicFormatValidation()
        elif level == 2:
            self.strategy = StructuralValidation()
        # ...
```

### Mixin Composition

Used in evaluators:

```python
class ConlluEvaluator(WordProcessingMixin, TreeValidationMixin):
    """Compose functionality from multiple mixins."""
    pass
```

### Function Composition

Used in converters:

```python
def full_conversion(text):
    """Compose multiple conversion steps."""
    text = normalize_features(text)
    text = proiel_to_perseus(text)
    text = validate_format(text)
    return text
```

## Data Flow

### Validation Pipeline

```{mermaid}
flowchart LR
    A[[Input File]]
    A ==> parse
    subgraph parse[Parse CoNLL-U]
        direction TB
        C(Format Validation)
        C --> D(Content Validation)
        D --> E(Struture Validation)
        E --> F(Language-specific Validation)
    end
    parse ==> G([Error Report])
```

### Evaluation Pipeline

```{mermaid}
flowchart LR
    A[[Gold File]]
    B[[System File]]
    A ==> sent
    B ==> sent
    subgraph sent[For each sentence]
        direction TB
        C(Compare Forms)
        C --> D(Compare Lemmata)
        D --> E(Compare Tags)
        E --> F(Compare Heads)
        F --> G(Compare Dependencies)
        G --> H(Compare Extended Deps)
    end
    sent ==> I(Aggregate Metrics)
    I ==> J([Score])
```

### Conversion Pipeline

```{mermaid}
flowchart TB
    A[[CoNLL-U File]]
    B(Parse Sentences)
    A ==> B
    B --> C(Extract Tokens)
    C --> D(Generate .txt)
    D --> E(Generate .ann)
    E --> F(Generate .conf)
    F --> G(Generate metadata.json)
    G ==> H([brat Files])
```

## Error Handling

### Error Hierarchy

```text
ValidationError (Base)
├── FormatError
│   ├── InvalidColumnCount
│   ├── InvalidIDFormat
│   └── InvalidMetadata
├── ContentError
│   ├── InvalidUPOS
│   ├── InvalidFeature
│   └── InvalidDeprel
└── StructuralError
    ├── CycleDetected
    ├── MultipleRoots
    └── DisconnectedGraph
```

### Error Reporting

Errors include:

- **Line number**: Where error occurred
- **Error type**: Category of error
- **Message**: Human-readable description
- **Severity**: CRITICAL, ERROR, WARNING
- **Suggestion**: How to fix (when applicable)

## Testing Architecture

See [Testing](testing.md) for detailed testing documentation.

## Extensibility

### Adding New Validators

```python
from nlp_utilities.conllu.validators import BaseValidator

class CustomValidator(BaseValidator):
    """Add custom validation logic."""

    def validate(self, sentence):
        # Your validation logic
        if not valid:
            self.add_error(line, message)
        return is_valid

# Register with main validator
validator.add_validator(CustomValidator())
```

### Adding New Converters

```python
def custom_to_perseus(custom_tag: str) -> str:
    """Convert custom tagset to Perseus."""
    # Conversion logic
    return perseus_tag

# Use in pipeline
from nlp_utilities.converters.xpos import register_converter
register_converter('custom', custom_to_perseus)
```

### Adding New Language Support

1. Create `data/lang_code_features.json`
2. Add language-specific validators
3. Register in language loader
4. Add tests for language-specific behavior

