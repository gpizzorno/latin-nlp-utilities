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

**CoNLL-U Tools** is a set of convenience tools for working with CoNLL-U files, UD treebanks, and annotated corpora. It provides converters, evaluation scripts, validation tools, and utilities for transforming, validating, and comparing linguistic data in `CoNLL-U`_ and `brat`_ standoff formats.

.. _CoNLL-U: https://universaldependencies.org/format.html
.. _brat: https://brat.nlplab.org

Features
--------

- **brat/CoNLL-U Interoperability**: Convert between brat `standoff`_ and `CoNLL-U`_
- **Morphological Feature Utilities**: Normalize and map features across tagsets (`Perseus`, `ITTB`, `PROIEL`, `DALME`)
- **Validation**: Check CoNLL-U files for format and annotation guideline compliance
- **Evaluation**: Score system outputs against gold-standard CoNLL-U files, including enhanced dependencies
- **Extensible**: Easily add new tagset converters or feature mappings

.. _standoff: https://brat.nlplab.org/standoff.html
.. _conllu: https://universaldependencies.org/format.html
.. _perseus: https://universaldependencies.org/treebanks/la_perseus/index.html
.. _ittb: https://universaldependencies.org/treebanks/la_ittb/index.html
.. _proiel: https://universaldependencies.org/treebanks/la_proiel/index.html
.. _dalme: https://dalme.org

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
