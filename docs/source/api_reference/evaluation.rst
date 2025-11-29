Evaluation Module
=================

The ``conllu_tools.evaluation`` module provides tools for evaluating CoNLL-U format annotations,
including computing precision, recall, and F1 scores for various annotation layers.

The evaluation framework is based on the official CoNLL shared task evaluation scripts,
with support for all standard UD evaluation metrics.

Main Classes
------------

Evaluator
~~~~~~~~~

.. autoclass:: conllu_tools.evaluation.evaluator.ConlluEvaluator
   :members:
   :undoc-members:
   :show-inheritance:

Score
~~~~~

.. autoclass:: conllu_tools.evaluation.base.Score
   :members:
   :undoc-members:
   :show-inheritance:

Supporting Classes
------------------

These classes are used internally by the evaluator but may be useful for advanced use cases.

UDWord
~~~~~~

.. autoclass:: conllu_tools.evaluation.base.UDWord
   :members:
   :undoc-members:
   :show-inheritance:

UDSpan
~~~~~~

.. autoclass:: conllu_tools.evaluation.base.UDSpan
   :members:
   :undoc-members:
   :show-inheritance:

Alignment
~~~~~~~~~

.. autoclass:: conllu_tools.evaluation.base.Alignment
   :members:
   :undoc-members:
   :show-inheritance:

AlignmentWord
~~~~~~~~~~~~~

.. autoclass:: conllu_tools.evaluation.base.AlignmentWord
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
----------

.. autoexception:: conllu_tools.evaluation.base.UDError
   :show-inheritance:


