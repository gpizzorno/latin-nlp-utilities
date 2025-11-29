Utils Module
============

The ``conllu_tools.utils`` module provides utilities for working with different tagsets
and formats, including morphology normalization, XPOS format conversion, and feature
validation.

**Key Capabilities:**

- Normalize morphological annotations across different treebank formats
- Convert between UPOS tags and Perseus XPOS codes
- Validate and convert features and XPOS strings
- Convert XPOS formats from LLCT, ITTB, and PROIEL treebanks to Perseus standard

Morphology Normalization
------------------------

The main entry point for normalizing morphological information.

.. autofunction:: conllu_tools.utils.normalization.normalize_morphology

UPOS Utilities
--------------

Convert between different POS tag systems.

.. automodule:: conllu_tools.utils.upos
   :members:
   :undoc-members:
   :show-inheritance:

Feature Utilities
-----------------

Convert and validate morphological features.

.. automodule:: conllu_tools.utils.features
   :members:
   :undoc-members:
   :show-inheritance:

XPOS Utilities
--------------

Convert and validate XPOS tags across different treebank formats.

Format XPOS
~~~~~~~~~~~

Auto-detect and convert XPOS formats to Perseus standard.

.. automodule:: conllu_tools.utils.xpos.format_xpos
   :members:
   :undoc-members:
   :show-inheritance:

Validate XPOS
~~~~~~~~~~~~~

Validate XPOS positions against UPOS-specific rules.

.. automodule:: conllu_tools.utils.xpos.validate
   :members:
   :undoc-members:
   :show-inheritance:

ITTB to Perseus
~~~~~~~~~~~~~~~

Convert Index Thomisticus Treebank XPOS to Perseus format.

.. automodule:: conllu_tools.utils.xpos.ittb_converters
   :members:
   :undoc-members:
   :show-inheritance:

PROIEL to Perseus
~~~~~~~~~~~~~~~~~

Convert PROIEL Treebank XPOS to Perseus format.

.. automodule:: conllu_tools.utils.xpos.proiel_converters
   :members:
   :undoc-members:
   :show-inheritance:

LLCT to Perseus
~~~~~~~~~~~~~~~

Convert Late Latin Charter Treebank XPOS to Perseus format.

.. automodule:: conllu_tools.utils.xpos.llct_converters
   :members:
   :undoc-members:
   :show-inheritance:

brat Utilities
--------------

Utilities for working with the brat standoff annotation format. These are used by the
conversion tools in the IO module but can also be used independently.

.. automodule:: conllu_tools.utils.brat
   :members:
   :undoc-members:
   :show-inheritance:
