"""Edge case tests for load_language_data."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from nlp_utilities.loaders import load_language_data


def test_none_type_raises_error() -> None:
    """Test that None as type raises appropriate error."""
    with pytest.raises(ValueError, match='Data type must be specified'):
        load_language_data(None, language=None)  # type: ignore[arg-type]


def test_additional_path_with_no_language() -> None:
    """Test loading additional data without language specified."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        additional_data = {
            'la': {
                'CustomFeature': {'type': 'custom'},
            },
        }
        json.dump(additional_data, f)
        temp_path = f.name

    try:
        data = load_language_data('feats', language=None, additional_path=temp_path)
        # Should merge into the features section
        assert 'features' in data
    finally:
        Path(temp_path).unlink()


def test_load_features_returns_dict() -> None:
    """Test that load_language_data always returns a dict."""
    result = load_language_data('feats', language='la')
    assert isinstance(result, dict)


def test_load_auxiliaries_returns_dict() -> None:
    """Test that load_language_data for auxiliaries returns a dict."""
    result = load_language_data('auxiliaries', language='en')
    assert isinstance(result, dict)


def test_case_sensitive_type() -> None:
    """Test that type parameter is case-sensitive."""
    with pytest.raises(ValueError, match='Unknown data type'):
        load_language_data('FEATS', language=None)


def test_case_sensitive_type_capitals() -> None:
    """Test that capitalized type raises error."""
    with pytest.raises(ValueError, match='Unknown data type'):
        load_language_data('Feats', language=None)


def test_additional_path_with_language() -> None:
    """Test that additional_path works with language specified."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        additional_data = {
            'CustomFeature': {'type': 'custom'},
        }
        json.dump(additional_data, f)
        temp_path = f.name

    try:
        data = load_language_data('feats', language='la', additional_path=temp_path)
        # Should merge into the features section
        assert 'CustomFeature' in data
    finally:
        Path(temp_path).unlink()


def test_dalme_with_language_not_latin() -> None:
    """Test that load_dalme doesn't work with non-Latin languages."""
    with pytest.raises(ValueError, match=r'DALME data can only be loaded for Latin \(la\) features'):
        load_language_data('feats', language='fr', load_dalme=True)
