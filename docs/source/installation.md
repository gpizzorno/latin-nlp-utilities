(installation)=
# Installation

This guide covers installing `latin-nlp-utilities` for various use cases.

## Quick Install

Install the latest version using pip:

```bash
pip install latin-nlp-utilities
```

This installs the package and all required dependencies.

## Requirements

### System Requirements

- **Python**: 3.9 or higher
- **Operating System**: macOS, Linux, or Windows

## Other Installation Methods

### From Source

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

## Next Steps

After installation, see:

- [Quick Start Guide](quickstart.md) - Get started with common tasks
- {doc}`user_guide/index` - Comprehensive usage guides
- {doc}`api_reference/index` - Full API documentation
