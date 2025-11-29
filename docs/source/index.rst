.. CoNLL-U Tools documentation master file

CoNLL-U Tools Documentation
===========================

.. image:: https://img.shields.io/badge/License-MIT-green.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

.. image:: https://img.shields.io/badge/Language-Python-blue.svg
   :target: https://www.python.org
   :alt: Python

.. image:: https://github.com/gpizzorno/conllu_tools/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/gpizzorno/conllu_tools/actions/workflows/tests.yml
   :alt: Tests

**CoNLL-U Tools** is a Python toolkit for working with CoNLL-U files, Universal Dependencies treebanks, and annotated corpora. It provides utilities for format conversion, validation, evaluation, pattern matching, and morphological normalization, supporting workflows with `CoNLL-U`_ and `brat`_ standoff formats.

.. _CoNLL-U: https://universaldependencies.org/format.html
.. _brat: https://brat.nlplab.org

Features
--------

- **Format Conversion**: Bidirectional conversion between brat `standoff`_ and `CoNLL-U`_ formats
- **Validation**: Check CoNLL-U files for format compliance and annotation guideline adherence
- **Evaluation**: Score parser outputs against gold-standard files with comprehensive metrics
- **Pattern Matching**: Find tokens and sentences matching complex linguistic criteria
- **Morphological Utilities**: Normalize features, convert between tagsets (`Perseus`_, `ITTB`_, `PROIEL`_, `LLCT`_)
- **Extensible**: Add custom tagset converters and feature mappings

.. _standoff: https://brat.nlplab.org/standoff.html
.. _Perseus: https://universaldependencies.org/treebanks/la_perseus/index.html
.. _ITTB: https://universaldependencies.org/treebanks/la_ittb/index.html
.. _PROIEL: https://universaldependencies.org/treebanks/la_proiel/index.html
.. _LLCT: https://universaldependencies.org/treebanks/la_llct/index.html

Quick Links
-----------

- :ref:`installation`
- :ref:`quickstart`
- :ref:`user_guide`
- :ref:`examples`
- :ref:`api_reference`

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation.md
   quickstart.md
   user_guide/index
   examples/index
   api_reference/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
