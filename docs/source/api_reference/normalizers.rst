Normalizers Module
==================

The ``nlp_utilities.normalizers`` module provides utilities for normalizing morphological features and part-of-speech tags.

Functions
---------

.. automodule:: nlp_utilities.normalizers
   :members:
   :undoc-members:
   :show-inheritance:

Feature Normalization
~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: nlp_utilities.normalizers.normalize_features
   :noindex:

   Normalize morphological features based on the UPOS tag and a feature set definition.
   This ensures that only valid features for a given part of speech are retained.

XPOS Normalization
~~~~~~~~~~~~~~~~~~

.. autofunction:: nlp_utilities.normalizers.normalize_xpos
   :noindex:

   Normalize language-specific POS tags (XPOS) to Perseus format based on the UPOS tag.
   This ensures consistent 9-character positional tags.

