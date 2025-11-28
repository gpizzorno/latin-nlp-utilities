"""Interface for conllu_tools module."""

from __future__ import annotations

import hashlib
from pathlib import Path

from .evaluation import ConlluEvaluator
from .validation import ConlluValidator


def get_md5(filepath: str | Path) -> str:
    """Calculate the MD5 hash of a file."""
    return hashlib.md5(open(filepath, 'rb').read()).hexdigest()


__all__ = [
    'ConlluEvaluator',
    'ConlluValidator',
    'get_md5',
]
