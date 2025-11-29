Validation Module
=================

The ``conllu_tools.validation`` module provides comprehensive validation tools for CoNLL-U
format files with configurable validation levels.

**Validation Levels:**

- **Level 1**: Basic format validation (Unicode, ID sequence, basic structure)
- **Level 2**: Universal guidelines (metadata, MISC column, feature format, enhanced deps)
- **Level 3**: Content validation (relation direction, functional leaves, projective punct)
- **Level 4**: Language-specific format validation
- **Level 5**: Language-specific content validation

Main Classes
------------

ConlluValidator
~~~~~~~~~~~~~~~

.. autoclass:: conllu_tools.validation.validator.ConlluValidator
   :members:
   :undoc-members:
   :show-inheritance:

ErrorReporter
~~~~~~~~~~~~~

.. autoclass:: conllu_tools.validation.error_reporter.ErrorReporter
   :members:
   :undoc-members:
   :show-inheritance:

ErrorEntry
~~~~~~~~~~

.. autoclass:: conllu_tools.validation.error_reporter.ErrorEntry
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
----------

.. autoexception:: conllu_tools.validation.error_reporter.ValidationError
   :show-inheritance:

Validation Mixins
-----------------

The validator is composed of multiple mixin classes, each handling a specific aspect of
validation. These are combined in ``ConlluValidator`` but can be referenced for understanding
the validation architecture.

.. note::

   These mixins are internal implementation details and are not part of the public API.
   They are documented here for advanced users who want to understand or extend the
   validation system.

**Format Validation Mixins:**

- ``FormatValidationMixin`` - Basic CoNLL-U format validation
- ``IdSequenceValidationMixin`` - Token ID sequence validation  
- ``UnicodeValidationMixin`` - Unicode normalization and character validation
- ``FeatureValidationMixin`` - FEATS column format validation

**Content Validation Mixins:**

- ``MetadataValidationMixin`` - Sentence metadata validation
- ``MiscValidationMixin`` - MISC column validation
- ``StructureValidationMixin`` - Dependency tree structure validation
- ``ContentValidationMixin`` - Content-level validation (relations, subjects, etc.)
- ``EnhancedDepsValidationMixin`` - Enhanced dependency validation
- ``CharacterValidationMixin`` - Character constraint validation

**Language-Specific Mixins:**

- ``LanguageFormatValidationMixin`` - Language-specific format rules
- ``LanguageContentValidationMixin`` - Language-specific content rules
