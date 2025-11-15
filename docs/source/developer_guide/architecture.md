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
   - Creates `metadata.json` file

2. **brat_to_conllu.py**
   - Reads brat standoff annotations
   - Reads context from `metadata.json` file
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

**Design Pattern**: Mixin composition for validation

```python
class ConlluValidator(
    FormatValidationMixin,
    IdSequenceValidationMixin,
    UnicodeValidationMixin,
    EnhancedDepsValidationMixin,
    MetadataValidationMixin,
    MiscValidationMixin,
    StructureValidationMixin,
    ContentValidationMixin,
    CharacterValidationMixin,
    LanguageFormatValidationMixin,
    LanguageContentValidationMixin,
    FeatureValidationMixin,
):
    """Main validator that composes multiple validation mixins."""

    def __init__(self, lang: str = 'ud', level: int = 2):
        self.lang = lang
        self.level = level
        self.reporter = ErrorReporter()
        # Load language-specific data if level >= 4

    def validate_file(self, filepath: str) -> ErrorReporter:
        """Validate a CoNLL-U file."""
        # Parse file
        # Run validation based on level
        # Return ErrorReporter with errors
```

**Validation Levels** (1-5):

1. **Level 1**: Format - Basic CoNLL-U format compliance (unicode, format, ID sequence, basic structure)
2. **Level 2**: Content - Valid tags and features (metadata, MISC, character constraints, feature format, enhanced deps)
3. **Level 3**: Extended - Tree properties (left-to-right relations, single subject, orphans, functional leaves)
4. **Level 4**: Language Format - Language-specific format requirements (feature sets, deprels, auxiliaries, whitespace)
5. **Level 5**: Language Content - Language-specific content validation

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

    def __init__(self, eval_deprels: bool = True, treebank_type: str = '0'):
        self.eval_deprels = eval_deprels
        self.treebank_type = self._parse_treebank_flags(treebank_type)

    def evaluate_files(self, gold_path: str, system_path: str) -> dict[str, Score]:
        """Compute all metrics."""
        # Parse files
        # Align words
        # Calculate metrics
        return {
            'Tokens': Score(...),
            'Sentences': Score(...),
            'Words': Score(...),
            'UPOS': Score(...),
            'XPOS': Score(...),
            'UFeats': Score(...),
            'AllTags': Score(...),
            'Lemmas': Score(...),
            'UAS': Score(...),
            'LAS': Score(...),
            'CLAS': Score(...),
            'MLAS': Score(...),
            'BLEX': Score(...),
            'ELAS': Score(...),
            'EULAS': Score(...),
        }
```

**Key Design Elements**:

- **Mixins**: Separate concerns (word processing vs tree validation)
- **Score objects**: Each metric returns a Score object with precision, recall, f1, and counts
- **Flexible comparison**: Support for different treebank types via configuration flags
- **Word alignment**: Character-based alignment for handling tokenization differences

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
def proiel_to_perseus(upos: str, xpos: str, feats: dict) -> str:
    """Convert PROIEL XPOS to Perseus format.

    Args:
        upos: Universal POS tag
        xpos: PROIEL format tag (e.g., "N")
        feats: Feature dictionary for reconciliation

    Returns:
        Perseus format tag (e.g., "v3spia---")
    """
    # Parse PROIEL tag
    # Map to Perseus positions
    # Reconcile with FEATS when needed
    # Return 9-character Perseus tag

def llct_to_perseus(upos: str, xpos: str, feats: dict) -> str:
    """Convert LLCT XPOS to Perseus format.

    Args:
        upos: Universal POS tag
        xpos: LLCT format tag (10-part pipe-separated)
        feats: Feature dictionary for reconciliation

    Returns:
        Perseus format tag (e.g., "n-s---mn-")
    """
    # Parse 10-part LLCT tag (drop 2nd part)
    # Map to Perseus 9-character positions
    # Reconcile XPOS and FEATS values (prefer XPOS)
    # Return normalized tag
```

**Converter Types**:

1. **UPOS Converters**: Language-specific POS → Universal POS
2. **XPOS Converters**: Between different positional tag schemes (require upos, xpos, feats for reconciliation)
3. **Feature Converters**: Dictionary ↔ CoNLL-U string format

**Key Design Elements**:

- **Pure functions**: Stateless, no side effects
- **Explicit mappings**: Clear lookup tables for transparency (CONCORDANCES dictionaries)
- **Reconciliation logic**: XPOS converters reconcile tag positions with FEATS values
- **Format validation**: Check input/output format correctness

### Loaders Module

**Purpose**: Load reference data and language-specific resources.

**Architecture**: Simple loader functions

```python
def load_language_data(
    _type: str,
    language: str | None = None,
    additional_path: str | None = None,
    load_dalme: bool = False
) -> dict:
    """Load language-specific resource data.

    Args:
        _type: Type of data to load ('feats', 'deprels', 'auxiliaries')
        language: Language code (if None, loads universal data)
        additional_path: Path to additional custom data
        load_dalme: Whether to load DALME-specific data

    Returns:
        dict with requested data structure
    """
    # Load from data/ directory
    # Parse JSON files
    # Merge with additional data if provided
    # Return structured data

def load_whitespace_exceptions(
    additional_path: str | None = None
) -> list:
    """Load tokenization whitespace exceptions.

    Returns:
        List of compiled regex patterns for tokens with spaces
    """
    # Load default exceptions
    # Add custom exceptions if path provided
    # Compile and return regex patterns
```

**Data Sources**:

- `data/feats.json`: Valid Universal Features
- `data/deprels.json`: Valid dependency relations
- `data/auxiliaries.json`: Auxiliary verb definitions
- `data/dalme_features.json`: DALME-specific mappings

**Key Design Elements**:

- **JSON format**: Human-readable, easy to edit
- **Package resources**: Data bundled with package (in `data/` directory)
- **Type-first loading**: Specify data type ('feats', 'deprels', 'auxiliaries') before language
- **Optional extensions**: Support for additional/custom data files
- **DALME support**: Optional loading of DALME-specific morphological data

### Normalizers Module

**Purpose**: Normalize and standardize annotations.

**Architecture**: Transformation functions

```python
def normalize_features(
    upos: str | None,
    features: str | dict,
    feature_set: dict | None
) -> dict | None:
    """Normalize morphological features.

    Args:
        upos: Universal POS tag for filtering valid features
        features: Feature string or dict to normalize
        feature_set: Feature set defining valid features by UPOS

    Returns:
        Normalized feature dictionary with only valid features
    """
    # Convert string to dict if needed
    # Filter features valid for UPOS
    # Capitalize feature names
    # Return cleaned dict

def normalize_xpos(upos: str, xpos: str) -> str:
    """Normalize XPOS tag to standard format.

    Args:
        upos: Universal POS tag
        xpos: Language-specific POS tag to normalize

    Returns:
        Normalized 9-character Perseus format tag
    """
    # Convert UPOS to Perseus type
    # Apply validity rules by position
    # Replace invalid positions with '-'
    # Ensure lowercase and correct length
    # Return normalized tag
```

**Key Design Elements**:

- **Non-destructive**: Return new values, don't modify input
- **Validation-aware**: Use feature sets for UPOS-based filtering
- **Type flexible**: normalize_features accepts string or dict input
- **Consistent**: Apply same rules across codebase (Perseus format, lowercase, proper length)

## Design Patterns

### Dependency Injection

Used in validators and evaluators:

```python
# Configure validator with language-specific data
validator = ConlluValidator(
    lang='la',
    level=4,
    add_features='custom_features.json',
    add_deprels='custom_deprels.json'
)

# Configure evaluator for specific treebank type
evaluator = ConlluEvaluator(
    eval_deprels=True,
    treebank_type='12'  # Disable enhancement types 1 and 2
)
```

### Level-Based Validation Strategy

Used for progressive validation:

```python
class ConlluValidator:
    """Choose validation checks based on level."""

    def _validate_sentence(self, sentence):
        # Level 1: Basic format, ID sequence, structure
        self._validate_unicode(sentence)
        self._validate_format(sentence)
        self._validate_id_sequence(sentence)
        self._validate_structure(sentence)

        if self.level < 2:
            return

        # Level 2: Metadata, MISC, features, enhanced deps
        self._validate_metadata(sentence)
        self._validate_misc(sentence)
        self._validate_feature_format(sentence)
        self._validate_enhanced_dependencies(sentence)

        if self.level < 3:
            return

        # Level 3: Content constraints
        self._validate_content(sentence)

        # ... levels 4 and 5
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
# Compose multiple conversion and normalization steps
from nlp_utilities.converters.xpos import llct_to_perseus
from nlp_utilities.normalizers import normalize_features, normalize_xpos
from nlp_utilities.loaders import load_language_data

feature_set = load_language_data('feats', language='la')

# Multi-step processing
perseus_xpos = llct_to_perseus(upos, llct_xpos, feats)
normalized_xpos = normalize_xpos(upos, perseus_xpos)
normalized_feats = normalize_features(upos, feats, feature_set)
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

### Error Reporting Structure

The validation system uses a structured error reporting mechanism:

```python
from dataclasses import dataclass

@dataclass
class ErrorEntry:
    """Represents a single validation error."""
    alt_id: str | None          # Alternative sentence ID
    testlevel: int              # Validation level (1-5)
    error_type: str             # Category of error
    testid: str                 # Test identifier
    msg: str                    # Error message
    node_id: str | None         # Node ID if applicable
    line_no: int | None         # Line number
    tree_counter: int | None    # Sentence counter

class ErrorReporter:
    """Manages error collection and reporting."""
    
    def warn(self, msg: str, error_type: str, testlevel: int = 0, 
             testid: str = 'some-test', line_no: int | None = None,
             node_id: str | None = None) -> None:
        """Record a validation error."""
        
    def format_errors(self) -> list[str]:
        """Format all errors as strings."""
        
    def get_error_count(self) -> int:
        """Get total number of errors."""
```

### Error Collection Pattern

Validators collect errors without raising exceptions:

```python
class ConlluValidator:
    def __init__(self, ...):
        self.reporter = ErrorReporter()
        
    def validate_file(self, filepath: str) -> ErrorReporter:
        """Validate and return error reporter."""
        # Validation collects errors in reporter
        # Never raises exceptions during validation
        return self.reporter
```

### Error Display

```python
validator = ConlluValidator(lang='la', level=3)
reporter = validator.validate_file('data.conllu')

if reporter.get_error_count() > 0:
    print(f"Found {reporter.get_error_count()} errors:")
    for error_msg in reporter.format_errors():
        print(error_msg)
```

## Testing Architecture

See [Testing](testing.md) for detailed testing documentation.

## Extensibility

### Adding Custom Validation Logic

The validation system uses mixins, so extend by creating new mixin classes:

```python
from nlp_utilities.conllu.validators.error_reporter import ErrorReporter

class CustomValidationMixin:
    """Add custom validation logic."""
    
    reporter: ErrorReporter  # Provided by ConlluValidator
    
    def validate_custom_rule(self, sentence):
        """Check custom validation rule."""
        for token in sentence:
            if not self._is_valid(token):
                self.reporter.warn(
                    msg=f"Custom validation failed for token {token['id']}",
                    error_type="Custom",
                    testlevel=3,
                    testid="custom-rule",
                    line_no=token.get('line_no')
                )

# Create custom validator by composing with mixins
from nlp_utilities.conllu.validators.validator import ConlluValidator

class ExtendedValidator(ConlluValidator, CustomValidationMixin):
    """Validator with custom logic."""
    
    def validate_file(self, filepath: str) -> ErrorReporter:
        """Add custom validation step."""
        reporter = super().validate_file(filepath)
        # Run additional custom validation
        return reporter
```

### Adding New Converters

Create new converter functions following the existing pattern:

```python
# For XPOS converters requiring reconciliation
def custom_to_perseus(upos: str, xpos: str, feats: dict) -> str:
    """Convert custom tagset to Perseus format.
    
    Args:
        upos: Universal POS tag
        xpos: Custom format tag
        feats: Feature dictionary for reconciliation
        
    Returns:
        9-character Perseus format tag
    """
    # Parse custom tag
    # Map positions to Perseus format
    # Reconcile with FEATS
    return perseus_tag

# For simple UPOS converters
def custom_to_upos(custom_pos: str) -> str:
    """Convert custom POS to Universal POS."""
    MAPPING = {
        'custom1': 'NOUN',
        'custom2': 'VERB',
        # ...
    }
    return MAPPING.get(custom_pos, '_')
```

### Adding New Language Support

1. **Create language-specific feature set** (`data/la_feats.json`):
```json
{
  "Case": ["Nom", "Gen", "Dat", "Acc", "Voc", "Abl", "Loc"],
  "Gender": ["Masc", "Fem", "Neut"]
}
```

2. **Create deprel mapping** (`data/la_deprels.json`):
```json
{
  "nsubj": "nominal subject",
  "obj": "object"
}
```

3. **Use in validation**:
```python
validator = ConlluValidator(
    lang='la',
    level=4,
    add_features='la_feats.json',
    add_deprels='la_deprels.json'
)
```

## See Also

- [Testing](testing.md) - Learn about testing strategy, organization, and practices
