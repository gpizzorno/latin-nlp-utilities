# Architecture

This document explains the architecture and design patterns of the `latin-nlp-utilities` package.

## Overview

The package is organized into five main modules:

- **brat**: CoNLL-U ↔ brat standoff format conversion
- **conllu**: Validation and evaluation of CoNLL-U files
- **converters**: Tagset and feature format conversion
- **loaders**: Data loading utilities
- **normalizers**: Annotation normalization
- **validators**: Morphology validation

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
├── validators.py        # Morphology validation
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
4. **Format Converters**: Auto-detect and convert XPOS formats to Perseus
5. **Feature-to-XPOS Converters**: Generate XPOS from feature dictionaries

**Additional Converter Functions**:

```python
def format_xpos(upos: str, xpos: str | None, feats: dict[str, str] | str | None) -> str:
    """Convert XPOS to Perseus format with automatic format detection.

    Args:
        upos: Universal POS tag
        xpos: XPOS string in any format (LLCT, ITTB, PROIEL, Perseus, etc.)
        feats: Feature dictionary or string

    Returns:
        Perseus format XPOS (9 characters)

    Format detection (regex patterns):
        - PERSEUS_XPOS_MATCHER: [nvapmdcrileugt-]{9}
        - LLCT_XPOS_MATCHER: Pipe-separated 10-part format
        - ITTB_XPOS_MATCHER: e.g., 'gen4|tem1|mod1'
        - PROIEL_XPOS_MATCHER: Single/double character codes

    Workflow:
        1. Match xpos against known patterns
        2. Call appropriate converter (llct_to_perseus, ittb_to_perseus, etc.)
        3. If no match or None, return default: '{upos_code}--------'
        4. For Perseus format, ensure first char matches UPOS
    """
    if xpos is not None:
        if re.match(PERSEUS_XPOS_MATCHER, xpos):
            return f'{upos_to_perseus(upos)}{xpos[1:]}'
        if re.match(LLCT_XPOS_MATCHER, xpos):
            return llct_to_perseus(upos, xpos, feats)
        if re.match(ITTB_XPOS_MATCHER, xpos):
            return ittb_to_perseus(upos, xpos)
        if re.match(PROIEL_XPOS_MATCHER, xpos):
            return proiel_to_perseus(upos, feats)
    return f'{upos_to_perseus(upos)}--------'

def features_to_xpos(feats: dict[str, str] | str) -> str:
    """Convert features to XPOS in Perseus format.

    Args:
        feats: Feature string or dictionary

    Returns:
        9-character Perseus XPOS string

    Uses FEATS_TO_XPOS mapping:
        {('Case', 'Nom'): (8, 'n'), ('Case', 'Gen'): (8, 'g'), ...}
        Maps (feature, value) pairs to (position, character)

    Workflow:
        1. Initialize xpos as 9 dashes: '---------'
        2. For each feature-value pair in feats
        3. Look up corresponding (position, character) in FEATS_TO_XPOS
        4. Set xpos[position-1] = character
        5. Return assembled XPOS string
    """
    if isinstance(feats, str):
        feats = feature_string_to_dict(feats)
    
    xpos = ['-'] * 9
    for (feat, value), (position, char) in FEATS_TO_XPOS.items():
        if feats.get(feat) == value:
            xpos[position - 1] = char
    
    return ''.join(xpos)
```

**Key Design Elements**:

- **Pure functions**: Stateless, no side effects
- **Explicit mappings**: Clear lookup tables for transparency (CONCORDANCES dictionaries)
- **Reconciliation logic**: XPOS converters reconcile tag positions with FEATS values
- **Format validation**: Check input/output format correctness
- **Auto-detection**: format_xpos automatically detects input format
- **Bidirectional**: Can convert features→XPOS and XPOS→features

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

**Purpose**: Normalize and standardize morphological annotations.

**Architecture**: Composite transformation function

```python
def normalize_morphology(
    upos: str,
    xpos: str,
    feats: dict[str, str] | str,
    feature_set: dict[str, Any],
    ref_features: dict[str, str] | str | None = None,
) -> tuple[str, dict[str, str]]:
    """Normalize morphological information.

    Takes UPOS, XPOS, and FEATS, normalizes and validates them against
    a provided feature set, and reconciles with reference features if provided.

    Args:
        upos: Universal POS tag
        xpos: Language-specific POS tag (any format: LLCT, ITTB, PROIEL, Perseus)
        feats: Feature string or dictionary
        feature_set: Feature set dictionary defining valid features by UPOS
        ref_features: Reference features to reconcile with (optional)

    Returns:
        Tuple of (normalized_xpos, validated_features)

    Workflow:
        1. Format XPOS to Perseus standard (format_xpos)
        2. Validate XPOS against UPOS (validate_xpos)
        3. Convert feats to dictionary if needed
        4. Reconcile with ref_features (feats take precedence)
        5. Validate features against feature_set (validate_features)
        6. Generate XPOS from validated features (features_to_xpos)
        7. Validate generated XPOS (validate_xpos)
        8. Reconcile provided and generated XPOS (provided takes precedence)
    """
    # 1. Normalize XPOS format
    xpos = format_xpos(upos, xpos, feats)
    
    # 2. Validate XPOS against UPOS
    xpos = validate_xpos(upos, xpos)
    
    # 3. Ensure feats are a dict
    if isinstance(feats, str):
        feats = feature_string_to_dict(feats)
    
    # 4. Reconcile with reference features
    if ref_features is not None:
        if isinstance(ref_features, str):
            ref_features = feature_string_to_dict(ref_features)
        for key, value in ref_features.items():
            if key not in feats:
                feats[key] = value
    
    # 5. Validate features against feature set
    feats = validate_features(upos, feats, feature_set)
    
    # 6. Generate XPOS from features
    xpos_from_feats = features_to_xpos(feats)
    xpos_from_feats = validate_xpos(upos, xpos_from_feats)
    
    # 7. Reconcile XPOS values (provided takes precedence)
    for i in range(9):
        if xpos[i] == '-':
            xpos = xpos[:i] + xpos_from_feats[i] + xpos[i + 1:]
    
    return xpos, feats
```

**Key Design Elements**:

- **Comprehensive normalization**: Single function handles XPOS, FEATS, and their reconciliation
- **Format detection**: Automatically detects and converts LLCT, ITTB, PROIEL formats to Perseus
- **Bidirectional reconciliation**: Reconciles provided XPOS with generated XPOS, and feats with ref_features
- **Validation integration**: Uses validate_xpos and validate_features internally
- **Non-destructive**: Returns new values, doesn't modify input
- **Type flexible**: Accepts string or dict for feats and ref_features

### Validators Module

**Purpose**: Validate morphological annotations against feature sets and format rules.

**Architecture**: Validation functions

```python
def validate_features(
    upos: str,
    feats: dict[str, str] | str,
    feature_set: dict[str, Any]
) -> dict[str, str]:
    """Ensure features are valid for given UPOS based on feature set.

    Args:
        upos: Universal POS tag
        feats: Feature string or dictionary
        feature_set: Feature set dictionary defining valid features by UPOS

    Returns:
        Validated feature dictionary (invalid features removed)

    Validation steps:
        1. Convert feats string to dict if needed
        2. Normalize attribute names (case-insensitive matching)
        3. Normalize value names (case-insensitive matching)
        4. Check if feature is valid for the given UPOS
        5. Check if value is not marked as invalid (0) in feature set
        6. Return only valid features
    """
    # Convert to dict if string
    if isinstance(feats, str):
        feats = feature_string_to_dict(feats)
    
    validated_feats = {}
    for attr, value in feats.items():
        # Normalize and validate
        if attr_valid_for_upos(attr, value, upos, feature_set):
            validated_feats[norm_attr] = norm_value
    
    return validated_feats

def validate_xpos(upos: str, xpos: str | None) -> str:
    """Ensure XPOS is valid for given UPOS.

    Args:
        upos: Universal POS tag
        xpos: Language-specific POS tag (Perseus format)

    Returns:
        Validated 9-character Perseus XPOS string

    Validation steps:
        1. Set first character to match UPOS (Perseus mapping)
        2. Check each position against VALIDITY_BY_POS rules
        3. Replace invalid characters with '-'
        4. Ensure exactly 9 characters

    Position validity rules (Perseus format):
        - Position 1: UPOS-dependent (n, v, a, p, m, d, c, r, l, e, i, u, g, -)
        - Position 2: Only valid for 'v' (verbs)
        - Position 3: Valid for n, v, a, p, m
        - Position 4-6: Only valid for 'v' (verbs)
        - Position 7-8: Valid for n, v, a, p, m
        - Position 9: Only valid for 'a' (adjectives)
    """
    upos_code = upos_to_perseus(upos)
    
    if xpos is None or len(xpos) != 9:
        return f'{upos_code}--------'
    
    xpos_list = list(xpos)
    xpos_list[0] = upos_code  # Ensure first char matches UPOS
    
    # Validate each position
    for position, valid_pos in VALIDITY_BY_POS.items():
        char = xpos_list[position - 1]
        if char != '-' and upos_code not in valid_pos:
            xpos_list[position - 1] = '-'
    
    return ''.join(xpos_list)
```

**Key Design Elements**:

- **Feature filtering**: Removes features invalid for UPOS
- **Position validation**: Enforces Perseus XPOS format rules
- **Case normalization**: Handles case-insensitive feature matching
- **Used internally**: Called by normalize_morphology for validation
- **Standalone usage**: Can be used independently for validation-only tasks

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

Used in converters and normalizers:

```python
# Single-function normalization (recommended)
from nlp_utilities.normalizers import normalize_morphology
from nlp_utilities.loaders import load_language_data

feature_set = load_language_data('feats', language='la')

# Handles format detection, validation, and reconciliation
normalized_xpos, validated_feats = normalize_morphology(
    upos='VERB',
    xpos='v|v|3|s|p|i|a|-|-|-',  # LLCT format - auto-detected
    feats='Mood=Ind|Number=Sing|Person=3|Tense=Pres|Voice=Act',
    feature_set=feature_set
)

# Component-level composition (advanced)
from nlp_utilities.converters.xpos import format_xpos
from nlp_utilities.converters.features import features_to_xpos
from nlp_utilities.validators import validate_xpos, validate_features

# Step-by-step processing
xpos = format_xpos(upos, llct_xpos, feats)  # Convert to Perseus
xpos = validate_xpos(upos, xpos)  # Validate positions
feats = validate_features(upos, feats, feature_set)  # Filter invalid
xpos_from_feats = features_to_xpos(feats)  # Generate from features
xpos_from_feats = validate_xpos(upos, xpos_from_feats)  # Validate generated
# Reconcile provided and generated XPOS...
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
