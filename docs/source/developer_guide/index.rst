.. _developer_guide:

Developer Guide
===============

Information for contributors and developers.

.. toctree::
   :maxdepth: 2

   architecture
   testing


Development Setup
-----------------

1. Clone the repository
2. Install development dependencies: ``pip install -e ".[dev]"``
3. Run tests: ``pytest``
4. Check types: ``mypy nlp_utilities/``
5. Format code: Code is automatically formatted with ruff

Code Style
----------

This project uses:

- `ruff <https://github.com/astral-sh/ruff>`_ for linting and formatting
- Type hints for all public functions
