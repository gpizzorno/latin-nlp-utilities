IO Module
=========

The ``conllu_tools.io`` module provides utilities for converting between CoNLL-U and
brat standoff formats, as well as functions for loading language-specific data and
configurations.

Conversion Functions
--------------------

These functions convert between CoNLL-U and brat annotation formats, enabling
round-trip annotation workflows.

conllu_to_brat
~~~~~~~~~~~~~~

.. autofunction:: conllu_tools.io.conllu_to_brat

brat_to_conllu
~~~~~~~~~~~~~~

.. autofunction:: conllu_tools.io.brat_to_conllu

Data Loading Functions
----------------------

These functions load language-specific data files for validation and normalization.

load_language_data
~~~~~~~~~~~~~~~~~~

.. autofunction:: conllu_tools.io.load_language_data

load_whitespace_exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: conllu_tools.io.load_whitespace_exceptions

