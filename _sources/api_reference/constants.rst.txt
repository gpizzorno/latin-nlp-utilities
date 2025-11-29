Constants Module
================

The ``conllu_tools.constants`` module provides reference data for Universal Dependencies
annotations, including valid tags, relations, features, and mappings between different
annotation schemes.

These constants are used internally by the validation and utility functions, but are
also available for direct use in custom processing pipelines.

Universal Dependencies Tags
---------------------------

UPOS Tags
~~~~~~~~~

.. py:data:: conllu_tools.constants.UPOS_TAGS
   :type: list[str]

   List of valid Universal Part-of-Speech tags.

   .. code-block:: python

      UPOS_TAGS = [
          'ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 'INTJ',
          'NOUN', 'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT',
          'SCONJ', 'SYM', 'VERB', 'X'
      ]

Universal Dependency Relations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:data:: conllu_tools.constants.UNIVERSAL_DEPRELS
   :type: set[str]

   Set of valid Universal Dependency relations.

   Includes: ``acl``, ``advcl``, ``advmod``, ``amod``, ``appos``, ``aux``,
   ``case``, ``cc``, ``ccomp``, ``clf``, ``compound``, ``conj``, ``cop``,
   ``csubj``, ``dep``, ``det``, ``discourse``, ``dislocated``, ``expl``,
   ``fixed``, ``flat``, ``goeswith``, ``iobj``, ``list``, ``mark``, ``nmod``,
   ``nsubj``, ``nummod``, ``obj``, ``obl``, ``orphan``, ``parataxis``,
   ``punct``, ``reparandum``, ``root``, ``vocative``, ``xcomp``

Universal Features
~~~~~~~~~~~~~~~~~~

.. py:data:: conllu_tools.constants.UNIVERSAL_FEATURES
   :type: set[str]

   Set of Universal Dependencies morphological feature names.

   Includes: ``Abbr``, ``Animacy``, ``Aspect``, ``Case``, ``Definite``,
   ``Degree``, ``Evident``, ``Foreign``, ``Gender``, ``Mood``, ``NumType``,
   ``Number``, ``Person``, ``Polarity``, ``Polite``, ``Poss``, ``PronType``,
   ``Reflex``, ``Tense``, ``VerbForm``, ``Voice``

Relation Categories
-------------------

.. py:data:: conllu_tools.constants.CONTENT_DEPRELS
   :type: set[str]

   Set of content (non-functional) dependency relations.

   Content relations attach content words that contribute semantic meaning.

.. py:data:: conllu_tools.constants.FUNCTIONAL_DEPRELS
   :type: set[str]

   Set of functional dependency relations.

   Functional relations attach function words (``aux``, ``cop``, ``mark``,
   ``det``, ``clf``, ``case``, ``cc``).

.. py:data:: conllu_tools.constants.LEFT_TO_RIGHT_RELATIONS
   :type: set[str]

   Relations that must always attach left-to-right in the sentence.

   Includes: ``conj``, ``fixed``, ``flat``, ``goeswith``, ``appos``

CoNLL-U Token Structure
-----------------------

.. py:data:: conllu_tools.constants.TOKEN_KEYS
   :type: dict[str, str]

   Mapping of CoNLL-U column names to their expected types.

   .. code-block:: python

      TOKEN_KEYS = {
          'id': 'int',
          'form': 'str',
          'lemma': 'str',
          'upos': 'str',
          'xpos': 'str',
          'feats': 'dict',
          'head': 'int',
          'deprel': 'str',
          'deps': 'list',
          'misc': 'dict',
      }

XPOS Mappings
-------------

These mappings are used for converting between morphological features and
Perseus-format XPOS tags.

.. py:data:: conllu_tools.constants.UPOS_TO_PERSEUS
   :type: dict[str, str]

   Mapping from UPOS tags to Perseus XPOS first-position codes.

   .. code-block:: python

      UPOS_TO_PERSEUS = {
          'ADJ': 'a', 'ADP': 'r', 'ADV': 'd', 'AUX': 'v',
          'CCONJ': 'c', 'DET': 'p', 'NOUN': 'n', 'NUM': 'm',
          'PART': 't', 'PRON': 'p', 'PROPN': 'n', 'PUNCT': 'u',
          'SCONJ': 'c', 'VERB': 'v', 'X': '-'
      }

.. py:data:: conllu_tools.constants.FEATS_TO_XPOS
   :type: dict[tuple[str, str], tuple[int, str]]

   Mapping from (feature, value) pairs to (position, character) in Perseus XPOS.

   See :doc:`/user_guide/utils` for the complete mapping table.

.. py:data:: conllu_tools.constants.XPOS_TO_FEATS
   :type: dict[tuple[int, str], tuple[str, str]]

   Inverse mapping from (position, character) to (feature, value).

   This is the inverse of ``FEATS_TO_XPOS``.

.. py:data:: conllu_tools.constants.VALIDITY_BY_POS
   :type: dict[int, str]

   Defines which XPOS positions are valid for which POS categories.

   Used by :func:`~conllu_tools.utils.xpos.validate.validate_xpos` to check
   position validity.

   .. code-block:: python

      VALIDITY_BY_POS = {
          2: 'v',       # Position 2 (person): only valid for verbs
          3: 'nvapm',   # Position 3 (number): nouns, verbs, adj, pron, num
          4: 'v',       # Position 4 (tense): only verbs
          5: 'v',       # Position 5 (mood/verbform): only verbs
          6: 'v',       # Position 6 (voice): only verbs
          7: 'nvapm',   # Position 7 (gender): nouns, verbs, adj, pron, num
          8: 'nvapm',   # Position 8 (case): nouns, verbs, adj, pron, num
          9: 'a',       # Position 9 (degree): only adjectives
      }

Treebank Concordances
---------------------

These dictionaries define mappings for converting XPOS formats from specific
Latin treebanks to the Perseus standard format.

.. py:data:: conllu_tools.constants.ITTB_CONCORDANCES
   :type: dict

   Mappings for Index Thomisticus Treebank XPOS conversion.

.. py:data:: conllu_tools.constants.PROIEL_CONCORDANCES
   :type: dict

   Mappings for PROIEL Treebank XPOS conversion.

.. py:data:: conllu_tools.constants.LLCT_CONCORDANCES
   :type: dict

   Mappings for Late Latin Charter Treebank XPOS conversion.

MISC Column
-----------

.. py:data:: conllu_tools.constants.MISC_ATTRIBUTES
   :type: set[str]

   Known/standard attributes for the MISC column.

   Includes: ``SpaceAfter``, ``Lang``, ``Translit``, ``LTranslit``,
   ``Gloss``, ``LId``, ``LDeriv``
