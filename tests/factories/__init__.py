"""Interface for the factories module."""

from __future__ import annotations

from .enhanced_deps import EnhancedDepsFactory
from .error_entry import ErrorEntryFactory
from .feature_set import FeatureSetFactory
from .sentence import ConlluSentenceFactory, build_conllu_sentence
from .tree_structure import TreeStructureFactory

__all__ = [
    'ConlluSentenceFactory',
    'EnhancedDepsFactory',
    'ErrorEntryFactory',
    'FeatureSetFactory',
    'TreeStructureFactory',
    'build_conllu_sentence',
]
