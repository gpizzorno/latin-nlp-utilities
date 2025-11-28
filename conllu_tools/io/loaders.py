"""Utility functions for loading data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import IO, Any

import regex as re

from conllu_tools.constants import (
    DALME_FEATURES,
    DEFAULT_AUX,
    DEFAULT_DEPRELS,
    DEFAULT_FEATURES,
    DEFAULT_WHITESPACE_EXCEPTIONS,
)


def load_language_data(  # noqa: C901, PLR0912
    _type: str,
    language: str | None,
    additional_path: str | Path | None = None,
    load_dalme: bool = False,  # noqa: FBT001
) -> dict[str, Any]:
    """Load language data.

    Arguments:
        _type: Type of data to load ('features', 'auxiliaries', 'dependencies').
        language: A language code (e.g., 'la' for Latin), to filter for specific subsets.
        additional_path: Path to a JSON file containing additional data.
        load_dalme: Whether to load DALME-specific data.

    Returns:
        A dictionary containing the loaded data.

    """
    if not _type:
        msg = 'Data type must be specified'
        raise ValueError(msg)

    defaults = {
        'feats': DEFAULT_FEATURES,
        'auxiliaries': DEFAULT_AUX,
        'deprels': DEFAULT_DEPRELS,
    }

    if _type not in defaults:
        msg = f'Unknown data type: {_type}. Valid types are: {list(defaults.keys())}'
        raise ValueError(msg)

    default_target = defaults[_type]
    section_key = _type if _type != 'feats' else 'features'

    with default_target.open('r', encoding='utf-8') as file:
        data: dict[str, Any] = json.load(file)

    if language is not None:
        data = data[section_key][language]

    if additional_path:
        additional_path = Path(additional_path) if isinstance(additional_path, str) else additional_path
        # check if the additional data file exists
        if not additional_path.exists():
            msg = f'Additional data file not found: {additional_path}'
            raise FileNotFoundError(msg)

        with additional_path.open('r', encoding='utf-8') as file:
            xtra_data = json.load(file)
            for name, values in xtra_data.items():
                if language is not None:
                    data[name] = values
                else:
                    data[section_key][name] = values

    if load_dalme:
        if _type != 'feats':
            msg = 'DALME data can only be loaded for features'
            raise ValueError(msg)

        if language is not None and language != 'la':
            msg = 'DALME data can only be loaded for Latin (la) features'
            raise ValueError(msg)

        with DALME_FEATURES.open('r', encoding='utf-8') as file:
            xtra_features = json.load(file)
            for name, values in xtra_features.items():
                if language is not None:
                    data[name] = values
                else:
                    data[section_key]['la'][name] = values

    return data


def load_whitespace_exceptions(additional_exceptions_path: str | Path | None = None) -> list[re.Pattern]:
    """Load whitespace exceptions.

    The format consists of regular expressions (one per line) that match tokens
    allowed to contain whitespace. These are compiled and stored for validation.

    Arguments:
        additional_exceptions_path: Optional path to a file containing additional whitespace exceptions.

    Returns:
        A list of compiled regex patterns representing whitespace exceptions.

    """
    patterns: list[re.Pattern] = DEFAULT_WHITESPACE_EXCEPTIONS.copy()

    def _process_file(data: IO[str], patterns_list: list[re.Pattern]) -> None:
        for raw_line in data:
            line = raw_line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            # Compile the regex pattern
            try:
                compiled_pattern = re.compile(line, re.UNICODE)
                patterns_list.append(compiled_pattern)
            except re.error:
                # Skip invalid regex patterns
                continue

    if additional_exceptions_path:
        additional_exceptions_path = (
            Path(additional_exceptions_path)
            if isinstance(additional_exceptions_path, str)
            else additional_exceptions_path
        )
        # check if the additional exceptions file exists
        if not additional_exceptions_path.exists():
            msg = f'Additional exceptions file not found: {additional_exceptions_path}'
            raise FileNotFoundError(msg)

        with additional_exceptions_path.open('r', encoding='utf-8') as file:
            _process_file(file, patterns)

    return patterns
