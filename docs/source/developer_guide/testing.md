# Testing

This guide explains the testing strategy, organization, and practices for `latin-nlp-utilities`.

## Overview

The project uses a comprehensive testing strategy:

- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test module interactions
- **Fixture factories**: Factory Boy for test data generation

## Test Organization

### Directory Structure

```text
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── brat/                    # brat conversion tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── brat_to_conllu/
│   ├── conllu_to_brat/
│   ├── integration/
│   └── utils/
├── conllu/                  # Validation & evaluation tests
│   ├── conftest.py
│   ├── evaluators/
│   └── validators/
├── converters/              # Converter tests
│   ├── test_dalme_to_upos.py
│   ├── test_feature_dict_to_string.py
│   ├── test_ittb_converters.py
│   ├── test_proiel_converters.py
│   └── ...
├── loaders/                 # Loader tests
├── normalizers/             # Normalizer tests
├── factories/               # Test data factories
│   ├── __init__.py
│   └── conllu/
├── helpers/                 # Test utilities
│   └── conllu/
└── test_data/               # Test fixtures
    ├── gold.conllu
    ├── system.conllu
    ├── en_sentence.json
    └── brat/
```

**Naming Conventions**:

- Test files: `test_*.py`
- Test functions: `test_*`
- Fixtures: Descriptive names without `test_` prefix

## Running Tests

### Basic Test Execution

Run all tests:

```bash
pytest
```

Run specific test file:

```bash
pytest tests/converters/test_ittb_converters.py
```

Run specific test function:

```bash
pytest tests/converters/test_ittb_converters.py::test_ittb_to_perseus_verb
```

Run tests matching pattern:

```bash
pytest -k "test_brat"
```

### Verbose Output

```bash
# Show test names
pytest -v

# Show print statements
pytest -s

# Show detailed output
pytest -vv
```

### Coverage Reports

Run with coverage:

```bash
pytest --cov=nlp_utilities
```

Generate HTML report:

```bash
pytest --cov=nlp_utilities --cov-report=html
open htmlcov/index.html
```

Coverage by file:

```bash
pytest --cov=nlp_utilities --cov-report=term-missing
```

### Stop on First Failure

```bash
pytest -x
```

Show slowest tests:

```bash
pytest --durations=10
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from nlp_utilities.converters.xpos import ittb_to_perseus

def test_ittb_to_perseus_verb():
    """Test ITTB verb conversion to Perseus format."""
    # Arrange
    ittb_tag = "Vif3s3"

    # Act
    result = ittb_to_perseus(ittb_tag)

    # Assert
    assert result == "v3sfia---"
```

**AAA Pattern**: Arrange, Act, Assert

- **Arrange**: Set up test data and conditions
- **Act**: Execute the code being tested
- **Assert**: Verify the results

### Parametrized Tests

Test multiple cases efficiently:

```python
import pytest

@pytest.mark.parametrize("ittb_tag,expected", [
    ("Vif3s3", "v3sfia---"),
    ("Vip3s1", "v1spia---"),
    ("Vsp3p3", "v3ppsa---"),
])
def test_ittb_to_perseus_verbs(ittb_tag, expected):
    """Test multiple ITTB verb conversions."""
    assert ittb_to_perseus(ittb_tag) == expected
```

### Testing Exceptions

```python
import pytest

def test_invalid_tag_raises_error():
    """Test that invalid tag raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        ittb_to_perseus("INVALID")

    assert "unknown tag" in str(exc_info.value).lower()
```

### Testing File Operations

Use temporary directories:

```python
import pytest
from pathlib import Path

def test_file_conversion(tmp_path):
    """Test file conversion using temporary directory."""
    # Create test file
    input_file = tmp_path / "input.conllu"
    input_file.write_text("# Test sentence\n1\tword\t...\n")

    # Run conversion
    output_dir = tmp_path / "output"
    conllu_to_brat(str(input_file), str(output_dir))

    # Verify output
    assert (output_dir / "input-doc-001.txt").exists()
    assert (output_dir / "input-doc-001.ann").exists()
```

## Fixtures

### Using Built-in Fixtures

**tmp_path**: Temporary directory

```python
def test_with_temp_dir(tmp_path):
    """Test using temporary directory."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    assert test_file.read_text() == "content"
```

**monkeypatch**: Modify objects temporarily

```python
def test_with_monkeypatch(monkeypatch):
    """Test with environment variable."""
    monkeypatch.setenv("TEST_VAR", "value")
    # Test code using TEST_VAR
```

**capsys**: Capture stdout/stderr

```python
def test_print_output(capsys):
    """Test print statements."""
    print("test output")
    captured = capsys.readouterr()
    assert "test output" in captured.out
```

### Custom Fixtures

Define in `conftest.py`:

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_conllu_sentence():
    """Provide a sample CoNLL-U sentence."""
    return {
        'metadata': {'text': 'Sample sentence.'},
        'tokens': [
            {'id': '1', 'form': 'Sample', 'lemma': 'sample', ...},
            {'id': '2', 'form': 'sentence', 'lemma': 'sentence', ...},
        ]
    }

@pytest.fixture
def feature_set():
    """Provide Latin feature set."""
    from nlp_utilities.loaders import load_language_data
    return load_language_data('la')
```

Use fixtures:

```python
def test_with_fixture(sample_conllu_sentence):
    """Test using custom fixture."""
    assert len(sample_conllu_sentence['tokens']) == 2
```

### Fixture Scopes

```python
@pytest.fixture(scope="function")  # Default: new instance per test
def function_scope():
    return {}

@pytest.fixture(scope="module")    # One instance per module
def module_scope():
    return load_large_data()

@pytest.fixture(scope="session")   # One instance for entire test session
def session_scope():
    return setup_database()
```

### Factory Fixtures

Create fixtures that return factories:

```python
import pytest
from factory import Factory

@pytest.fixture
def sentence_factory():
    """Factory for creating test sentences."""
    class SentenceFactory(Factory):
        class Meta:
            model = dict

        id = 1
        form = "word"
        lemma = "word"
        upos = "NOUN"

    return SentenceFactory

def test_with_factory(sentence_factory):
    """Test using factory fixture."""
    sentence = sentence_factory(form="test")
    assert sentence['form'] == "test"
```

## Property-Based Testing

### Using Hypothesis

Hypothesis generates test cases automatically:

```python
from hypothesis import given, strategies as st

@given(
    case=st.sampled_from(['Nom', 'Gen', 'Acc', 'Dat', 'Abl']),
    number=st.sampled_from(['Sing', 'Plur']),
    gender=st.sampled_from(['Masc', 'Fem', 'Neut'])
)
def test_feature_normalization(case, number, gender):
    """Test feature normalization with generated values."""
    features = f"Case={case}|Number={number}|Gender={gender}"
    normalized = normalize_features(features)

    # Properties that should always hold
    assert 'Case=' in normalized
    assert 'Number=' in normalized
    assert 'Gender=' in normalized
    assert normalized == '|'.join(sorted(normalized.split('|')))
```

### Custom Strategies

```python
from hypothesis import strategies as st

# Strategy for CoNLL-U IDs
conllu_ids = st.integers(min_value=1, max_value=100).map(str)

# Strategy for UPOS tags
upos_tags = st.sampled_from([
    'NOUN', 'VERB', 'ADJ', 'ADV', 'PRON', 'DET',
    'ADP', 'CONJ', 'NUM', 'PART', 'INTJ', 'PUNCT'
])

@given(
    token_id=conllu_ids,
    upos=upos_tags
)
def test_token_validation(token_id, upos):
    """Test token validation with generated data."""
    token = {'id': token_id, 'upos': upos}
    # Test validation logic
```

## Integration Tests

### Testing Module Interactions

```python
def test_conversion_validation_integration(tmp_path):
    """Test full conversion and validation workflow."""
    # Create test input
    input_file = tmp_path / "input.conllu"
    input_file.write_text(SAMPLE_CONLLU)

    # Convert to brat
    brat_dir = tmp_path / "brat"
    conllu_to_brat(str(input_file), str(brat_dir))

    # Convert back
    output_dir = tmp_path / "output"
    feature_set = load_language_data('la')
    brat_to_conllu(
        str(brat_dir),
        str(output_dir),
        ref_conllu=str(input_file),
        feature_set=feature_set
    )

    # Validate result
    output_file = output_dir / "converted.conllu"
    validator = Validator(str(output_file))
    assert validator.validate()
```

### Round-Trip Testing

```python
def test_brat_conversion_roundtrip(tmp_path):
    """Test that CoNLL-U → brat → CoNLL-U preserves data."""
    original = load_conllu('test_data/gold.conllu')

    # Convert to brat
    brat_dir = tmp_path / "brat"
    conllu_to_brat('test_data/gold.conllu', str(brat_dir))

    # Convert back
    output_dir = tmp_path / "output"
    brat_to_conllu(
        str(brat_dir),
        str(output_dir),
        ref_conllu='test_data/gold.conllu',
        feature_set=load_language_data('la')
    )

    # Compare
    converted = load_conllu(str(output_dir / 'converted.conllu'))
    assert len(original) == len(converted)

    for orig_sent, conv_sent in zip(original, converted):
        assert orig_sent['metadata'] == conv_sent['metadata']
        # Compare tokens...
```

## Test Data Management

### Using Test Fixtures

Store test data in `tests/test_data/`:

```text
tests/test_data/
├── gold.conllu              # Gold standard file
├── system.conllu            # System output
├── en_sentence.json         # English sentence data
├── la_sentence.json         # Latin sentence data
├── evaluation_baseline.json # Baseline scores
├── brat/                    # brat test files
│   ├── test-doc-001.txt
│   ├── test-doc-001.ann
│   └── annotation.conf
└── load_data.py            # Utilities for loading
```

### Loading Test Data

```python
from pathlib import Path

TEST_DATA_DIR = Path(__file__).parent / 'test_data'

def load_test_conllu(filename):
    """Load test CoNLL-U file."""
    path = TEST_DATA_DIR / filename
    return load_conllu(str(path))

def test_with_test_data():
    """Test using stored test data."""
    gold = load_test_conllu('gold.conllu')
    system = load_test_conllu('system.conllu')

    evaluator = Evaluator(gold, system)
    results = evaluator.evaluate()

    assert results['LAS'] > 90.0
```

### Factory Boy

Generate test data programmatically:

```python
# tests/factories/conllu/sentence_factory.py
import factory

class TokenFactory(factory.Factory):
    class Meta:
        model = dict

    id = factory.Sequence(lambda n: str(n + 1))
    form = factory.Faker('word')
    lemma = factory.LazyAttribute(lambda o: o.form.lower())
    upos = factory.Iterator(['NOUN', 'VERB', 'ADJ'])
    xpos = '_'
    feats = 'Case=Nom|Number=Sing'
    head = '0'
    deprel = 'root'
    deps = '_'
    misc = '_'

class SentenceFactory(factory.Factory):
    class Meta:
        model = dict

    metadata = {'text': factory.Faker('sentence')}
    tokens = factory.List([
        factory.SubFactory(TokenFactory) for _ in range(5)
    ])
```

Use factories in tests:

```python
def test_with_factory():
    """Test using factory-generated data."""
    sentence = SentenceFactory()
    assert len(sentence['tokens']) == 5
    assert sentence['metadata']['text']
```

## Mocking

### Using pytest-mock

Mock external dependencies:

```python
def test_with_mock(mocker):
    """Test with mocked file operations."""
    mock_open = mocker.patch('builtins.open', mocker.mock_open(
        read_data='# Test\n1\tword\t...\n'
    ))

    result = load_conllu('test.conllu')

    mock_open.assert_called_once_with('test.conllu', 'r', encoding='utf-8')
    assert len(result) > 0
```

### Mocking Functions

```python
def test_mock_loader(mocker):
    """Test with mocked data loader."""
    mock_load = mocker.patch('nlp_utilities.loaders.load_language_data')
    mock_load.return_value = {
        'upos': ['NOUN', 'VERB'],
        'features': {'Case': ['Nom', 'Gen']}
    }

    result = normalize_features('Case=Nom', feature_set=mock_load())

    assert result == {'Case': 'Nom'}
```

## Testing Best Practices

### Test Naming

Use descriptive names:

```python
# Good
def test_ittb_verb_conversion_with_active_voice():
    pass

# Bad
def test_conversion():
    pass
```

**Pattern**: `test_<what>_<condition>_<expected_result>`

### Test Independence

Tests should not depend on each other:

```python
# Bad - tests depend on order
state = {}

def test_first():
    state['value'] = 1

def test_second():
    assert state['value'] == 1  # Depends on test_first

# Good - each test is independent
@pytest.fixture
def state():
    return {'value': 1}

def test_first(state):
    assert state['value'] == 1

def test_second(state):
    state['value'] = 2
    assert state['value'] == 2
```

### Test One Thing

Each test should verify one behavior:

```python
# Bad - tests multiple things
def test_converter():
    assert ittb_to_perseus("Vif3s3") == "v3sfia---"
    assert proiel_to_perseus("V-3PAI---3S---") == "v3spia---"
    assert validate_perseus("v3sfia---")

# Good - separate tests
def test_ittb_to_perseus_conversion():
    assert ittb_to_perseus("Vif3s3") == "v3sfia---"

def test_proiel_to_perseus_conversion():
    assert proiel_to_perseus("V-3PAI---3S---") == "v3spia---"

def test_perseus_validation():
    assert validate_perseus("v3sfia---")
```

### Clear Assertions

Use specific, informative assertions:

```python
# Bad
assert result

# Good
assert len(result) == 3, f"Expected 3 items, got {len(result)}"
assert result['upos'] == 'NOUN', f"Expected NOUN, got {result['upos']}"
```

### Use pytest.approx for Floats

```python
import pytest

def test_evaluation_score():
    """Test evaluation with float comparison."""
    score = calculate_las(gold, system)
    assert score == pytest.approx(95.5, abs=0.1)
```

## Continuous Integration

### GitHub Actions

Example workflow (.github/workflows/test.yml):

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          pytest --cov=nlp_utilities --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Test Coverage Goals

### Target Metrics

- **Overall coverage**: ≥90%
- **Critical modules**: ≥95%
  - brat conversions
  - validators
  - evaluators
- **Utility modules**: ≥85%

### Measuring Coverage

```bash
# Overall coverage
pytest --cov=nlp_utilities

# Coverage by module
pytest --cov=nlp_utilities.brat --cov-report=term-missing

# Find uncovered lines
pytest --cov=nlp_utilities --cov-report=html
open htmlcov/index.html
```

## Debugging Tests

### Using pdb

```python
def test_with_debugging():
    """Test with breakpoint for debugging."""
    result = complex_function()

    import pdb; pdb.set_trace()  # Breakpoint

    assert result == expected
```

### pytest –pdb

Automatically drop into debugger on failure:

```bash
pytest --pdb
```

### Print Debugging

```bash
# Show print statements
pytest -s

# Verbose output
pytest -vv
```

## See Also

- [Architecture](architecture.md) - Understanding the codebase structure
- **pytest documentation**: [https://docs.pytest.org/](https://docs.pytest.org/)
- **Hypothesis documentation**: [https://hypothesis.readthedocs.io/](https://hypothesis.readthedocs.io/)
