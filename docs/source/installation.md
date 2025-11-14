(installation)=
# Installation

This guide covers installing `latin-nlp-utilities` for various use cases.

## Quick Install

Install the latest version using pip:

```bash
pip install latin-nlp-utilities
```

Or install from source:

```bash
git clone https://github.com/gpizzorno/latin-nlp-utilities.git
cd latin-nlp-utilities
pip install -e .
```

This installs the package and all required dependencies.

## Requirements

### System Requirements

- **Python**: 3.9 or higher
- **Operating System**: macOS, Linux, or Windows

### Python Dependencies

The package automatically installs these dependencies:

- [conllu](https://github.com/EmilStenstrom/conllu) - CoNLL-U file parsing
- [importlib_resources](https://github.com/python/importlib_resources) - Resource loading
- [regex](https://github.com/mrabarnett/mrab-regex) - Advanced pattern matching

These are installed automatically when you install `latin-nlp-utilities`.

## Development Installation

For contributors or those using the latest development version:

### Clone the Repository

```bash
git clone https://github.com/gpizzorno/latin-nlp-utilities.git
cd latin-nlp-utilities
```

### Create Virtual Environment

It’s recommended to use a virtual environment:

```bash
# Using venv (Python 3.9+)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or using conda
conda create -n latin-nlp python=3.11
conda activate latin-nlp
```

### Install in Development Mode

Install the package in editable mode:

```bash
pip install -e .
```

This creates an editable installation, so changes to the source code are immediately available.

### Install Development Dependencies

For testing and development:

```bash
pip install -e ".[dev]"
```

This installs additional tools:

- [pytest](https://github.com/pytest-dev/pytest), [pytest-cov](https://github.com/pytest-dev/pytest-cov), and [pytest-mock](https://github.com/pytest-dev/pytest-mock) - Testing framework and coverage
- [mypy](https://github.com/python/mypy) - Type checking
- [hypothesis](https://github.com/HypothesisWorks/hypothesis) and [factory_boy](https://github.com/FactoryBoy/factory_boy/) - Property-based testing

### Install Documentation Dependencies

To build the documentation locally:

```bash
pip install -e ".[docs]"
```

This installs:

- [sphinx](https://github.com/sphinx-doc/sphinx), [sphinx-rtd-theme](https://github.com/readthedocs/sphinx_rtd_theme), and [sphinx-autodoc-typehints](https://github.com/tox-dev/sphinx-autodoc-typehints) - Documentation generation
- [myst-parser](https://github.com/executablebooks/MyST-Parser) and [sphinx-markdown-builder](https://github.com/liran-funaro/sphinx-markdown-builder) - Markdown support for Sphinx

Then build the docs:

```bash
cd docs/
make html
open _build/html/index.html  # macOS
# or: xdg-open _build/html/index.html  # Linux
```

### Run Tests

Verify your development installation:

```bash
pytest
```

For coverage report:

```bash
pytest --cov=nlp_utilities --cov-report=html
```

## Installation Methods

### Using pip (Recommended for users)

```bash
pip install latin-nlp-utilities
```

### From Source (Recommended for developers)

Standard installation for users and developers:

```bash
git clone https://github.com/gpizzorno/latin-nlp-utilities.git
cd latin-nlp-utilities
pip install -e .
```

### From GitHub (Direct)

Install the latest development version without cloning:

```bash
pip install git+https://github.com/gpizzorno/latin-nlp-utilities.git
```

### Specific Version

Install a specific version from GitHub:

```bash
pip install git+https://github.com/gpizzorno/latin-nlp-utilities.git@v1.0.0
```

### Upgrade

Update to the latest version:

```bash
cd latin-nlp-utilities
git pull origin main
pip install -e . --upgrade
```

## Troubleshooting

### Import Error: No module named ‘nlp_utilities’

**Problem**: Python cannot find the installed package.

**Solutions**:

1. Verify installation:
   ```bash
   pip list | grep latin-nlp-utilities
   ```
2. Check that you’re using the correct Python environment:
   ```bash
   which python
   python -m site
   ```
3. Reinstall the package:
   ```bash
   pip uninstall latin-nlp-utilities
   pip install -e .
   ```

### Version Conflicts

**Problem**: Dependency version conflicts during installation.

**Solutions**:

1. Use a fresh virtual environment:
   ```bash
   python -m venv fresh_env
   source fresh_env/bin/activate
   pip install -e .
   ```
2. Update pip:
   ```bash
   pip install --upgrade pip setuptools wheel
   ```
3. Install with `--no-deps` and manually install dependencies:
   ```bash
   pip install --no-deps -e .
   pip install -r requirements.txt
   ```

### Permission Errors

**Problem**: Permission denied during installation.

**Solutions**:

1. Use virtual environment (recommended):
   ```bash
   python -m venv myenv
   source myenv/bin/activate
   pip install -e .
   ```
2. Use user installation:
   ```bash
   pip install --user -e .
   ```

### Tests Failing

**Problem**: Tests fail after development installation.

**Solutions**:

1. Ensure all dev dependencies are installed:
   ```bash
   pip install -e ".[dev]"
   ```
2. Clean and reinstall:
   ```bash
   pip uninstall latin-nlp-utilities
   pip install -e .
   ```
3. Check Python version:
   ```bash
   python --version  # Should be 3.9+
   ```

### UTF-8 Encoding Errors

**Problem**: Unicode errors when processing Latin text.

**Solutions**:

1. Ensure your system locale supports UTF-8:
   ```bash
   # Linux/macOS
   export LANG=en_US.UTF-8
   export LC_ALL=en_US.UTF-8
   ```
2. Specify encoding when opening files:
   ```python
   with open('file.conllu', 'r', encoding='utf-8') as f:
       content = f.read()
   ```

## Platform-Specific Notes

### Linux

Some distributions may need to install Python development headers:

```bash
# Debian/Ubuntu
sudo apt-get install python3-dev

# Fedora/RHEL
sudo dnf install python3-devel
```

### Windows

Use Command Prompt or PowerShell:

```powershell
pip install -e .
```

For virtual environments:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

## Next Steps

After installation, see:

- [Quick Start Guide](quickstart.md) - Get started with common tasks
- {doc}`user_guide/index` - Comprehensive usage guides
- {doc}`api_reference/index` - Full API documentation
