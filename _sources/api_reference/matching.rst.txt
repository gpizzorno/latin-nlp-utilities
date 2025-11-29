Matching Module
===============

The ``conllu_tools.matching`` module provides utilities for finding and matching complex
linguistic patterns in CoNLL-U data. It supports pattern-based searching across parsed
corpora using a flexible condition-based matching system.

**Key Features:**

- Token-level pattern matching with conditions on any CoNLL-U field
- Sentence-level pattern sequences for multi-token matching
- Support for negation, substring matching, and value alternatives
- Pattern building from simple string syntax

Quick Example
-------------

.. code-block:: python

   from conllu_tools.matching import build_pattern, find_in_corpus

   # Build a pattern to find adjective + noun sequences
   pattern = build_pattern("ADJ+NOUN", name="adj_noun")

   # Find all matches in a corpus
   matches = find_in_corpus(corpus, [pattern])

Utility Functions
-----------------

build_pattern
~~~~~~~~~~~~~

.. autofunction:: conllu_tools.matching.build_pattern

find_in_corpus
~~~~~~~~~~~~~~

.. autofunction:: conllu_tools.matching.find_in_corpus

Pattern Classes
---------------

SentencePattern
~~~~~~~~~~~~~~~

.. autoclass:: conllu_tools.matching.SentencePattern
   :members:
   :undoc-members:
   :show-inheritance:

TokenPattern
~~~~~~~~~~~~

.. autoclass:: conllu_tools.matching.TokenPattern
   :members:
   :undoc-members:
   :show-inheritance:

Condition
~~~~~~~~~

.. autoclass:: conllu_tools.matching.Condition
   :members:
   :undoc-members:
   :show-inheritance:

Result Classes
--------------

MatchResult
~~~~~~~~~~~

.. autoclass:: conllu_tools.matching.MatchResult
   :members:
   :undoc-members:
   :show-inheritance:
